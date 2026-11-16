"""Bilim Kaliti — sinf o'yinlari uchun Telegram bot.

Bot o'yinlarni Telegram ichida (Mini App) ochadi va o'yin boshlanganda
javob kodlarini o'qituvchiga yuboradi.
"""
import hashlib
import hmac
import json
import logging
import os
import time
from pathlib import Path
from urllib.parse import parse_qsl

from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    WebAppInfo,
)
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bilim-kaliti")

TOKEN = os.environ["BOT_TOKEN"].strip()
# Render bu manzilni o'zi beradi. Boshqa joyda ishga tushirilsa, BASE_URL qo'yiladi.
BASE_URL = (os.environ.get("BASE_URL") or os.environ.get("RENDER_EXTERNAL_URL") or "").rstrip("/")
PORT = int(os.environ.get("PORT", "10000"))
WEBHOOK_PATH = "/webhook/" + hashlib.sha256(TOKEN.encode()).hexdigest()[:32]
GAMES_DIR = Path(__file__).parent / "games"

# (fayl, ?g= parametri, tugma nomi, qisqa tavsif)
GAMES = [
    ("sirli-xonalar", "", "🗝️ Sirli xonalar", "qulflangan xonalardan chiqish"),
    ("kosmik-baza", "", "🛸 Kosmik baza", "har bir guruh oʻz eshiklarini ochadi"),
    ("eshik-kodi", "", "🏰 Eshik kodi", "5 ta eshikli qasr"),
    ("toplam", "minora", "🏗️ Minora qurish", "toʻgʻri javob — yangi qavat"),
    ("toplam", "xazina", "🗺️ Xazina xaritasi", "orolma-orol xazinaga"),
    ("toplam", "raketa", "🚀 Raketa poygasi", "qiyinlikni oʻzing tanla"),
    ("toplam", "mozaika", "🧩 Rasm ochish", "yashirin rasmni top"),
    ("toplam", "bomba", "💣 Bomba", "toʻgʻri simni kes"),
    ("toplam", "tez", "⚡ Kim tezroq", "dars boshidagi isinish"),
    ("toplam", "nishon", "🎯 Nishon", "navbat bilan oʻq otish"),
    ("toplam", "zanjir", "🔗 Son zanjiri", "ketma-ket amallar"),
]

BTN_GAMES = "🎮 Oʻyinlar"
BTN_KEY = "🔑 Javoblar"
BTN_HELP = "ℹ️ Yordam"

bot = Bot(TOKEN)
dp = Dispatcher()

# Har bir o'qituvchining hozirgi o'yindagi javoblari (server qayta ishga tushsa, tozalanadi).
KEYS: dict[int, tuple[str, float]] = {}


def menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_GAMES), KeyboardButton(text=BTN_KEY)], [KeyboardButton(text=BTN_HELP)]],
        resize_keyboard=True,
    )


def game_version(slug: str) -> str:
    """Fayl o'zgarganda yangi raqam beradi: Telegram eski nusxani ko'rsatmaydi."""
    try:
        return str(int((GAMES_DIR / f"{slug}.html").stat().st_mtime))
    except OSError:
        return "0"


def game_url(slug: str, g: str) -> str:
    url = f"{BASE_URL}/games/{slug}.html?v={game_version(slug)}"
    return url + (f"&g={g}" if g else "")


def games_kb() -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(text=title, web_app=WebAppInfo(url=game_url(slug, g))) for slug, g, title, _ in GAMES]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def games_text() -> str:
    lines = ["Oʻyinni tanlang. U Telegram ichida ochiladi:\n"]
    lines += [f"{title} — {desc}" for _, _, title, desc in GAMES]
    lines.append("\nOʻyin boshlanganda javob kodlari shu chatga keladi.")
    return "\n".join(lines)


HELP_TEXT = (
    "Qanday foydalaniladi:\n\n"
    "1. Kompyuterda Telegram Desktop’da shu botni oching va elektron doskaga ulang.\n"
    "2. «🎮 Oʻyinlar» tugmasini bosib, oʻyinni tanlang. Oʻyin oynasini kattalashtiring.\n"
    "3. Sozlamalarni tanlab, oʻyinni boshlang.\n"
    "4. Javob kodlari shu chatga keladi. Telefoningizda koʻrib turing, doskada ochish shart emas.\n"
    "5. Oʻyin davomida hozirgi kodlarni bilish uchun «🔑 Javoblar» tugmasini bosing."
)


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Assalomu alaykum! Men «Bilim Kaliti» botiman 🔑\n"
        "Darsda guruhlar bilan oʻynaladigan matematik oʻyinlarni ochib beraman.",
        reply_markup=menu_kb(),
    )
    await message.answer(games_text(), reply_markup=games_kb())


@dp.message(F.text == BTN_GAMES)
@dp.message(Command("oyinlar"))
async def show_games(message: Message) -> None:
    await message.answer(games_text(), reply_markup=games_kb())


@dp.message(F.text == BTN_KEY)
@dp.message(Command("kalit"))
async def show_key(message: Message) -> None:
    item = KEYS.get(message.from_user.id)
    if not item:
        await message.answer("Hozircha javoblar yoʻq. Avval oʻyinni boshlang.")
        return
    await message.answer(item[0])


@dp.message(F.text == BTN_HELP)
@dp.message(Command("yordam"))
async def show_help(message: Message) -> None:
    await message.answer(HELP_TEXT)


def check_init_data(init_data: str) -> dict | None:
    """Mini App'dan kelgan ma'lumot haqiqatan Telegram'dan ekanini tekshiradi."""
    try:
        pairs = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        return None
    received = pairs.pop("hash", None)
    if not received:
        return None
    check_string = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    secret = hmac.new(b"WebAppData", TOKEN.encode(), hashlib.sha256).digest()
    calc = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calc, received):
        return None
    if time.time() - int(pairs.get("auth_date", "0")) > 86400:
        return None
    try:
        return json.loads(pairs.get("user", "{}"))
    except json.JSONDecodeError:
        return None


async def api_key(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"ok": False}, status=400)
    user = check_init_data(str(data.get("initData", "")))
    if not user or "id" not in user:
        return web.json_response({"ok": False}, status=403)
    text = str(data.get("text", ""))[:3500]
    KEYS[user["id"]] = (text, time.time())
    if data.get("notify"):
        try:
            await bot.send_message(user["id"], text)
        except Exception as e:  # foydalanuvchi botni bloklagan bo'lishi mumkin
            log.warning("send failed: %s", e)
    return web.json_response({"ok": True})


async def index(request: web.Request) -> web.Response:
    return web.Response(text="Bilim Kaliti bot ishlayapti.")


async def on_startup(app: web.Application) -> None:
    if not BASE_URL:
        log.error("BASE_URL topilmadi: webhook oʻrnatilmadi.")
        return
    await bot.set_webhook(BASE_URL + WEBHOOK_PATH, drop_pending_updates=True)
    log.info("Webhook oʻrnatildi: %s", BASE_URL)


@web.middleware
async def no_cache(request: web.Request, handler):
    response = await handler(request)
    if request.path.startswith("/games/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


def main() -> None:
    app = web.Application(middlewares=[no_cache])
    app.router.add_get("/", index)
    app.router.add_post("/api/key", api_key)
    app.router.add_static("/games/", GAMES_DIR)
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    app.on_startup.append(on_startup)
    web.run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
