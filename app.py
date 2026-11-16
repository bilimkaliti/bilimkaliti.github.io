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
    CallbackQuery,
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

# Sinflar va mavzular (build vaqtida games/grades.json ga yoziladi)
GRADES: dict[str, list[dict]] = json.loads((GAMES_DIR / "grades.json").read_text(encoding="utf-8"))
TOPIC_NAMES = {t["i"]: t["n"] for lst in GRADES.values() for t in lst}
GRADE_GAMES = [g for g in GAMES if g[0] == "toplam"]
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0") or 0)

BTN_CLASSES = "📚 Sinflar"
BTN_GAMES = "🎮 Barcha oʻyinlar"
BTN_GAMES_OLD = "🎮 Oʻyinlar"
BTN_KEY = "🔑 Javoblar"
BTN_HELP = "ℹ️ Yordam"
BTN_FEEDBACK = "💬 Savol va takliflar"
BTN_HOME = "🏠 Bosh menyu"
BTN_BACK = "⬅️ Sinflar"
BTN_OTHER = "🔜 Boshqa fanlar"
MATH = "🧮 Matematika"

bot = Bot(TOKEN)
dp = Dispatcher()

# Har bir o'qituvchining hozirgi o'yindagi javoblari (server qayta ishga tushsa, tozalanadi).
KEYS: dict[int, tuple[str, float]] = {}
WAIT_FEEDBACK: set[int] = set()


def kb(rows: list[list[str]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t) for t in r] for r in rows], resize_keyboard=True)


def menu_kb() -> ReplyKeyboardMarkup:
    return kb([[BTN_CLASSES], [BTN_GAMES, BTN_KEY], [BTN_FEEDBACK, BTN_HELP]])


def classes_kb() -> ReplyKeyboardMarkup:
    return kb([["7-sinf", "6-sinf"], ["5-sinf", "4-sinf"], ["3-sinf", "2-sinf"], ["1-sinf"], [BTN_HOME]])


def subjects_kb(g: str) -> ReplyKeyboardMarkup:
    return kb([[f"{MATH} {g}"], [BTN_OTHER], [BTN_BACK, BTN_HOME]])


def game_version(slug: str) -> str:
    """Fayl o'zgarganda yangi raqam beradi: Telegram eski nusxani ko'rsatmaydi."""
    try:
        return str(int((GAMES_DIR / f"{slug}.html").stat().st_mtime))
    except OSError:
        return "0"


def game_url(slug: str, g: str, extra: str = "") -> str:
    url = f"{BASE_URL}/games/{slug}.html?v={game_version(slug)}"
    return url + (f"&g={g}" if g else "") + extra


def games_kb() -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(text=title, web_app=WebAppInfo(url=game_url(slug, g))) for slug, g, title, _ in GAMES]
    return InlineKeyboardMarkup(inline_keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)])


def games_text() -> str:
    lines = ["Oʻyinni tanlang. U Telegram ichida ochiladi:\n"]
    lines += [f"{title} — {desc}" for _, _, title, desc in GAMES]
    lines.append("\nOʻyin boshlanganda javob kodlari shu chatga keladi.")
    return "\n".join(lines)


def topics_kb(g: str) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text="🎲 Barcha mavzular aralash", callback_data=f"tp:{g}:all")]]
    rows += [[InlineKeyboardButton(text=t["n"], callback_data=f"tp:{g}:{t['i']}")] for t in GRADES.get(g, [])]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def topic_games_kb(g: str, t: str) -> InlineKeyboardMarkup:
    extra = f"&sinf={g}&t={t}"
    buttons = [InlineKeyboardButton(text=title, web_app=WebAppInfo(url=game_url(slug, gk, extra))) for slug, gk, title, _ in GRADE_GAMES]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    rows.append([InlineKeyboardButton(text="⬅️ Mavzular", callback_data=f"sb:{g}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


HELP_TEXT = (
    "Qanday foydalaniladi:\n\n"
    "1. Kompyuterda Telegram Desktop’da shu botni oching va elektron doskaga ulang.\n"
    "2. «📚 Sinflar» → sinf → «🧮 Matematika» → mavzu → oʻyin.\n"
    "   Yoki «🎮 Barcha oʻyinlar» orqali istalgan oʻyinni oching.\n"
    "3. Sozlamalarni tanlab, oʻyinni boshlang. Oʻyin oynasi oʻzi toʻliq ekranga oʻtadi.\n"
    "4. Javob kodlari shu chatga keladi — telefoningizda koʻrib turing.\n"
    "5. Oʻyin davomida hozirgi javoblar uchun «🔑 Javoblar» tugmasini bosing."
)


@dp.message(CommandStart())
async def start(message: Message) -> None:
    WAIT_FEEDBACK.discard(message.from_user.id)
    await message.answer(
        "Assalomu alaykum! Men «Bilim Kaliti» botiman 🔑\n"
        "Darsda guruhlar bilan oʻynaladigan oʻyinlarni ochib beraman.\n\n"
        "Boshlash uchun «📚 Sinflar» tugmasini bosing.",
        reply_markup=menu_kb(),
    )


@dp.message(F.text == BTN_HOME)
async def home(message: Message) -> None:
    WAIT_FEEDBACK.discard(message.from_user.id)
    await message.answer("Bosh menyu", reply_markup=menu_kb())


@dp.message(F.text.in_({BTN_CLASSES, BTN_BACK}))
async def show_classes(message: Message) -> None:
    WAIT_FEEDBACK.discard(message.from_user.id)
    await message.answer("Sinfni tanlang:", reply_markup=classes_kb())


@dp.message(F.text.regexp(r"^([1-7])-sinf$").as_("m"))
async def show_subjects(message: Message, m) -> None:
    g = m.group(1)
    await message.answer(f"{g}-sinf. Fanni tanlang:", reply_markup=subjects_kb(g))


@dp.message(F.text.regexp(r"^🧮 Matematika ([1-7])$").as_("m"))
async def show_topics(message: Message, m) -> None:
    g = m.group(1)
    await message.answer(f"🧮 Matematika, {g}-sinf\nMavzuni tanlang:", reply_markup=topics_kb(g))


@dp.message(F.text == BTN_OTHER)
async def other_subjects(message: Message) -> None:
    await message.answer("Boshqa fanlar tez orada qoʻshiladi. Hozircha 🧮 Matematika mavjud.")


@dp.callback_query(F.data.startswith("tp:"))
async def pick_topic(call: CallbackQuery) -> None:
    _, g, t = call.data.split(":")
    name = "🎲 Barcha mavzular aralash" if t == "all" else TOPIC_NAMES.get(int(t), "Mavzu")
    await call.message.edit_text(f"🧮 Matematika, {g}-sinf\n📘 {name}\n\nOʻyinni tanlang:", reply_markup=topic_games_kb(g, t))
    await call.answer()


@dp.callback_query(F.data.startswith("sb:"))
async def back_to_topics(call: CallbackQuery) -> None:
    g = call.data.split(":")[1]
    await call.message.edit_text(f"🧮 Matematika, {g}-sinf\nMavzuni tanlang:", reply_markup=topics_kb(g))
    await call.answer()


@dp.message(F.text.in_({BTN_GAMES, BTN_GAMES_OLD}))
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


@dp.message(Command("id"))
async def show_id(message: Message) -> None:
    await message.answer(f"Sizning Telegram ID raqamingiz: {message.from_user.id}")


@dp.message(F.text == BTN_FEEDBACK)
async def ask_feedback(message: Message) -> None:
    WAIT_FEEDBACK.add(message.from_user.id)
    await message.answer("Savol yoki taklifingizni yozib yuboring. Bekor qilish uchun «🏠 Bosh menyu» ni bosing.",
                         reply_markup=kb([[BTN_HOME]]))


@dp.message(F.text, lambda m: m.from_user.id in WAIT_FEEDBACK)
async def got_feedback(message: Message) -> None:
    WAIT_FEEDBACK.discard(message.from_user.id)
    u = message.from_user
    who = f"{u.full_name}" + (f" (@{u.username})" if u.username else "") + f", id {u.id}"
    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, f"💬 Yangi savol/taklif\n{who}\n\n{message.text[:3500]}")
        except Exception as e:
            log.warning("feedback send failed: %s", e)
    else:
        log.info("FEEDBACK from %s: %s", who, message.text)
    await message.answer("Rahmat! Xabaringiz qabul qilindi. 🙏", reply_markup=menu_kb())


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
