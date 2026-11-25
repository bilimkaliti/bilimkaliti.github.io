"""Bilim Kaliti — sinf o'yinlari uchun Telegram bot.

Bot o'yinlarni Telegram ichida (Mini App) ochadi va o'yin boshlanganda
javob kodlarini o'qituvchiga yuboradi.
"""
import ast
import base64
import asyncio
import datetime
import hashlib
import hmac
import json
import logging
import operator
import os
import random
import re
import secrets
import time
from pathlib import Path
from urllib.parse import parse_qsl

import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    BotCommand,
    MenuButtonWebApp,
    BufferedInputFile,
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
    ("toplam", "nishon", "🎯 Nishon", "har guruhning oʻz nishoni"),
    ("toplam", "mental", "🧮 Mental arifmetika", "ongda hisoblash"),
    ("toplam", "juft", "🃏 Juftini top", "xotira va diqqat"),
    ("toplam", "zanjir", "🔗 Son zanjiri", "ketma-ket amallar"),
    ("bilim", "togri", "✅ Toʻgʻri yoki notoʻgʻri", "istalgan fan uchun"),
    ("bilim", "jlash", "🔗 Juftlash", "soʻz ↔ tarjima, sana ↔ voqea"),
    ("bilim", "tartib", "📅 Tartibga sol", "gap va voqealarni tartibla"),
    ("bilim", "guruh", "🗂️ Guruhlarga ajrat", "soʻzlarni savatlarga joyla"),
    ("bilim", "timsoh", "🐊 Timsohli katakchalar", "katakni tanla — ball yoki timsoh"),
    ("bilim", "million", "💰 Million", "savollar tobora ogʻirlashadi"),
    ("bilim", "harf", "🔤 Anagram", "aralash harflardan soʻz top"),
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
BTN_AI = "✨ AI bilan savollar"
BTN_OWN = "✍️ Oʻz savollarim"
BTN_SETS = "📦 Toʻplamlarim"
BTN_LIB = "📚 Kutubxona"
SITE_URL = os.environ.get("SITE_URL", "https://bilimkaliti.github.io/").rstrip("/") + "/"
LIB_CHAT = int(os.environ.get("LIBRARY_CHAT_ID", "0") or 0)
MATH_FANS = {"matematika", "algebra", "geometriya", "boshlangʻich taʼlim", ""}

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
AI_DAILY = int(os.environ.get("AI_DAILY", "20") or 20)   # bir o'qituvchiga kuniga nechta AI so'rov
MAX_SETS = 30
MAX_ITEMS = 60
SETS_FILE = "bilim-kaliti-toplamlar.json"

bot = Bot(TOKEN)
dp = Dispatcher()

# Har bir o'qituvchining hozirgi o'yindagi javoblari (server qayta ishga tushsa, tozalanadi).
KEYS: dict[int, tuple[str, float]] = {}
WAIT_FEEDBACK: set[int] = set()
WAIT_AI: set[int] = set()
WAIT_OWN: set[int] = set()
AI_USES: dict[tuple[int, str], tuple[str, int]] = {}
SETS_CACHE: dict[int, list[dict]] = {}
SET_LOCKS: dict[int, asyncio.Lock] = {}


def clear_wait(uid: int) -> None:
    for s in (WAIT_FEEDBACK, WAIT_AI, WAIT_OWN):
        s.discard(uid)


def kb(rows: list[list[str]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t) for t in r] for r in rows], resize_keyboard=True)


def menu_kb() -> ReplyKeyboardMarkup:
    return kb([[BTN_CLASSES], [BTN_AI, BTN_OWN], [BTN_SETS, BTN_KEY], [BTN_GAMES, BTN_LIB], [BTN_FEEDBACK, BTN_HELP]])


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


BILIM_GAMES = {"tf": [("togri", "✅ Toʻgʻri yoki notoʻgʻri")], "pair": [("jlash", "🔗 Juftlash")],
               "order": [("tartib", "📅 Tartibga sol")], "group": [("guruh", "🗂️ Guruhlarga ajrat")],
               "mc": [("togri", "✅ Toʻgʻri yoki notoʻgʻri"), ("jlash", "🔗 Juftlash")]}


def set_games_kb(sid: str, mc: bool = False, kind: str = "") -> InlineKeyboardMarkup:
    extra = f"&set={sid}"
    buttons = [] if kind in ("tf", "order", "group") else [
        InlineKeyboardButton(text=title, web_app=WebAppInfo(url=game_url(slug, gk, extra)))
        for slug, gk, title, _ in GRADE_GAMES if gk not in ("zanjir", "mental") and not ((mc or kind == "pair") and gk == "bomba")]
    buttons += [InlineKeyboardButton(text=title, web_app=WebAppInfo(url=game_url("bilim", gk, extra)))
                for gk, title in BILIM_GAMES.get(kind or ("mc" if mc else ""), [])]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    rows.append([InlineKeyboardButton(text="🗑 Oʻchirish", callback_data=f"sd:{sid}"),
                 InlineKeyboardButton(text="📦 Toʻplamlarim", callback_data="sl")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


HELP_TEXT = (
    "Qanday foydalaniladi:\n\n"
    "1. Kompyuterda Telegram Desktop’da shu botni oching va elektron doskaga ulang.\n"
    "2. «📚 Sinflar» → sinf → «🧮 Matematika» → mavzu → oʻyin.\n"
    "   Yoki «🎮 Barcha oʻyinlar» orqali istalgan oʻyinni oching.\n"
    "3. Sozlamalarni tanlab, oʻyinni boshlang. Oʻyin oynasi oʻzi toʻliq ekranga oʻtadi.\n"
    "4. Javob kodlari shu chatga keladi — telefoningizda koʻrib turing.\n"
    "5. Oʻyin davomida hozirgi javoblar uchun «🔑 Javoblar» tugmasini bosing.\n\n"
    "«✨ AI bilan savollar» — mavzuni yozasiz, AI qisqa savollar tuzadi.\n"
    "«✍️ Oʻz savollarim» — oʻzingiz «savol | javob» koʻrinishida yozasiz.\n"
    "«📦 Toʻplamlarim» — saqlangan savollar. Ular oʻyin sozlamalarida ham chiqadi.\n"
    "Oʻyin tugagach, natija va qaysi mavzuni takrorlash kerakligi shu chatga keladi."
)


@dp.message(CommandStart())
async def start(message: Message) -> None:
    clear_wait(message.from_user.id)
    arg = (message.text or "").split(maxsplit=1)[1:] or [""]
    if arg[0].startswith("login_"):
        code = arg[0][6:]
        rec = LOGIN_CODES.get(code)
        if rec and time.time() - rec["t"] < LOGIN_TTL:
            u = message.from_user
            rec["uid"], rec["name"] = u.id, (u.full_name or u.username or "Oʻqituvchi")[:40]
            await message.answer("✅ Saytga kirdingiz! Endi brauzerga qayting — sahifa oʻzi yangilanadi.",
                                 reply_markup=menu_kb())
        else:
            await message.answer("⚠️ Kirish havolasi eskirgan. Saytda «Kirish» tugmasini qaytadan bosing.",
                                 reply_markup=menu_kb())
        return
    await message.answer(
        "Assalomu alaykum! Men «Bilim Kaliti» botiman 🔑\n"
        "Darsda guruhlar bilan oʻynaladigan oʻyinlarni ochib beraman.\n\n"
        "Boshlash uchun «📚 Sinflar» tugmasini bosing.\n\n"
        f"🌐 Sayt (kompyuter va doska uchun): {SITE_URL}\n"
        "📢 Yangiliklar: @bilimkaliti_uz",
        reply_markup=menu_kb(),
    )


@dp.message(F.text == BTN_HOME)
async def home(message: Message) -> None:
    clear_wait(message.from_user.id)
    await message.answer("Bosh menyu", reply_markup=menu_kb())


@dp.message(F.text.in_({BTN_CLASSES, BTN_BACK}))
async def show_classes(message: Message) -> None:
    clear_wait(message.from_user.id)
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
    kbd = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📖 Ona tili", url=SITE_URL + "#/fan/Ona%20tili%20va%20adabiyot"),
                                                 InlineKeyboardButton(text="🇬🇧 Ingliz tili", url=SITE_URL + "#/fan/Ingliz%20tili")],
                                                [InlineKeyboardButton(text="🇷🇺 Rus tili", url=SITE_URL + "#/fan/Rus%20tili"),
                                                 InlineKeyboardButton(text="🌐 Hamma fanlar", url=SITE_URL + "#/kutubxona")]])
    await message.answer("Botda hozircha 🧮 Matematika bor. Ona tili, 🇬🇧 Ingliz tili va 🇷🇺 Rus tili boʻyicha tayyor savollar bazasi saytda — mavzuni tanlab, oʻyinni shu yerning oʻzida boshlaysiz. Boshqa fanlar ketma-ket qoʻshilmoqda.", reply_markup=kbd)


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
    clear_wait(message.from_user.id)
    WAIT_FEEDBACK.add(message.from_user.id)
    await message.answer("Savol yoki taklifingizni yozib yuboring. Bekor qilish uchun «🏠 Bosh menyu» ni bosing.",
                         reply_markup=kb([[BTN_HOME]]))


@dp.message(F.text, lambda m: m.from_user.id in WAIT_FEEDBACK)
async def got_feedback(message: Message) -> None:
    clear_wait(message.from_user.id)
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


# ===================== Toʻplamlar: saqlash =====================
# Render diski vaqtinchalik, shuning uchun toʻplamlar o'qituvchining o'z chatida
# biriktirilgan (pin) JSON faylda saqlanadi.

def lock_for(uid: int) -> asyncio.Lock:
    if uid not in SET_LOCKS:
        SET_LOCKS[uid] = asyncio.Lock()
    return SET_LOCKS[uid]


async def load_sets(uid: int) -> list[dict]:
    if uid in SETS_CACHE:
        return SETS_CACHE[uid]
    sets: list[dict] = []
    try:
        chat = await bot.get_chat(uid)
        pm = chat.pinned_message
        if pm and pm.document and pm.document.file_name == SETS_FILE:
            buf = await bot.download(pm.document.file_id)
            data = json.loads(buf.read().decode("utf-8"))
            if isinstance(data, list):
                sets = [s for s in data if isinstance(s, dict) and s.get("id") and isinstance(s.get("items"), list)]
    except Exception as e:
        log.warning("load_sets %s: %s", uid, e)
    SETS_CACHE[uid] = sets
    return sets


async def save_sets(uid: int, sets: list[dict]) -> None:
    SETS_CACHE[uid] = sets
    old = None
    try:
        old = (await bot.get_chat(uid)).pinned_message
    except Exception:
        pass
    data = json.dumps(sets, ensure_ascii=False).encode("utf-8")
    msg = await bot.send_document(
        uid, BufferedInputFile(data, filename=SETS_FILE),
        caption="📦 Toʻplamlaringiz shu faylda saqlanadi. Bu xabarni oʻchirmang va pindan olmang.",
        disable_notification=True,
    )
    try:
        await bot.pin_chat_message(uid, msg.message_id, disable_notification=True)
    except Exception as e:
        log.warning("pin failed: %s", e)
    if old and old.document and old.document.file_name == SETS_FILE:
        try:
            await bot.delete_message(uid, old.message_id)
        except Exception:
            pass


async def add_set(uid: int, name: str, items: list[dict], src: str, fan: str = "",
                  sinf: str = "", mavzu: str = "", pub: bool = True) -> tuple[dict, bool]:
    async with lock_for(uid):
        sets = list(await load_sets(uid))
        s = {"id": secrets.token_hex(3), "name": name[:60], "src": src, "t": int(time.time()), "items": items[:MAX_ITEMS]}
        if fan:
            s["fan"] = fan[:60]
        sets.append(s)
        dropped = len(sets) > MAX_SETS
        sets = sets[-MAX_SETS:]
        await save_sets(uid, sets)
    stat_inc("sets")
    if pub and AUTO_PUB:
        asyncio.create_task(lib_auto(uid, s, sinf, mavzu))
    return s, dropped


def set_preview(s: dict, limit: int = 12) -> str:
    lines = [f"📦 «{s['name']}» — {len(s['items'])} ta savol\n"]
    for i, it in enumerate(s["items"][:limit], 1):
        k = item_kind(it)
        if k == "mc":
            lines.append(f"{i}. {it['q']}  →  {it['o'][it.get('c', 0)]}")
        elif k == "num":
            lines.append(f"{i}. {it['q']}  →  {it['a']}")
        elif k == "tf":
            lines.append(f"{i}. {it['q']}  →  {'✅ toʻgʻri' if it['t'] else '❌ notoʻgʻri'}")
        elif k == "pair":
            lines.append(f"{i}. {it['a']}  ↔  {it['b']}")
        elif k == "order":
            lines.append(f"{i}. {it['q']}: " + " → ".join(it["s"]))
        else:
            lines.append(f"{i}. {it['q']}: " + "; ".join(f"{g['n']}: {', '.join(g['w'])}" for g in it["g"]))
    if len(s["items"]) > limit:
        lines.append(f"… yana {len(s['items']) - limit} ta")
    small = sum(1 for it in s["items"] if item_kind(it) == "num" and 1 <= it["a"] <= 9)
    lines.append("\nOʻyinni tanlang 👇")
    if any("o" in it for it in s["items"]):
        lines.append("(Test savollari: oʻquvchi toʻgʻri variant raqamini bosadi. 💣 Bomba son-javobli savollar uchun.)")
    elif set_kind(s["items"]) in ("tf", "pair", "order", "group"):
        lines[-1] = "\nOʻyinni tanlang 👇"
    elif small < len(s["items"]):
        lines.append("(💣 Bomba va bir xonali rejimda faqat javobi 1–9 boʻlgan savollar chiqadi.)")
    return "\n".join(lines)[:4000]


# ===================== Oʻz savollarim =====================

def parse_own(text: str) -> tuple[str, list[dict], list[int]]:
    name, items, bad = "", [], []
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        if "|" not in line:
            if not name and not items:
                name = line[:60]
            else:
                bad.append(n)
            continue
        parts = [x.strip() for x in line.split("|")]
        if len(parts) >= 3 and parts[0] and all(parts[1:5]):
            opts = list(dict.fromkeys(x[:120] for x in parts[1:5]))
            if len(opts) >= 2:
                items.append({"q": parts[0][:300], "o": opts, "c": 0})
                continue
        q, _, a = line.rpartition("|")
        q, a = q.strip(), a.strip().replace(" ", "")
        if q and re.fullmatch(r"\d{1,4}", a):
            items.append({"q": q[:300], "a": int(a)})
        else:
            bad.append(n)
    return name, items, bad


@dp.message(F.text == BTN_OWN)
async def ask_own(message: Message) -> None:
    clear_wait(message.from_user.id)
    WAIT_OWN.add(message.from_user.id)
    await message.answer(
        "✍️ Savollaringizni bitta xabarda yozing. Har bir qator: savol | javob\n"
        "Birinchi qatorga (| belgisiz) toʻplam nomini yozsangiz boʻladi.\n\n"
        "Namuna:\n"
        "Kasrlar — 5-sinf\n"
        "1/2 + 1/2 = ? | 1\n"
        "36 ning 1/4 qismi | 9\n"
        "Kvadratning tomoni 7 sm. Perimetri? | 28\n\n"
        "Test savoli (istalgan fan): savol | toʻgʻri javob | xato | xato | xato\n"
        "Fransiyaning poytaxti? | Parij | Lion | Marsel | Nitstsa\n\n"
        "Son-javob — butun son (0–9999). Bekor qilish: «🏠 Bosh menyu».",
        reply_markup=kb([[BTN_HOME]]),
    )


@dp.message(F.text, lambda m: m.from_user.id in WAIT_OWN)
async def got_own(message: Message) -> None:
    uid = message.from_user.id
    name, items, bad = parse_own(message.text or "")
    if not items:
        await message.answer("Birorta ham «savol | javob» qatori topilmadi. Namunadagidek qaytadan yozing.")
        return
    WAIT_OWN.discard(uid)
    name = name or f"Oʻz savollarim ({datetime.date.today():%d.%m})"
    s, dropped = await add_set(uid, name, items, "own")
    note = f"\n⚠️ {', '.join(map(str, bad[:10]))}-qatorlar tushunilmadi va tashlab ketildi." if bad else ""
    if dropped:
        note += f"\nℹ️ Eng koʻpi {MAX_SETS} ta toʻplam saqlanadi, eng eskisi oʻchirildi."
    await message.answer("✅ Saqlandi." + note, reply_markup=menu_kb())
    await message.answer(set_preview(s), reply_markup=set_games_kb(s["id"], any("o" in it for it in s["items"]), set_kind(s["items"])))


# ===================== AI (Gemini) =====================
GEM_API = "https://generativelanguage.googleapis.com/v1beta"
_MODEL: str | None = None

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow}


def safe_eval(expr: str) -> float | None:
    """Faqat sonlar va + - * / // % ** dan iborat ifodani hisoblaydi."""
    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
            return n.value
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            v = ev(n.operand)
            return -v if isinstance(n.op, ast.USub) else v
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
            a, b = ev(n.left), ev(n.right)
            if isinstance(n.op, ast.Pow) and (abs(b) > 12 or abs(a) > 1000):
                raise ValueError("katta daraja")
            return _OPS[type(n.op)](a, b)
        raise ValueError("ruxsat etilmagan")
    try:
        expr = str(expr).replace("×", "*").replace("·", "*").replace(":", "/").replace("÷", "/").replace("^", "**")
        if len(expr) > 120:
            return None
        return float(ev(ast.parse(expr, mode="eval")))
    except Exception:
        return None


def check_items(raw) -> list[dict]:
    out, seen = [], set()
    for it in raw if isinstance(raw, list) else []:
        if not isinstance(it, dict):
            continue
        q = str(it.get("q", "")).strip()
        try:
            a = int(it.get("a"))
        except (TypeError, ValueError):
            continue
        v = safe_eval(it.get("expr", ""))
        if not q or len(q) > 220 or not (0 <= a <= 9999) or v is None or abs(v - a) > 1e-9 or q in seen:
            continue
        seen.add(q)
        out.append({"q": q, "a": a})
    return out


async def gemini_model(session: aiohttp.ClientSession) -> str:
    """Mavjud modellar ichidan bepul va tez «flash-lite» ni avtomatik tanlaydi."""
    global _MODEL
    if _MODEL:
        return _MODEL
    names: list[str] = []
    try:
        async with session.get(f"{GEM_API}/models", params={"pageSize": "200"},
                               headers={"x-goog-api-key": GEMINI_KEY}) as r:
            data = await r.json()
        names = [m["name"] for m in data.get("models", [])
                 if "generateContent" in m.get("supportedGenerationMethods", []) and "gemini" in m.get("name", "")]
    except Exception as e:
        log.warning("ListModels: %s", e)

    def score(n: str):
        s = 4 if "flash-lite" in n else 2 if "flash" in n else 0
        if any(x in n for x in ("preview", "exp", "tts", "image", "live", "audio", "thinking", "embed")):
            s -= 3
        m = re.search(r"gemini-(\d+(?:\.\d+)?)", n)
        return (s, float(m.group(1)) if m else 0.0, "latest" not in n)
    _MODEL = max(names, key=score) if names else "models/gemini-2.0-flash-lite"
    log.info("Gemini model: %s", _MODEL)
    return _MODEL


AI_PROMPT = """Sen boshlangʻich sinf va 5–7-sinf matematika oʻqituvchisining yordamchisisan.
Oʻqituvchining soʻrovi: «{topic}»

Shu mavzuda {n} ta QISQA va TEZ yechiladigan savol tuz:
- oʻquvchi 10–30 soniyada, asosan ogʻzaki yechsin; uzun masala emas, 1–2 qisqa gap;
- maqsad: diqqat, mantiqiy fikrlash va fanga qiziqishni oshirish; qiziqarli, hayotiy misollar boʻlsin;
- sinf aytilgan boʻlsa, oʻsha sinf darajasiga mos boʻlsin;
- javob har doim BUTUN SON, 0 dan 999 gacha (kasr yoki manfiy javob boʻlmasin);
- savollar bir-birini takrorlamasin, qiyinligi asta-sekin oshsin;
- til: oʻzbek tili, lotin yozuvi (oʻ, gʻ harflari bilan).
Har bir savol uchun "expr" — javobni hisoblab beradigan arifmetik ifoda yoz (faqat raqamlar, + - * / // % ** va qavslar), masalan "(36/4)*2".
Faqat JSON qaytar:
{{"name": "toʻplam uchun qisqa nom", "items": [{{"q": "savol matni", "a": 18, "expr": "(36/4)*2"}}]}}"""


async def gemini_questions(topic: str, n: int = 12) -> tuple[str, list[dict]]:
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        model = await gemini_model(session)
        body = {
            "contents": [{"role": "user", "parts": [{"text": AI_PROMPT.format(topic=topic, n=n)}]}],
            "generationConfig": {"temperature": 0.9, "responseMimeType": "application/json"},
        }
        async with session.post(f"{GEM_API}/{model}:generateContent", json=body,
                                headers={"x-goog-api-key": GEMINI_KEY}) as r:
            if r.status == 429:
                raise RuntimeError("limit")
            if r.status == 404:
                global _MODEL
                _MODEL = None
            data = await r.json()
            if r.status != 200:
                raise RuntimeError(f"http {r.status}: {str(data)[:300]}")
    text = "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    obj = json.loads(text)
    if isinstance(obj, list):
        obj = {"items": obj}
    return str(obj.get("name") or topic)[:60], check_items(obj.get("items"))


CHAT_DAILY = int(os.environ.get("CHAT_DAILY", "40") or 40)


def ai_left(uid: int, kind: str = "gen") -> int:
    today = datetime.date.today().isoformat()
    day, used = AI_USES.get((uid, kind), (today, 0))
    if day != today:
        used = 0
    base = CHAT_DAILY if kind == "chat" else AI_DAILY
    limit = base * 4 if uid == ADMIN_ID else base
    return limit - used


def ai_use(uid: int, kind: str = "gen") -> None:
    today = datetime.date.today().isoformat()
    day, used = AI_USES.get((uid, kind), (today, 0))
    AI_USES[(uid, kind)] = (today, (used if day == today else 0) + 1)
    stat_inc("ai" if kind == "gen" else "chat")


@dp.message(F.text == BTN_AI)
async def ask_ai(message: Message) -> None:
    clear_wait(message.from_user.id)
    if not GEMINI_KEY:
        await message.answer("✨ AI hali ulanmagan. Administrator Render’da GEMINI_API_KEY ni qoʻshishi kerak.")
        return
    if ai_left(message.from_user.id) <= 0:
        await message.answer("Bugungi AI soʻrovlar soni tugadi. Ertaga yana urinib koʻring 🙂")
        return
    WAIT_AI.add(message.from_user.id)
    await message.answer(
        "✨ Sinf va mavzuni yozing, AI 12 ta qisqa savol tuzadi.\n\n"
        "Namunalar:\n"
        "• 5-sinf, kasrlarni qoʻshish\n"
        "• 3-sinf, koʻpaytirish jadvali, mantiqiy savollar\n"
        "• 6-sinf, EKUK va EKUB\n"
        "• 2-sinf, soat va vaqt\n\n"
        "Bekor qilish: «🏠 Bosh menyu».",
        reply_markup=kb([[BTN_HOME]]),
    )


@dp.message(F.text, lambda m: m.from_user.id in WAIT_AI)
async def got_ai(message: Message) -> None:
    uid = message.from_user.id
    topic = (message.text or "").strip()[:200]
    if len(topic) < 3:
        await message.answer("Mavzuni biroz batafsilroq yozing.")
        return
    WAIT_AI.discard(uid)
    if ai_left(uid) <= 0:
        await message.answer("Bugungi AI soʻrovlar soni tugadi. Ertaga yana urinib koʻring 🙂", reply_markup=menu_kb())
        return
    wait = await message.answer("⏳ AI savollarni tayyorlayapti… (10–30 soniya)", reply_markup=menu_kb())
    ai_use(uid)
    try:
        name, items = await gemini_questions(topic)
    except RuntimeError as e:
        log.warning("gemini: %s", e)
        txt = ("AI hozir band (bepul limit). Bir daqiqadan keyin yana urinib koʻring."
               if str(e) == "limit" else "AI javob bermadi. Birozdan keyin yana urinib koʻring.")
        await wait.edit_text("⚠️ " + txt)
        return
    except Exception as e:
        log.warning("gemini parse: %s", e)
        await wait.edit_text("⚠️ AI javobini oʻqib boʻlmadi. Yana bir bor urinib koʻring.")
        return
    if len(items) < 4:
        await wait.edit_text("⚠️ AI yetarlicha toʻgʻri savol tuza olmadi. Mavzuni boshqacharoq yozib koʻring.")
        return
    s, dropped = await add_set(uid, name, items, "ai")
    try:
        await wait.delete()
    except Exception:
        pass
    note = f"\nℹ️ Eng koʻpi {MAX_SETS} ta toʻplam saqlanadi, eng eskisi oʻchirildi." if dropped else ""
    await message.answer(
        f"✅ Tayyor! Har bir javob avtomatik tekshirildi.{note}\n"
        "Baribir oʻyindan oldin koʻz yugurtirib chiqing.")
    await message.answer(set_preview(s), reply_markup=set_games_kb(s["id"], any("o" in it for it in s["items"]), set_kind(s["items"])))


# ===================== Toʻplamlarim =====================

def sets_list_kb(sets: list[dict]) -> InlineKeyboardMarkup:
    icon = {"ai": "✨", "own": "✍️"}
    rows = [[InlineKeyboardButton(text=f"{icon.get(s.get('src'), '📦')} {s['name']} ({len(s['items'])})",
                                  callback_data=f"so:{s['id']}")] for s in reversed(sets)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def send_sets_list(uid: int, edit: Message | None = None) -> None:
    sets = await load_sets(uid)
    if not sets:
        text = "Hozircha toʻplam yoʻq.\n«✨ AI bilan savollar» yoki «✍️ Oʻz savollarim» orqali yarating."
        if edit:
            await edit.edit_text(text)
        else:
            await bot.send_message(uid, text)
        return
    text = "📦 Toʻplamlaringiz. Birini tanlang:"
    if edit:
        await edit.edit_text(text, reply_markup=sets_list_kb(sets))
    else:
        await bot.send_message(uid, text, reply_markup=sets_list_kb(sets))


@dp.message(Command("sayt"))
async def site_cmd(message: Message) -> None:
    kbd = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🌐 Saytni ochish", url=SITE_URL)],
                                                [InlineKeyboardButton(text="📲 Telegram ichida ochish", web_app=WebAppInfo(url=SITE_URL))],
                                                [InlineKeyboardButton(text="📢 Yangiliklar kanali", url="https://t.me/bilimkaliti_uz")]])
    await message.answer(f"🌐 Bilim Kaliti sayti: {SITE_URL}\n\nKompyuter yoki elektron doskada shu manzilni oching — "
                         "oʻyinlar, AI yordamchi, kutubxona va sinf vositalari.", reply_markup=kbd)


@dp.message(F.text == BTN_LIB)
async def show_lib(message: Message) -> None:
    clear_wait(message.from_user.id)
    kbd = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📚 Kutubxonani ochish", url=SITE_URL + "#/kutubxona")],
                                                [InlineKeyboardButton(text="🌐 Saytni ochish", url=SITE_URL)]])
    await message.answer("📚 Kutubxonada oʻqituvchilar ulashgan toʻplamlar bor: fan, sinf va mavzu boʻyicha qidiring, "
                         "bir bosishda oʻynang. Oʻz toʻplamingizni ham saytdagi «📦 Toʻplamlarim» boʻlimidan ulashing.",
                         reply_markup=kbd)


@dp.channel_post(Command("ulash"))
async def lib_connect(post: Message) -> None:
    await bot.send_message(post.chat.id, f"✅ Kanal ID: {post.chat.id}\n\nRender → Environment → LIBRARY_CHAT_ID = {post.chat.id}\n"
                                         "Shuni qoʻshgach, kutubxona shu kanalda saqlanadi.")


@dp.message(F.text == BTN_SETS)
async def show_sets(message: Message) -> None:
    clear_wait(message.from_user.id)
    await send_sets_list(message.from_user.id)


@dp.callback_query(F.data == "sl")
async def cb_sets_list(call: CallbackQuery) -> None:
    await send_sets_list(call.from_user.id, edit=call.message)
    await call.answer()


@dp.callback_query(F.data.startswith("so:"))
async def cb_set_open(call: CallbackQuery) -> None:
    sid = call.data[3:]
    s = next((x for x in await load_sets(call.from_user.id) if x["id"] == sid), None)
    if not s:
        await call.answer("Toʻplam topilmadi", show_alert=True)
        return
    await call.message.edit_text(set_preview(s), reply_markup=set_games_kb(sid, any("o" in it for it in s["items"]), set_kind(s["items"])))
    await call.answer()


@dp.callback_query(F.data.startswith("sd:"))
async def cb_set_delete(call: CallbackQuery) -> None:
    sid = call.data[3:]
    kbd = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Ha, oʻchirish", callback_data=f"sx:{sid}"),
        InlineKeyboardButton(text="↩️ Yoʻq", callback_data=f"so:{sid}")]])
    await call.message.edit_reply_markup(reply_markup=kbd)
    await call.answer("Rostdan oʻchirasizmi?")


@dp.callback_query(F.data.startswith("sx:"))
async def cb_set_delete_yes(call: CallbackQuery) -> None:
    sid, uid = call.data[3:], call.from_user.id
    async with lock_for(uid):
        sets = [s for s in await load_sets(uid) if s["id"] != sid]
        await save_sets(uid, sets)
    asyncio.create_task(lib_unlink(uid, sid))
    await call.answer("Oʻchirildi")
    await send_sets_list(uid, edit=call.message)


# ===================== KUTUBXONA (Telegram kanalida saqlanadi) =====================
LIB_INDEX_FILE = "bilim-kaliti-kutubxona.json"
LIB: dict | None = None
LIB_ITEMS: dict[str, list] = {}
LIB_LOCK = asyncio.Lock()
LIB_DIRTY = False


def _s(v, n: int) -> str:
    return str(v if v is not None else "").strip()[:n]


def item_kind(it: dict) -> str:
    if "o" in it:
        return "mc"
    if "t" in it:
        return "tf"
    if "b" in it:
        return "pair"
    if "s" in it:
        return "order"
    if "g" in it:
        return "group"
    return "num"


def set_kind(items: list) -> str:
    ks = {item_kind(it) for it in items}
    return ks.pop() if len(ks) == 1 else ("mc" if "mc" in ks else "mix")


def norm_items(raw) -> list[dict]:
    out = []
    for it in raw if isinstance(raw, list) else []:
        if not isinstance(it, dict):
            continue
        if "b" in it and "o" not in it:
            a, b = _s(it.get("a"), 160), _s(it.get("b"), 160)
            if a and b:
                out.append({"a": a, "b": b})
            continue
        if isinstance(it.get("s"), list):
            s = [_s(x, 120) for x in it["s"] if _s(x, 120)][:8]
            if len(s) >= 3 and len(set(s)) == len(s):
                out.append({"q": _s(it.get("q"), 200) or "Toʻgʻri tartibga soling", "s": s})
            continue
        if isinstance(it.get("g"), list):
            g = []
            for x in it["g"][:4]:
                if isinstance(x, dict):
                    w = [_s(y, 80) for y in (x.get("w") or []) if _s(y, 80)][:10] if isinstance(x.get("w"), list) else []
                    if _s(x.get("n"), 60) and w:
                        g.append({"n": _s(x.get("n"), 60), "w": w})
            if len(g) >= 2:
                out.append({"q": _s(it.get("q"), 200) or "Guruhlarga ajrating", "g": g})
            continue
        q = str(it.get("q", "")).strip()[:600]
        if not q:
            continue
        if "t" in it and "o" not in it and "a" not in it:
            out.append({"q": q, "t": 1 if it.get("t") in (1, True, "1", "true", "toʻgʻri") else 0})
            continue
        if isinstance(it.get("o"), list):
            o = [str(x).strip()[:200] for x in it["o"] if str(x).strip()][:4]
            try:
                c = int(it.get("c", 0))
            except (TypeError, ValueError):
                continue
            if len(o) >= 2 and len(set(o)) == len(o) and 0 <= c < len(o):
                out.append({"q": q, "o": o, "c": c})
        else:
            try:
                a = int(it.get("a"))
            except (TypeError, ValueError):
                continue
            if 0 <= a <= 9999:
                out.append({"q": q, "a": a})
    return out[:MAX_ITEMS]


async def lib_load() -> dict:
    global LIB
    if LIB is not None:
        return LIB
    async with LIB_LOCK:
        if LIB is not None:
            return LIB
        data = {"sets": []}
        if LIB_CHAT:
            try:
                pm = (await bot.get_chat(LIB_CHAT)).pinned_message
                if pm and pm.document and pm.document.file_name == LIB_INDEX_FILE:
                    d = json.loads((await bot.download(pm.document.file_id)).read().decode("utf-8"))
                    if isinstance(d, dict) and isinstance(d.get("sets"), list):
                        data = d
            except Exception as e:
                log.warning("lib_load: %s", e)
        LIB = data
    return LIB


async def lib_save_index() -> None:
    """LIB_LOCK ichida chaqiriladi."""
    global LIB_DIRTY
    old = None
    try:
        old = (await bot.get_chat(LIB_CHAT)).pinned_message
    except Exception:
        pass
    msg = await bot.send_document(LIB_CHAT, BufferedInputFile(json.dumps(LIB, ensure_ascii=False).encode("utf-8"), filename=LIB_INDEX_FILE),
                                  caption="📚 Kutubxona roʻyxati. Bu xabarni oʻchirmang.", disable_notification=True)
    try:
        await bot.pin_chat_message(LIB_CHAT, msg.message_id, disable_notification=True)
        try:
            await bot.delete_message(LIB_CHAT, msg.message_id + 1)  # «pinned» xizmat xabari
        except Exception:
            pass
    except Exception as e:
        log.warning("lib pin: %s", e)
    if old and old.document and old.document.file_name == LIB_INDEX_FILE:
        try:
            await bot.delete_message(LIB_CHAT, old.message_id)
        except Exception:
            pass
    LIB_DIRTY = False


async def lib_flush_loop(app: web.Application) -> None:
    async def loop():
        while True:
            await asyncio.sleep(1800)
            if LIB_DIRTY and LIB_CHAT and LIB is not None:
                try:
                    async with LIB_LOCK:
                        await lib_save_index()
                except Exception as e:
                    log.warning("lib flush: %s", e)
    app["lib_task"] = asyncio.create_task(loop())


# ===================== STATISTIKA (faqat admin koʻradi) =====================
# Saqlanadi: kutubxona kanalidagi alohida JSON fayl, fayl manzili kutubxona roʻyxatida (LIB["stat"]).
STAT_FILE = "bilim-kaliti-statistika.json"
STAT: dict | None = None
STAT_DIRTY = False
STAT_LOCK = asyncio.Lock()
ONLINE: dict[str, tuple[float, str]] = {}   # tashrif id -> (oxirgi vaqt, sahifa)
STAT_KEEP_DAYS = 120


def _today() -> str:
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=5)).date().isoformat()   # Toshkent vaqti


def _stat_blank() -> dict:
    return {"v": 1, "since": _today(), "users": {}, "days": {}, "games": {}, "tools": {}, "pages": {},
            "today": {"d": _today(), "vis": [], "act": []}}


async def stat_load() -> dict:
    global STAT
    if STAT is not None:
        return STAT
    async with STAT_LOCK:
        if STAT is not None:
            return STAT
        data = _stat_blank()
        if LIB_CHAT:
            try:
                ref = (await lib_load()).get("stat") or {}
                if ref.get("file"):
                    d = json.loads((await bot.download(ref["file"])).read().decode("utf-8"))
                    if isinstance(d, dict) and isinstance(d.get("users"), dict):
                        for k, v in _stat_blank().items():
                            d.setdefault(k, v)
                        data = d
            except Exception as e:
                log.warning("stat_load: %s", e)
        STAT = data
    return STAT


def _day(s: dict) -> dict:
    """Bugungi kun yozuvi; kun almashsa, kechagi noyob roʻyxatlar songa aylanadi."""
    t = s["today"]
    d = _today()
    if t.get("d") != d:
        old = s["days"].setdefault(t.get("d") or d, {})
        old["v"], old["au"] = len(t.get("vis") or []), len(t.get("act") or [])
        s["today"] = t = {"d": d, "vis": [], "act": []}
        for k in sorted(s["days"])[:-STAT_KEEP_DAYS]:
            s["days"].pop(k, None)
    return s["days"].setdefault(d, {})


def stat_inc(key: str, n: int = 1, sub: str | None = None, name: str | None = None) -> None:
    """Hisoblagichni oshiradi (STAT yuklangan boʻlsa)."""
    global STAT_DIRTY
    s = STAT
    if s is None:
        return
    day = _day(s)
    day[key] = day.get(key, 0) + n
    if sub and name:
        bucket = s.setdefault(sub, {})
        name = str(name)[:40]
        if name in bucket or len(bucket) < 300:
            bucket[name] = bucket.get(name, 0) + n
    STAT_DIRTY = True


def stat_user(uid: int, name: str = "", username: str = "", src: str = "bot") -> None:
    global STAT_DIRTY
    s = STAT
    if s is None or not uid:
        return
    _day(s)
    now = int(time.time())
    u = s["users"].get(str(uid))
    if u is None:
        u = s["users"][str(uid)] = {"n": "", "u": "", "f": now, "l": now, "src": [], "a": 0}
        stat_inc("new")
    if name:
        u["n"] = str(name)[:60]
    if username:
        u["u"] = str(username)[:40]
    u["l"] = now
    u["a"] = u.get("a", 0) + 1
    if src not in u["src"]:
        u["src"].append(src)
    act = s["today"]["act"]
    if uid not in act:
        act.append(uid)
    STAT_DIRTY = True


async def stat_save() -> None:
    global STAT_DIRTY
    if STAT is None or not LIB_CHAT:
        return
    async with STAT_LOCK:
        _day(STAT)
        body = json.dumps(STAT, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        STAT_DIRTY = False
        msg = await bot.send_document(LIB_CHAT, BufferedInputFile(body, filename=STAT_FILE),
                                      caption="📊 Statistika (avtomatik). Oʻchirmang.", disable_notification=True)
    async with LIB_LOCK:
        lib = LIB if LIB is not None else None
        if lib is None:
            return
        old = lib.get("stat") or {}
        lib["stat"] = {"file": msg.document.file_id, "mid": msg.message_id, "t": int(time.time())}
        await lib_save_index()
    if old.get("mid"):
        try:
            await bot.delete_message(LIB_CHAT, old["mid"])
        except Exception:
            pass


async def stat_loop(app: web.Application) -> None:
    async def loop():
        try:
            await lib_load()
            await stat_load()
        except Exception as e:
            log.warning("stat init: %s", e)
        while True:
            await asyncio.sleep(600)
            if STAT_DIRTY:
                try:
                    await stat_save()
                except Exception as e:
                    log.warning("stat save: %s", e)
    app["stat_task"] = asyncio.create_task(loop())


async def stat_shutdown(app: web.Application) -> None:
    """Server uxlashidan oldin (Render) soʻnggi maʼlumotlarni saqlab qoʻyadi."""
    if STAT_DIRTY:
        try:
            await asyncio.wait_for(stat_save(), 20)
        except Exception as e:
            log.warning("stat shutdown: %s", e)


@dp.update.outer_middleware()
async def stat_mw(handler, event, data):
    try:
        u = data.get("event_from_user")
        if u and not u.is_bot:
            stat_user(u.id, u.full_name, u.username or "", "bot")
            if event.message is not None:
                stat_inc("bot")
    except Exception as e:
        log.warning("stat_mw: %s", e)
    return await handler(event, data)


_VID = re.compile(r"^[A-Za-z0-9_-]{6,32}$")


async def api_hit(request: web.Request) -> web.Response:
    """Sayt va oʻyinlardan anonim tashrif belgisi (shaxsiy maʼlumotsiz)."""
    data = await read_json(request)
    await stat_load()
    vid, kind = str(data.get("v", "")), str(data.get("k", "view"))
    if not _VID.match(vid):
        return web.json_response({"ok": False})
    page = re.sub(r"[^\w/\-]", "", str(data.get("p", "")))[:40] or "home"
    now = time.time()
    ONLINE[vid] = (now, page)
    if len(ONLINE) > 3000:
        for k, (t, _) in list(ONLINE.items()):
            if now - t > 300:
                ONLINE.pop(k, None)
    if kind == "beat":
        return web.json_response({"ok": True})
    day = _day(STAT)
    vis = STAT["today"]["vis"]
    if vid not in vis and len(vis) < 20000:
        vis.append(vid)
        dev = "m" if data.get("m") else "d"
        stat_inc("dev_" + dev)
    if kind == "game":
        stat_inc("g", sub="games", name=re.sub(r"[^\w\-]", "", str(data.get("g", "")))[:30] or "?")
    elif kind == "view":
        stat_inc("pv", sub="pages", name=page.split("/")[0] or "home")
    u = read_token(str(data.get("token", ""))) if data.get("token") else None
    if u:
        stat_user(u["u"], u.get("n", ""), "", "site")
    return web.json_response({"ok": True})


def _series(s: dict, n: int = 30) -> list[dict]:
    base = datetime.date.fromisoformat(_today())
    out = []
    for i in range(n - 1, -1, -1):
        d = (base - datetime.timedelta(days=i)).isoformat()
        row = dict(s["days"].get(d, {}))
        if d == s["today"]["d"]:
            row["v"], row["au"] = len(s["today"]["vis"]), len(s["today"]["act"])
        out.append({"d": d, **{k: row.get(k, 0) for k in ("v", "au", "pv", "g", "new", "ai", "chat", "bot", "lib", "pub", "sets")}})
    return out


async def stat_report() -> dict:
    s = await stat_load()
    _day(s)
    now = time.time()
    ser = _series(s, 30)
    users = s["users"]
    week = now - 7 * 86400
    month = now - 30 * 86400
    online = sum(1 for t, _ in ONLINE.values() if now - t < 150)
    pages_now: dict[str, int] = {}
    for t, p in ONLINE.values():
        if now - t < 150:
            pages_now[p.split("/")[0] or "home"] = pages_now.get(p.split("/")[0] or "home", 0) + 1
    tot = lambda k: sum(r.get(k, 0) for r in s["days"].values())
    lib = await lib_load()
    ul = sorted(({"id": int(k), **v} for k, v in users.items()), key=lambda x: -x.get("l", 0))
    return {
        "since": s.get("since"), "now": int(now), "online": online, "pagesNow": pages_now,
        "users": {"total": len(users), "today": len(s["today"]["act"]),
                  "week": sum(1 for u in users.values() if u.get("l", 0) >= week),
                  "month": sum(1 for u in users.values() if u.get("l", 0) >= month),
                  "site": sum(1 for u in users.values() if "site" in u.get("src", [])),
                  "bot": sum(1 for u in users.values() if "bot" in u.get("src", []))},
        "visitors": {"today": len(s["today"]["vis"]), "week": sum(r["v"] for r in ser[-7:]), "month": sum(r["v"] for r in ser)},
        "totals": {"games": tot("g"), "ai": tot("ai"), "chat": tot("chat"), "pv": tot("pv"), "bot": tot("bot"),
                   "lib": tot("lib"), "pub": tot("pub"), "sets": tot("sets"), "pdf": tot("pdf"),
                   "mob": tot("dev_m"), "desk": tot("dev_d")},
        "library": {"sets": len(lib.get("sets", [])), "plays": sum(int(m.get("plays") or 0) for m in lib.get("sets", []))},
        "series": ser,
        "games": sorted(s.get("games", {}).items(), key=lambda x: -x[1])[:20],
        "tools": sorted(s.get("tools", {}).items(), key=lambda x: -x[1])[:20],
        "pages": sorted(s.get("pages", {}).items(), key=lambda x: -x[1])[:15],
        "list": ul[:500],
    }


async def api_admin_stats(request: web.Request) -> web.Response:
    u = site_user(await read_json(request))
    if not u or not ADMIN_ID or u["u"] != ADMIN_ID:
        return jerr("Bu sahifa faqat admin uchun.", 403)
    return web.json_response({"ok": True, "stat": await stat_report()})


@dp.message(Command("stat"))
async def cmd_stat(message: Message) -> None:
    if not ADMIN_ID or message.from_user.id != ADMIN_ID:
        return
    r = await stat_report()
    U, V, T = r["users"], r["visitors"], r["totals"]
    top = "\n".join(f"   {i}. {g} — {n}" for i, (g, n) in enumerate(r["games"][:5], 1)) or "   hali yoʻq"
    last = "\n".join(f"   • {x.get('n') or '—'}{' @' + x['u'] if x.get('u') else ''}" for x in r["list"][:5]) or "   —"
    text = (f"📊 Bilim Kaliti statistikasi ({r['since']} dan beri)\n\n"
            f"🟢 Hozir saytda: {r['online']}\n\n"
            f"👤 Foydalanuvchilar (bot/sayt orqali kirgan): {U['total']}\n"
            f"   bugun faol: {U['today']} · 7 kun: {U['week']} · 30 kun: {U['month']}\n"
            f"   botda: {U['bot']} · saytga kirgan: {U['site']}\n\n"
            f"🌐 Sayt tashrifchilari: bugun {V['today']} · 7 kun {V['week']} · 30 kun {V['month']}\n"
            f"🎮 Oʻyinlar boshlangan: {T['games']}\n"
            f"✨ AI soʻrovlar: {T['ai']} · chat: {T['chat']}\n"
            f"📚 Kutubxona: {r['library']['sets']} toʻplam, {r['library']['plays']} marta oʻynalgan\n\n"
            f"🏆 Eng koʻp oʻynalgan:\n{top}\n\n🕒 Oxirgi faollar:\n{last}")
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📊 Batafsil (saytda)", url=SITE_URL + "#/admin")]]))


def lib_meta(m: dict) -> dict:
    return {k: m.get(k) for k in ("id", "name", "fan", "sinf", "mavzu", "author", "n", "mc", "kind", "t", "plays")}


async def api_lib_list(request: web.Request) -> web.Response:
    data = await read_json(request)
    lib = await lib_load()
    fan, sinf, qq = clip(data.get("fan"), 60), clip(data.get("sinf"), 10), clip(data.get("q"), 60).lower()
    u = site_user(data) if data.get("token") else None
    res = []
    for m in lib["sets"]:
        if fan and m.get("fan") != fan:
            continue
        if sinf and str(m.get("sinf")) != sinf:
            continue
        if qq and qq not in f"{m.get('name','')} {m.get('mavzu','')} {m.get('author','')}".lower():
            continue
        x = lib_meta(m)
        x["mine"] = bool(u and (u["u"] == m.get("uid") or u["u"] == ADMIN_ID))
        res.append(x)
    order = str(data.get("sort", "new"))
    if order == "top":
        res.sort(key=lambda m: -(m.get("plays") or 0))
    return web.json_response({"ok": True, "on": bool(LIB_CHAT), "sets": res[:300]})


async def lib_items(meta: dict) -> list:
    lid = meta["id"]
    if lid not in LIB_ITEMS:
        d = json.loads((await bot.download(meta["fid"])).read().decode("utf-8"))
        LIB_ITEMS[lid] = norm_items(d.get("items") if isinstance(d, dict) else d)
    return LIB_ITEMS[lid]


async def api_lib_get(request: web.Request) -> web.Response:
    lid = clip((await read_json(request)).get("id"), 20)
    lib = await lib_load()
    m = next((x for x in lib["sets"] if x.get("id") == lid), None)
    if not m:
        return jerr("Topilmadi", 404)
    try:
        items = await lib_items(m)
    except Exception as e:
        log.warning("lib_get: %s", e)
        return jerr("Yuklab boʻlmadi", 502)
    return web.json_response({"ok": True, "set": {**lib_meta(m), "items": items}})


async def api_lib_play(request: web.Request) -> web.Response:
    global LIB_DIRTY
    lid = clip((await read_json(request)).get("id"), 20)
    lib = await lib_load()
    m = next((x for x in lib["sets"] if x.get("id") == lid), None)
    if m:
        m["plays"] = int(m.get("plays") or 0) + 1
        LIB_DIRTY = True
        stat_inc("lib")
    return web.json_response({"ok": True})


async def api_lib_publish(request: web.Request) -> web.Response:
    data = await read_json(request)
    u = site_user(data)
    if not u:
        return jerr("auth", 401)
    if not LIB_CHAT:
        return jerr("Kutubxona hali ulanmagan (administrator LIBRARY_CHAT_ID ni qoʻshishi kerak).", 503)
    uid = u["u"]
    s = next((x for x in await load_sets(uid) if x["id"] == str(data.get("set_id"))), None)
    if not s:
        return jerr("Toʻplam topilmadi")
    items = norm_items(s["items"])
    if len(items) < (2 if set_kind(items) in ("order", "group") else 4):
        return jerr("Kutubxonaga kamida 4 ta savolli toʻplam qoʻshiladi.")
    name = clip(data.get("name") or s["name"], 60)
    fan, sinf, mavzu = clip(data.get("fan"), 60) or "Matematika", clip(data.get("sinf"), 10), clip(data.get("mavzu"), 100)
    lib = await lib_load()
    if sum(1 for m in lib["sets"] if m.get("uid") == uid) >= 60:
        return jerr("Bitta oʻqituvchi koʻpi bilan 60 ta toʻplam ulasha oladi.")
    if any(m.get("uid") == uid and m.get("src") == s["id"] for m in lib["sets"]):
        return jerr("Bu toʻplam kutubxonada allaqachon bor.")
    try:
        lid = await lib_add(uid, u["n"], s["id"], name, fan, sinf, mavzu, items)
    except Exception as e:
        log.warning("publish: %s", e)
        return jerr("Kanalga yozib boʻlmadi. Bot kanalda administrator ekanini tekshiring.", 502)
    return web.json_response({"ok": True, "id": lid})


def items_sig(items: list) -> str:
    return hashlib.md5(json.dumps(items, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:12]


async def lib_add(uid: int, author: str, src: str, name: str, fan: str, sinf: str, mavzu: str, items: list, auto: bool = False) -> str:
    """Toʻplamni kutubxona kanaliga yozadi va roʻyxatga qoʻshadi (xato boʻlsa — exception)."""
    lib = await lib_load()
    lid = secrets.token_hex(4)
    payload = {"name": name, "fan": fan, "sinf": sinf, "mavzu": mavzu, "author": author, "items": items}
    async with LIB_LOCK:
        doc = await bot.send_document(
            LIB_CHAT, BufferedInputFile(json.dumps(payload, ensure_ascii=False).encode("utf-8"), filename=f"{lid}.json"),
            caption=f"📚 {name}\n{fan}{' · ' + sinf + '-sinf' if sinf else ''} · {len(items)} ta savol\n✍️ {author}"[:1000],
            disable_notification=True)
        lib["sets"].insert(0, {"id": lid, "name": name, "fan": fan, "sinf": sinf, "mavzu": mavzu, "author": author, "uid": uid,
                               "src": src, "n": len(items), "mc": any("o" in it for it in items), "kind": set_kind(items), "t": int(time.time()),
                               "plays": 0, "fid": doc.document.file_id, "mid": doc.message_id, "sig": items_sig(items), "auto": auto})
        LIB_ITEMS[lid] = items
        await lib_save_index()
    stat_inc("pub")
    return lid


# Yangi yaratilgan har bir toʻplam avtomatik kutubxonaga ham tushadi (hammaga koʻrinadi).
# Oʻchirish uchun Render'da AUTO_PUBLISH=0 qoʻyiladi.
AUTO_PUB = os.environ.get("AUTO_PUBLISH", "1").strip() != "0"
AUTO_PER_TEACHER = 60


async def lib_auto(uid: int, s: dict, sinf: str = "", mavzu: str = "") -> None:
    if not LIB_CHAT:
        return
    try:
        items = norm_items(s.get("items"))
        if len(items) < (2 if set_kind(items) in ("order", "group") else 4):
            return
        lib = await lib_load()
        sig = items_sig(items)
        if any(m.get("sig") == sig or (m.get("uid") == uid and m.get("src") == s["id"]) for m in lib["sets"]):
            return   # aynan shu savollar kutubxonada allaqachon bor
        if sum(1 for m in lib["sets"] if m.get("uid") == uid) >= AUTO_PER_TEACHER:
            return
        st = (STAT or {}).get("users", {}).get(str(uid)) or {}
        author = st.get("n") or "Oʻqituvchi"
        await lib_add(uid, author, s["id"], s["name"], s.get("fan") or "Matematika", sinf, mavzu, items, auto=True)
    except Exception as e:
        log.warning("lib_auto: %s", e)


async def lib_unlink(uid: int, sid: str) -> None:
    """Oʻqituvchi toʻplamini oʻchirsa, avtomatik ulashilgan nusxasi ham kutubxonadan olinadi."""
    if not LIB_CHAT:
        return
    try:
        lib = await lib_load()
        gone = [m for m in lib["sets"] if m.get("uid") == uid and m.get("src") == sid and m.get("auto")]
        if not gone:
            return
        async with LIB_LOCK:
            lib["sets"] = [m for m in lib["sets"] if m not in gone]
            for m in gone:
                LIB_ITEMS.pop(m["id"], None)
                try:
                    await bot.delete_message(LIB_CHAT, m["mid"])
                except Exception:
                    pass
            await lib_save_index()
    except Exception as e:
        log.warning("lib_unlink: %s", e)


async def api_lib_delete(request: web.Request) -> web.Response:
    data = await read_json(request)
    u = site_user(data)
    if not u:
        return jerr("auth", 401)
    lib = await lib_load()
    lid = clip(data.get("id"), 20)
    m = next((x for x in lib["sets"] if x.get("id") == lid), None)
    if not m or (m.get("uid") != u["u"] and u["u"] != ADMIN_ID):
        return jerr("Ruxsat yoʻq", 403)
    async with LIB_LOCK:
        lib["sets"] = [x for x in lib["sets"] if x.get("id") != lid]
        LIB_ITEMS.pop(lid, None)
        try:
            await bot.delete_message(LIB_CHAT, m["mid"])
        except Exception:
            pass
        await lib_save_index()
    return web.json_response({"ok": True})


async def api_sets_save(request: web.Request) -> web.Response:
    data = await read_json(request)
    u = site_user(data)
    if not u:
        return jerr("auth", 401)
    items = norm_items(data.get("items"))
    if not items:
        return jerr("Birorta ham toʻgʻri savol topilmadi.")
    s, dropped = await add_set(u["u"], clip(data.get("name"), 60) or "Oʻz savollarim", items, "own", clip(data.get("fan"), 60),
                               sinf=clip(data.get("sinf"), 10), pub=data.get("pub", True) is not False)
    return web.json_response({"ok": True, "set": {"id": s["id"], "name": s["name"], "fan": s.get("fan", ""), "items": s["items"]}, "dropped": dropped})


async def api_sets_delete(request: web.Request) -> web.Response:
    data = await read_json(request)
    u = site_user(data)
    if not u:
        return jerr("auth", 401)
    sid = str(data.get("id", ""))
    async with lock_for(u["u"]):
        sets = await load_sets(u["u"])
        if not any(s["id"] == sid for s in sets):
            return jerr("Topilmadi", 404)
        await save_sets(u["u"], [s for s in sets if s["id"] != sid])
    asyncio.create_task(lib_unlink(u["u"], sid))
    return web.json_response({"ok": True})


MC_PROMPT = """Sen «{fan}» fani oʻqituvchisining yordamchisisan. Sinf: {sinf}. Mavzu: «{topic}».
Shu mavzuda {n} ta QISQA test savoli tuz:
- savol bitta qisqa gap, oʻquvchi 10–20 soniyada javob beradi; diqqat, mantiq va qiziqishni oshirsin;
- har savolda 4 ta qisqa variant (1–4 soʻz), faqat bittasi toʻgʻri, qolganlari ishonarli xato;
- faktlar aniq va xatosiz boʻlsin, sinf darajasiga mos boʻlsin;
- til: {lang}.
Faqat JSON qaytar, har doim BIRINCHI variant — toʻgʻri javob:
{{"name": "toʻplam uchun qisqa nom", "items": [{{"q": "savol", "o": ["toʻgʻri", "xato", "xato", "xato"]}}]}}"""


async def gemini_mc(fan: str, sinf: str, topic: str, lang: str, n: int = 12, extra: str = "", file: dict | None = None) -> tuple[str, list]:
    text = MC_PROMPT.format(fan=fan, sinf=sinf or "koʻrsatilmagan", topic=topic, n=n, lang=lang)
    if extra:
        text += f"\nOʻqituvchining qoʻshimcha istagi: {extra}"
    parts = []
    if file:
        parts.append({"inline_data": file})
        text += "\nIlova qilingan manbaga (rasm yoki PDF) tayanib tuz."
    parts.append({"text": text})
    obj = parse_json_text(await gemini_call([{"role": "user", "parts": parts}], temperature=0.8))
    raw = obj.get("items") if isinstance(obj, dict) else obj
    items = norm_items([{**it, "c": 0} for it in raw if isinstance(it, dict)] if isinstance(raw, list) else [])
    items = [it for it in items if "o" in it and len(it["o"]) == 4]
    return str((obj.get("name") if isinstance(obj, dict) else "") or topic)[:60], items


# ---- yangi oʻyin turlari uchun AI formatlari ----
KIND_FMT = {
    "tf": ("{n} ta QISQA gap (har biri bitta aniq fakt) tuz: taxminan yarmi toʻgʻri, yarmi notoʻgʻri. Notoʻgʻri gaplar ishonarli, "
           "lekin shubhasiz xato boʻlsin; «baʼzan», «koʻpincha» kabi noaniq soʻzlarni ishlatma.\n"
           'JSON: {{"name": "toʻplam nomi", "items": [{{"q": "gap", "t": 1}}]}}  (t: 1 — toʻgʻri, 0 — notoʻgʻri)'),
    "pair": ("{n} ta JUFT tuz: chapda atama, soʻz yoki sana; oʻngda unga mos qisqa javob (taʼrif, tarjima, voqea, belgi) — 1–6 soʻz. "
             "Har bir juft yagona boʻlsin, oʻng tomonlar bir-biriga oʻxshab adashtirmasin.\n"
             'JSON: {{"name": "toʻplam nomi", "items": [{{"a": "chap", "b": "oʻng"}}]}}'),
    "order": ("{n} ta TARTIBGA SOLISH topshirigʻi tuz: har birida 4–6 ta qisqa element (1–6 soʻz) TOʻGʻRI ketma-ketlikda "
              "(xronologiya, jarayon bosqichlari, kattalik tartibi). Tartib aniq va bahssiz boʻlsin; kerak boʻlsa sanani qavsda yoz.\n"
              'JSON: {{"name": "toʻplam nomi", "items": [{{"q": "topshiriq matni", "s": ["birinchi", "ikkinchi", "uchinchi", "toʻrtinchi"]}}]}}'),
    "group": ("{n} ta GURUHLARGA AJRATISH topshirigʻi tuz: har birida 2–3 ta guruh nomi va har guruhga 3–5 tadan qisqa soʻz yoki tushuncha. "
              "Har bir soʻz faqat bitta guruhga shubhasiz tegishli boʻlsin.\n"
              'JSON: {{"name": "toʻplam nomi", "items": [{{"q": "topshiriq", "g": [{{"n": "guruh nomi", "w": ["soʻz", "soʻz", "soʻz"]}}]}}]}}'),
}
KIND_N = {"tf": 14, "pair": 12, "order": 5, "group": 3}
KIND_ALIAS = {"togri": "tf", "juft": "pair", "jlash": "pair", "tartib": "order", "guruh": "group"}


async def gemini_kind(kind: str, fan: str, sinf: str, topic: str, lang: str, extra: str = "", file: dict | None = None) -> tuple[str, list]:
    text = (f"Sen «{fan}» fani oʻqituvchisining yordamchisisan. Sinf: {sinf or 'koʻrsatilmagan'}. Mavzu: «{topic}». "
            f"Sinfda guruh oʻyini uchun material tuz. Faktlar aniq va xatosiz, sinf darajasiga mos boʻlsin. Til: {lang}.\n"
            + KIND_FMT[kind].format(n=KIND_N[kind]) + "\nFaqat JSON qaytar.")
    if extra:
        text += f"\nOʻqituvchining qoʻshimcha istagi: {extra}"
    parts = []
    if file:
        parts.append({"inline_data": file})
        text += "\nIlova qilingan manbaga (rasm yoki PDF) tayanib tuz."
    parts.append({"text": text})
    obj = parse_json_text(await gemini_call([{"role": "user", "parts": parts}], temperature=0.7))
    raw = obj.get("items") if isinstance(obj, dict) else obj
    items = [it for it in norm_items(raw) if item_kind(it) == kind]
    return str((obj.get("name") if isinstance(obj, dict) else "") or topic)[:60], items


# ===================== SAYT: kirish, AI vositalari, chat =====================
SITE_ORIGINS = {o.strip().rstrip("/") for o in os.environ.get(
    "SITE_ORIGINS", "https://bilimkaliti.github.io,https://bilim-kaliti.github.io,https://mashrapovbehruz805-crypto.github.io").split(",") if o.strip()}
SITE_SECRET = hashlib.sha256(b"bk-site:" + TOKEN.encode()).digest()
LOGIN_CODES: dict[str, dict] = {}
LOGIN_TTL = 600
BOT_USERNAME = os.environ.get("BOT_USERNAME", "bilimkaliti_bot")


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def make_token(uid: int, name: str) -> str:
    payload = _b64(json.dumps({"u": uid, "n": name, "e": int(time.time()) + 90 * 86400}).encode())
    sig = hmac.new(SITE_SECRET, payload.encode(), hashlib.sha256).hexdigest()[:40]
    return f"{payload}.{sig}"


def read_token(tok: str) -> dict | None:
    try:
        payload, sig = tok.split(".", 1)
        good = hmac.new(SITE_SECRET, payload.encode(), hashlib.sha256).hexdigest()[:40]
        if not hmac.compare_digest(sig, good):
            return None
        data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        return data if data.get("e", 0) > time.time() else None
    except Exception:
        return None


@web.middleware
async def cors(request: web.Request, handler):
    origin = request.headers.get("Origin", "").rstrip("/")
    is_api = request.path.startswith("/api/")
    if request.method == "OPTIONS" and is_api:
        resp = web.Response(status=204)
    else:
        resp = await handler(request)
    if is_api and origin in SITE_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Max-Age"] = "86400"
        resp.headers["Vary"] = "Origin"
    return resp


async def read_json(request: web.Request) -> dict:
    try:
        data = await request.json()
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def site_user(data: dict) -> dict | None:
    u = read_token(str(data.get("token", "")))
    if u:
        stat_user(u["u"], u.get("n", ""), "", "site")
    return u


def jerr(msg: str, status: int = 400, **kw) -> web.Response:
    return web.json_response({"ok": False, "error": msg, **kw}, status=status)


async def api_ping(request: web.Request) -> web.Response:
    return web.json_response({"ok": True})


async def api_login_start(request: web.Request) -> web.Response:
    now = time.time()
    for c in [c for c, r in LOGIN_CODES.items() if now - r["t"] > LOGIN_TTL]:
        LOGIN_CODES.pop(c, None)
    if len(LOGIN_CODES) > 5000:
        return jerr("busy", 429)
    code = secrets.token_urlsafe(12)
    LOGIN_CODES[code] = {"t": now}
    return web.json_response({"ok": True, "code": code, "url": f"https://t.me/{BOT_USERNAME}?start=login_{code}"})


async def api_login_check(request: web.Request) -> web.Response:
    code = str((await read_json(request)).get("code", ""))
    rec = LOGIN_CODES.get(code)
    if not rec or time.time() - rec["t"] > LOGIN_TTL:
        LOGIN_CODES.pop(code, None)
        return web.json_response({"ok": False, "expired": True})
    if "uid" not in rec:
        return web.json_response({"ok": False, "wait": True})
    LOGIN_CODES.pop(code, None)
    return web.json_response({"ok": True, "token": make_token(rec["uid"], rec["name"]), "name": rec["name"]})


async def api_me(request: web.Request) -> web.Response:
    u = site_user(await read_json(request))
    if not u:
        return jerr("auth", 401)
    return web.json_response({"ok": True, "name": u["n"], "gen": ai_left(u["u"]), "chat": ai_left(u["u"], "chat"),
                              "admin": bool(ADMIN_ID and u["u"] == ADMIN_ID)})


async def gemini_call(contents: list, system: str | None = None, json_out: bool = True,
                      max_tokens: int = 8192, temperature: float = 0.8) -> str:
    timeout = aiohttp.ClientTimeout(total=150)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        model = await gemini_model(session)
        cfg = {"temperature": temperature, "maxOutputTokens": max_tokens}
        if json_out:
            cfg["responseMimeType"] = "application/json"
        body = {"contents": contents, "generationConfig": cfg}
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        async with session.post(f"{GEM_API}/{model}:generateContent", json=body,
                                headers={"x-goog-api-key": GEMINI_KEY}) as r:
            if r.status == 429:
                raise RuntimeError("limit")
            if r.status == 404:
                global _MODEL
                _MODEL = None
            data = await r.json(content_type=None)
            if r.status != 200:
                raise RuntimeError(f"http {r.status}: {str(data)[:300]}")
    cand = (data.get("candidates") or [{}])[0]
    parts = (cand.get("content") or {}).get("parts") or []
    text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
    if not text:
        raise RuntimeError("empty: " + str(cand.get("finishReason")))
    return text


def parse_json_text(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        text = text.rsplit("```", 1)[0]
    try:
        return json.loads(text)
    except Exception:
        a, b = text.find("{"), text.rfind("}")
        return json.loads(text[a:b + 1])


LANGS = {"uz": "oʻzbek tili, lotin yozuvi (oʻ, gʻ harflari bilan)", "ru": "rus tili", "en": "ingliz tili"}

TOOL_PROMPTS = {
    "test": ("{n} ta test savoli tuz. Qiyinligi: {qiyinlik}. Har savolda 4 ta javob varianti, faqat bittasi toʻgʻri; "
             "toʻgʻri javob oʻrni har xil boʻlsin; har biriga qisqa izoh yoz.\n"
             'JSON: {{"title": "...", "items": [{{"q": "savol", "options": ["A", "B", "C", "D"], "correct": 0, "explain": "..."}}]}}'),
    "krossvord": ("Krossvord uchun {n} ta soʻz va topishmoq (savol) tuz. Har bir soʻz — BITTA soʻz, 3–12 harf, "
                  "boʻsh joy, raqam va chiziqchasiz; asosiy atamalar boʻlsin; savollar qisqa va aniq.\n"
                  'JSON: {{"title": "...", "words": [{{"word": "SOʻZ", "clue": "savol"}}]}}'),
    "fleshkarta": ("{n} ta fleshkarta tuz: old tomonida savol yoki atama, orqa tomonida qisqa javob yoki taʼrif.\n"
                   'JSON: {{"title": "...", "cards": [{{"front": "...", "back": "..."}}]}}'),
    "glossariy": ("Mavzu boʻyicha {n} ta asosiy atamadan iborat glossariy tuz: atama, aniq taʼrif va qisqa misol.\n"
                  'JSON: {{"title": "...", "items": [{{"term": "...", "def": "...", "example": "..."}}]}}'),
    "tarqatma": ("Oʻquvchilar uchun tarqatma material tuz: qisqa kirish, 2–4 ta boʻlimda asosiy nazariya (sodda tilda), "
                 "3 ta yechilgan namuna va {n} ta mustaqil mashq (javoblari bilan).\n"
                 'JSON: {{"title": "...", "intro": "...", "sections": [{{"h": "...", "text": "..."}}], '
                 '"examples": [{{"q": "...", "a": "yechim"}}], "exercises": [{{"q": "...", "a": "javob"}}]}}'),
    "dars": ("{vaqt} daqiqalik dars ishlanma tuz (Oʻzbekiston maktablari uchun odatiy shaklda). Dars turi, metodlar, "
             "jihozlar, uch maqsad (taʼlimiy, tarbiyaviy, rivojlantiruvchi), darsning borishi bosqichlari "
             "(tashkiliy qism, uy vazifasini soʻrash, yangi mavzu bayoni, mustahkamlash, baholash, uyga vazifa) — "
             "har bosqichda vaqt, oʻqituvchi faoliyati va oʻquvchi faoliyati; kamida bitta interaktiv metod yoki oʻyin.\n"
             'JSON: {{"title": "...", "meta": {{"turi": "...", "metodlar": "...", "jihozlar": "..."}}, '
             '"goals": {{"talimiy": "...", "tarbiyaviy": "...", "rivojlantiruvchi": "..."}}, '
             '"stages": [{{"name": "...", "time": "5 daqiqa", "teacher": "...", "students": "..."}}], '
             '"homework": "...", "assessment": "..."}}'),
    "ishreja": ("Kalendar-tematik ish reja tuz: {davr}, haftasiga {soat} soat. Oʻzbekiston davlat taʼlim standarti va "
                "oʻquv dasturiga imkon qadar mos boʻlsin; mavzular mantiqiy ketma-ketlikda, takrorlash va nazorat "
                "ishlari bilan.\n"
                'JSON: {{"title": "...", "rows": [{{"n": 1, "topic": "...", "hours": 1, "type": "yangi mavzu / mustahkamlash / nazorat"}}], '
                '"notes": "..."}}'),
    "metodik": ("Oʻqituvchilar uchun metodik qoʻllanma tuz: mavzuni oʻqitishning maqsadi, asosiy tushunchalar, "
                "oʻqitish usullari va bosqichlari, oʻquvchilar koʻp qiladigan xatolar, interaktiv metodlar va oʻyinlar, "
                "baholash. 5–8 ta boʻlim.\n"
                'JSON: {{"title": "...", "sections": [{{"h": "...", "paras": ["..."], "bullets": ["..."]}}]}}'),
    "taqdimot": ("{n} ta slayddan iborat dars taqdimoti tuz. Har slaydda qisqa sarlavha, 3–5 ta qisqa band "
                 "(har biri 12 soʻzdan oshmasin), mos bitta emoji va oʻqituvchi uchun izoh. Birinchi slayd — kirish, "
                 "oxirgisi — xulosa yoki savollar.\n"
                 'JSON: {{"title": "...", "subtitle": "...", "slides": [{{"title": "...", "bullets": ["..."], "emoji": "📐", "note": "..."}}]}}'),
}
TOOL_LIMITS = {"test": (5, 30, 10), "krossvord": (6, 20, 12), "fleshkarta": (6, 30, 12), "glossariy": (6, 40, 15),
               "tarqatma": (3, 15, 6), "taqdimot": (5, 20, 10)}


def clip(v, n: int = 300) -> str:
    return str(v or "").strip()[:n]


async def api_ai(request: web.Request) -> web.Response:
    data = await read_json(request)
    u = site_user(data)
    if not u:
        return jerr("auth", 401)
    if not GEMINI_KEY:
        return jerr("AI hali ulanmagan (GEMINI_API_KEY yoʻq).", 503)
    uid, tool, p = u["u"], str(data.get("tool", "")), data.get("p") or {}
    if tool != "savollar" and tool not in TOOL_PROMPTS:
        return jerr("tool")
    if ai_left(uid) <= 0:
        return jerr("Bugungi AI limit tugadi. Ertaga yana urinib koʻring.", 429, limit=True)
    mavzu = clip(p.get("mavzu"), 300)
    if len(mavzu) < 2:
        return jerr("Mavzuni yozing.")
    sinf, fan = clip(p.get("sinf"), 30), clip(p.get("fan"), 60) or "Matematika"
    ai_use(uid)
    stat_inc("ai_t", sub="tools", name=tool)
    try:
        kind = KIND_ALIAS.get(str(p.get("tur") or ""), str(p.get("tur") or ""))
        if tool == "savollar" and kind in KIND_FMT:
            f = data.get("file")
            fobj = {"mime_type": str(f["mime"]), "data": str(f["data"])} if isinstance(f, dict) and f.get("data") else None
            name, items = await gemini_kind(kind, fan, sinf, mavzu, LANGS.get(str(p.get("til")), LANGS["uz"]), clip(p.get("extra"), 600), fobj)
            if len(items) < (2 if kind in ("order", "group") else 4):
                return jerr("AI yetarlicha material tuza olmadi. Mavzuni boshqacharoq yozing.")
            s, _ = await add_set(uid, name, items, "ai", fan, sinf=re.sub(r"\D", "", sinf)[:2], mavzu=mavzu[:100])
            return web.json_response({"ok": True, "result": {"title": s["name"], "set": s}, "left": ai_left(uid)})
        if tool == "savollar" and (fan.lower() not in MATH_FANS or str(p.get("tur")) == "mc"):
            f = data.get("file")
            fobj = {"mime_type": str(f["mime"]), "data": str(f["data"])} if isinstance(f, dict) and f.get("data") else None
            name, items = await gemini_mc(fan, sinf, mavzu, LANGS.get(str(p.get("til")), LANGS["uz"]), 12, clip(p.get("extra"), 600), fobj)
            if len(items) < 4:
                return jerr("AI yetarlicha toʻgʻri savol tuza olmadi. Mavzuni boshqacharoq yozing.")
            s, _ = await add_set(uid, name, items, "ai", fan, sinf=re.sub(r"\D", "", sinf)[:2], mavzu=mavzu[:100])
            return web.json_response({"ok": True, "result": {"title": s["name"], "set": s}, "left": ai_left(uid)})
        if tool == "savollar":
            name, items = await gemini_questions(f"{sinf}-sinf, {mavzu}" if sinf else mavzu)
            if len(items) < 4:
                return jerr("AI yetarlicha toʻgʻri savol tuza olmadi. Mavzuni boshqacharoq yozing.")
            s, _ = await add_set(uid, name, items, "ai", fan, sinf=re.sub(r"\D", "", sinf)[:2], mavzu=mavzu[:100])
            return web.json_response({"ok": True, "result": {"title": s["name"], "set": s}, "left": ai_left(uid)})
        lo, hi, df = TOOL_LIMITS.get(tool, (1, 50, 10))
        try:
            n = max(lo, min(hi, int(p.get("n") or df)))
        except (TypeError, ValueError):
            n = df
        fmt = {"n": n, "qiyinlik": clip(p.get("qiyinlik"), 20) or "oʻrta", "vaqt": clip(p.get("vaqt"), 5) or "45",
               "davr": clip(p.get("davr"), 40) or "bir yillik", "soat": clip(p.get("soat"), 3) or "5"}
        lang = LANGS.get(str(p.get("til")), LANGS["uz"])
        head = (f"Sen tajribali oʻqituvchi-metodistsan. Fan: {fan}. Sinf: {sinf or 'koʻrsatilmagan'}. "
                f"Mavzu: «{mavzu}». Til: {lang}. Mazmun yoshga mos, aniq va xatosiz boʻlsin; "
                "matematik ifodalarni oddiy matnda yoz (masalan 3/4, x², √9).\n")
        extra = clip(p.get("extra"), 600)
        if extra:
            head += f"Oʻqituvchining qoʻshimcha istagi: {extra}\n"
        parts = []
        f = data.get("file")
        if isinstance(f, dict) and f.get("data") and str(f.get("mime", "")).split("/")[0] in ("image", "application"):
            parts.append({"inline_data": {"mime_type": str(f["mime"]), "data": str(f["data"])}})
            head += "Ilova qilingan manbaga (rasm yoki PDF) tayanib tuz.\n"
        parts.append({"text": head + TOOL_PROMPTS[tool].format(**fmt) + "\nFaqat JSON qaytar."})
        text = await gemini_call([{"role": "user", "parts": parts}])
        result = parse_json_text(text)
        if not isinstance(result, dict):
            raise ValueError("not object")
        return web.json_response({"ok": True, "result": result, "left": ai_left(uid)})
    except RuntimeError as e:
        log.warning("api_ai %s: %s", tool, e)
        if str(e) == "limit":
            return jerr("AI hozir band (bepul limit). Bir daqiqadan keyin urinib koʻring.", 429)
        return jerr("AI javob bermadi. Birozdan keyin yana urinib koʻring.", 502)
    except Exception as e:
        log.warning("api_ai parse %s: %s", tool, e)
        return jerr("AI javobini oʻqib boʻlmadi. Yana bir bor urinib koʻring.", 502)


DARSLIK_PROMPT = """Sen tajribali {fan} oʻqituvchisisan. Ilova qilingan darslik sahifalari / PDF / Word matni asosida sinfda guruh oʻyini uchun savollar tuz.
Sinf: {sinf}. {mavzu_line}{pages_line}
Qoidalar:
- FAQAT manbadagi maʼlumotga tayan: matn, qoidalar, misollar, jadval va rasmlardan foydalan; manbada yoʻq faktni qoʻshma;
- avval manba nima haqida ekanini aniqla (mavzu nomi); agar manba tayyor test boʻlsa (raqamlangan savollar va A/B/C/D variantlar), JSONga "test": true qoʻsh;
- savollar QISQA (1–2 gap), oʻquvchi 10–30 soniyada javob beradi; diqqat, tushunish va mantiqni tekshirsin, qiyinligi asta-sekin oshsin;
- savollar takrorlanmasin, manbaning turli qismlarini qamrasin;
- qiyinlik: {qiyin};
- til: {lang}.
{fmt}
Faqat JSON qaytar."""

DARSLIK_MC = """{n} ta TEST savoli: har birida 4 ta qisqa variant (1–5 soʻz), faqat bittasi toʻgʻri, xatolari ishonarli. BIRINCHI variant har doim toʻgʻri javob.
JSON: {{"name": "toʻplam uchun qisqa nom", "mavzu": "aniqlangan mavzu", "izoh": "manba haqida bitta gap", "items": [{{"q": "savol", "o": ["toʻgʻri", "xato", "xato", "xato"]}}]}}"""

DARSLIK_NUM = """{n} ta SON-JAVOBLI savol: javob har doim BUTUN SON 0–999 (kasr, manfiy, birlik yoʻq). Manbadagi misol va masalalarga oʻxshash, lekin sonlari boshqa boʻlsin.
Har bir savolga "expr" — javobni hisoblaydigan arifmetik ifoda yoz (faqat raqamlar, + - * / // % ** va qavslar).
JSON: {{"name": "toʻplam uchun qisqa nom", "mavzu": "aniqlangan mavzu", "izoh": "manba haqida bitta gap", "items": [{{"q": "savol", "a": 18, "expr": "(36/4)*2"}}]}}"""

DARSLIK_MAX_FILES = 6

TEST_EXTRACT_PROMPT = """Ilova qilingan fayl(lar)da TAYYOR TEST bor. Vazifang — testni HECH NIMANI OʻZGARTIRMASDAN koʻchirib olish.
{pages_line}Qoidalar:
- savol matni va har bir variantni HARFMA-HARF AYNAN koʻchir: soʻz, imlo, tinish belgisi, son, formula — hammasi asl holicha; tahrirlama, qisqartirma, tarjima qilma, tuzatma;
- savollar va variantlar tartibini saqla; savol raqamini ("1.", "12)") va variant harflarini ("A)", "b.", "C)") olib tashla — faqat matnning oʻzi qolsin;
- formulani oddiy matn bilan yoz (x², √, ½ kabi belgilar bilan), maʼnosi oʻzgarmasin;
- toʻgʻri javob: faylda javoblar kaliti yoki belgilangan javob boʻlsa, FAQAT undan ol va "k": "kalit" yoz; kalit boʻlmasa, savolni oʻzing yech va "k": "ai" yoz;
- savol rasm yoki chizmasiz tushunarsiz boʻlsa, uni ham koʻchir va "rasm": true qoʻsh;
- test boʻlmagan matnni (sarlavha, koʻrsatma) savolga aylantirma; yangi savol qoʻshma;
- {dan_line}eng koʻpi 60 ta savol koʻchir; testda bulardan keyin yana savol qolsa "davomi": true yoz;
- "n" — savolning testdagi asl raqami (boʻlmasa tartib raqami).
{kalit_line}JSON: {{"name": "test nomi (faylda boʻlsa — aynan)", "mavzu": "test mavzusi", "kalit": true, "davomi": false, "items": [{{"n": 1, "q": "savol matni", "o": ["A varianti", "B varianti", "C varianti", "D varianti"], "c": 0, "k": "kalit"}}]}}
"c" — toʻgʻri variantning tartib raqami (0 dan); "kalit" — faylda javoblar kaliti bor-yoʻqligi. Faqat JSON qaytar."""

CHECK_PROMPT = """Quyidagi test savollarini mustaqil yech. Har bir savol uchun toʻgʻri variantning tartib raqamini (0 dan) yoz.
Ishonching komil boʻlmasa ham eng toʻgʻri deb bilganingni tanla.
JSON: {{"a": [0, 2, 1]}} — roppa-rosa {n} ta son, savollar tartibida. Faqat JSON qaytar.

{qs}"""

_LET = {**{ch: i for i, ch in enumerate("ABCDEF")}, **{ch: i for i, ch in enumerate("АБВГДЕ")}}


def parse_key(text: str) -> dict:
    """«1-B, 2) a, 3.D» yoki «1B 2A» -> {1: 1, 2: 0, 3: 3}."""
    out = {}
    for m in re.finditer(r"(\d{1,3})\s*[-–—.):=]?\s*([A-Fa-fА-Еа-е])(?![A-Za-zА-Яа-яʻ’'])", str(text or "")):
        out[int(m.group(1))] = _LET[m.group(2).upper()]
    return out


def norm_test(raw, key: dict | None = None) -> tuple[list[dict], dict]:
    """Tayyor testni oʻzgartirmasdan oʻyin formatiga oʻtkazadi (4 variant). key: {savol raqami: variant}."""
    out, info = [], {"ai": 0, "rasm": 0, "kesildi": 0, "tashlandi": 0, "qolda": 0, "aiidx": [], "rasmidx": []}
    for it in raw if isinstance(raw, list) else []:
        if not isinstance(it, dict):
            continue
        q = str(it.get("q") or "").strip()[:600]
        o = [str(x).strip()[:200] for x in (it.get("o") or []) if str(x).strip()] if isinstance(it.get("o"), list) else []
        try:
            c = int(it.get("c", -1))
        except (TypeError, ValueError):
            c = -1
        try:
            num = int(it.get("n"))
        except (TypeError, ValueError):
            num = None
        k = str(it.get("k"))
        if key and num in key and key[num] < len(o):
            c, k = key[num], "qolda"
        if not q or len(o) < 4 or not 0 <= c < len(o) or len(set(o)) != len(o):
            info["tashlandi"] += 1
            continue
        if len(o) > 4:
            keep = sorted([c] + [i for i in range(len(o)) if i != c][:3])
            c, o = keep.index(c), [o[i] for i in keep]
            info["kesildi"] += 1
        if k == "qolda":
            info["qolda"] += 1
        elif k != "kalit":
            info["ai"] += 1
            info["aiidx"].append(len(out))
        if it.get("rasm") in (True, 1, "true"):
            info["rasm"] += 1
            info["rasmidx"].append(len(out))
        out.append({"q": q, "o": o, "c": c})
    return out[:MAX_ITEMS], info


async def darslik_test(uid, parts: list, p: dict) -> web.Response:
    pages = clip(p.get("betlar"), 40)
    key = parse_key(clip(p.get("kalit"), 3000))
    kalit_line = ("Oʻqituvchi javoblar kalitini alohida berdi — toʻgʻri javobni oʻzing aniqlama, \"k\": \"kalit\" yoz: "
                  + ", ".join(f"{n}-{'ABCDEF'[v]}" for n, v in sorted(key.items())) + "\n") if key else ""
    try:
        dan = max(1, min(999, int(p.get("dan") or 1)))
    except (TypeError, ValueError):
        dan = 1
    parts.append({"text": TEST_EXTRACT_PROMPT.format(pages_line=f"PDFdan faqat shu betlarni oʻqi: {pages}.\n" if pages else "",
                                                     kalit_line=kalit_line,
                                                     dan_line=f"faqat {dan}-savoldan boshlab koʻchir, undan oldingilarini tashla; " if dan > 1 else "")})
    ai_use(uid)
    stat_inc("pdf", sub="tools", name="tayyor-test")
    try:
        obj = parse_json_text(await gemini_call([{"role": "user", "parts": parts}], temperature=0.1, max_tokens=16384))
    except RuntimeError as e:
        log.warning("test: %s", e)
        if str(e) == "limit":
            return jerr("AI hozir band (bepul limit). Bir daqiqadan keyin urinib koʻring.", 429)
        if "http 400" in str(e):
            return jerr("AI faylni oʻqiy olmadi. Rasm aniqroq boʻlsin yoki PDF hajmini kamaytiring.", 400)
        return jerr("AI javob bermadi. Birozdan keyin yana urinib koʻring.", 502)
    except Exception as e:
        log.warning("test parse: %s", e)
        return jerr("AI javobini oʻqib boʻlmadi. Yana bir bor urinib koʻring.", 502)
    if isinstance(obj, list):
        obj = {"items": obj}
    raw_items = obj.get("items") if isinstance(obj, dict) else None
    nums = [int(x["n"]) for x in raw_items or [] if isinstance(x, dict) and str(x.get("n", "")).isdigit()]
    items, info = norm_test(raw_items, key)
    info["oxirgi"] = max(nums) if nums else dan - 1 + len(raw_items or [])
    info["davomi"] = bool(obj.get("davomi")) or len(raw_items or []) > MAX_ITEMS
    if len(items) < 2:
        return jerr("Faylda 4 variantli test topilmadi. Test aniq koʻrinadigan rasm yoki PDF yuklang.")
    info["shubha"], info["tekshirildi"] = [], False
    idx = info["aiidx"]
    if idx and ai_left(uid) > 0:
        qs = "\n\n".join(f"{j + 1}. {items[i]['q']}\n" + "\n".join(f"  {v}) {x}" for v, x in enumerate(items[i]["o"])) for j, i in enumerate(idx))
        try:
            ai_use(uid)
            chk = parse_json_text(await gemini_call([{"role": "user", "parts": [{"text": CHECK_PROMPT.format(n=len(idx), qs=qs)}]}],
                                                    temperature=0.1))
            arr = chk.get("a") if isinstance(chk, dict) else chk
            if isinstance(arr, list) and len(arr) == len(idx):
                info["tekshirildi"] = True
                for i, a in zip(idx, arr):
                    try:
                        if int(a) != items[i]["c"]:
                            info["shubha"].append(i)
                    except (TypeError, ValueError):
                        info["shubha"].append(i)
        except Exception as e:
            log.warning("test check: %s", e)
    return web.json_response({"ok": True, "left": ai_left(uid), "tur": "mc", "manba": "test", "info": info,
                              "name": clip(obj.get("name"), 60) or clip(obj.get("mavzu"), 60) or "Tayyor test",
                              "mavzu": clip(obj.get("mavzu"), 120), "izoh": "", "items": items})


async def api_darslik(request: web.Request) -> web.Response:
    """Darslik sahifasi rasmi yoki PDF -> AI savollar (saqlanmaydi: oʻqituvchi tahrirlab saqlaydi)."""
    data = await read_json(request)
    u = site_user(data)
    if not u:
        return jerr("auth", 401)
    if not GEMINI_KEY:
        return jerr("AI hali ulanmagan (GEMINI_API_KEY yoʻq).", 503)
    uid, p = u["u"], data.get("p") or {}
    files = [f for f in (data.get("files") or []) if isinstance(f, dict) and f.get("data")][:DARSLIK_MAX_FILES]
    parts = []
    for f in files:
        mime = str(f.get("mime", ""))
        if mime == "application/pdf" or mime.startswith("image/"):
            parts.append({"inline_data": {"mime_type": mime, "data": str(f["data"])}})
    matn = str(p.get("matn") or "").strip()[:60000]
    if matn:
        parts.append({"text": "Manba — Word hujjatidagi matn (rasmlar alohida ilova qilingan boʻlishi mumkin):\n<<<\n" + matn + "\n>>>"})
    if not parts:
        return jerr("Darslik sahifasining rasmini, PDF yoki Word faylni yuklang.")
    if ai_left(uid) <= 0:
        return jerr("Bugungi AI limit tugadi. Ertaga yana urinib koʻring.", 429, limit=True)
    if str(p.get("manba")) == "test":
        return await darslik_test(uid, parts, p)
    fan = clip(p.get("fan"), 60) or "Matematika"
    sinf = clip(p.get("sinf"), 10)
    tur = KIND_ALIAS.get(str(p.get("tur") or "auto"), str(p.get("tur") or "auto"))
    if tur not in ("mc", "num") and tur not in KIND_FMT:
        tur = "num" if fan.lower() in MATH_FANS else "mc"
    try:
        n = max(6, min(30, int(p.get("n") or 12)))
    except (TypeError, ValueError):
        n = 12
    mavzu, pages, extra = clip(p.get("mavzu"), 200), clip(p.get("betlar"), 40), clip(p.get("extra"), 500)
    text = DARSLIK_PROMPT.format(
        fan=fan, sinf=sinf or "koʻrsatilmagan", qiyin={"1": "oson", "3": "qiyin"}.get(str(p.get("qiyin")), "oʻrta"),
        mavzu_line=f"Oʻqituvchi koʻrsatgan mavzu: «{mavzu}». " if mavzu else "",
        pages_line=f"PDFdan faqat shu betlardan foydalan: {pages}. " if pages else "",
        lang=LANGS.get(str(p.get("til")), LANGS["uz"]),
        fmt=(DARSLIK_MC.format(n=n) if tur == "mc" else DARSLIK_NUM.format(n=n) if tur == "num"
             else KIND_FMT[tur].format(n=max(2, min(KIND_N[tur] * 2, n if tur in ("tf", "pair") else KIND_N[tur])))))
    if extra:
        text += f"\nOʻqituvchining qoʻshimcha istagi: {extra}"
    parts.append({"text": text})
    ai_use(uid)
    stat_inc("pdf", sub="tools", name="darslik")
    try:
        obj = parse_json_text(await gemini_call([{"role": "user", "parts": parts}], temperature=0.6))
    except RuntimeError as e:
        log.warning("darslik: %s", e)
        if str(e) == "limit":
            return jerr("AI hozir band (bepul limit). Bir daqiqadan keyin urinib koʻring.", 429)
        if "http 400" in str(e):
            return jerr("AI faylni oʻqiy olmadi. Rasm aniqroq boʻlsin yoki PDF hajmini kamaytiring.", 400)
        return jerr("AI javob bermadi. Birozdan keyin yana urinib koʻring.", 502)
    except Exception as e:
        log.warning("darslik parse: %s", e)
        return jerr("AI javobini oʻqib boʻlmadi. Yana bir bor urinib koʻring.", 502)
    if isinstance(obj, list):
        obj = {"items": obj}
    raw = obj.get("items") if isinstance(obj, dict) else None
    if tur == "num":
        items = check_items(raw)
    elif tur in KIND_FMT:
        items = [it for it in norm_items(raw) if item_kind(it) == tur]
    else:
        items = [it for it in norm_items([{**it, "c": 0} for it in raw if isinstance(it, dict)] if isinstance(raw, list) else [])
                 if len(it.get("o", [])) == 4]
    if len(items) < (2 if tur in ("order", "group") else 3):
        return jerr("Manbadan yetarlicha savol tuzib boʻlmadi. Sahifa aniqroq tushgan rasmni yuklang yoki boshqa savol turini tanlang.")
    return web.json_response({"ok": True, "left": ai_left(uid), "tur": tur,
                              "name": clip(obj.get("name"), 60) or clip(obj.get("mavzu"), 60) or "Darslikdan savollar",
                              "mavzu": clip(obj.get("mavzu"), 120), "izoh": clip(obj.get("izoh"), 300), "items": items[:n],
                              "testga": obj.get("test") in (True, 1, "true")})


CHAT_SYSTEM = ("Sen «Bilim Kaliti» saytidagi oʻqituvchilar yordamchisisan. Oʻqituvchiga dars rejalash, mavzuni "
               "tushuntirish usullari, misol va masalalar, oʻyin va interaktiv metodlar, baholash, ota-onalar bilan "
               "muloqot kabi ishlarda amaliy yordam berasan. Odatda oʻzbek tilida (lotin yozuvi) javob ber; "
               "foydalanuvchi boshqa tilda yozsa, oʻsha tilda javob ber. Javoblar aniq, qisqa va tartibli boʻlsin "
               "(markdown: sarlavha, roʻyxat, qalin). Bilmagan narsangni toʻqima.")


async def api_chat(request: web.Request) -> web.Response:
    data = await read_json(request)
    u = site_user(data)
    if not u:
        return jerr("auth", 401)
    if not GEMINI_KEY:
        return jerr("AI hali ulanmagan (GEMINI_API_KEY yoʻq).", 503)
    if ai_left(u["u"], "chat") <= 0:
        return jerr("Bugungi chat limiti tugadi. Ertaga yana urinib koʻring.", 429, limit=True)
    msgs = [m for m in (data.get("messages") or []) if isinstance(m, dict)][-14:]
    contents = []
    for m in msgs:
        role = "model" if m.get("role") == "model" else "user"
        txt = clip(m.get("text"), 6000)
        if txt:
            contents.append({"role": role, "parts": [{"text": txt}]})
    if not contents or contents[-1]["role"] != "user":
        return jerr("empty")
    f = data.get("file")
    if isinstance(f, dict) and f.get("data"):
        contents[-1]["parts"].insert(0, {"inline_data": {"mime_type": str(f.get("mime")), "data": str(f["data"])}})
    ai_use(u["u"], "chat")
    try:
        text = await gemini_call(contents, system=CHAT_SYSTEM, json_out=False, max_tokens=4096, temperature=0.7)
    except RuntimeError as e:
        log.warning("chat: %s", e)
        return jerr("AI hozir band. Bir daqiqadan keyin urinib koʻring." if str(e) == "limit"
                    else "AI javob bermadi. Birozdan keyin urinib koʻring.", 502)
    return web.json_response({"ok": True, "text": text, "left": ai_left(u["u"], "chat")})


async def api_send(request: web.Request) -> web.Response:
    data = await read_json(request)
    u = site_user(data)
    if not u:
        return jerr("auth", 401)
    html = str(data.get("html", ""))[:3_000_000]
    name = re.sub(r"[^\w\-. ]+", "", str(data.get("name", "hujjat")), flags=re.U).strip()[:60] or "hujjat"
    try:
        await bot.send_document(u["u"], BufferedInputFile(html.encode("utf-8"), filename=name + ".doc"),
                                caption=f"📄 {name}\nWord yoki brauzerda ochiladi. (Bilim Kaliti sayti)")
    except Exception as e:
        log.warning("send: %s", e)
        return jerr("Yuborib boʻlmadi. Botni bloklamaganingizni tekshiring.", 502)
    return web.json_response({"ok": True})


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
    if data.get("kind") != "report":  # hisobot javoblar kalitini almashtirmaydi
        KEYS[user["id"]] = (text, time.time())
    if data.get("notify"):
        try:
            await bot.send_message(user["id"], text)
        except Exception as e:  # foydalanuvchi botni bloklagan bo'lishi mumkin
            log.warning("send failed: %s", e)
    return web.json_response({"ok": True})


async def api_sets(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"ok": False}, status=400)
    user = check_init_data(str(data.get("initData", ""))) if data.get("initData") else None
    if not user and data.get("token"):
        t = read_token(str(data["token"]))
        user = {"id": t["u"]} if t else None
    if not user or "id" not in user:
        return web.json_response({"ok": False}, status=403)
    sets = await load_sets(int(user["id"]))
    return web.json_response({"ok": True, "sets": [{"id": s["id"], "name": s["name"], "fan": s.get("fan", ""), "items": s["items"]} for s in sets]})


SITE_INDEX = Path(__file__).parent / "index.html"


async def index(request: web.Request) -> web.StreamResponse:
    # Sayt bosh sahifasi (GitHub Pages bilan bir xil fayl); bo'lmasa oddiy javob.
    if SITE_INDEX.exists():
        return web.FileResponse(SITE_INDEX, headers={"Cache-Control": "no-cache"})
    return web.Response(text="Bilim Kaliti bot ishlayapti.")


BOT_SHORT = "Sinf uchun guruh oʻyinlari, Robo raqib va AI yordamchi — bepul. Sayt: " + SITE_URL.replace("https://", "").rstrip("/")
BOT_DESC = ("🔑 Bilim Kaliti — oʻqituvchilar uchun bepul yordamchi:\n\n"
            "🎮 Elektron doskada 2–4 guruh bellashadigan 20 ta oʻyin\n"
            "🤖 Robo bilan bellashuv va yakka mashq\n"
            "✨ AI: test, taqdimot, dars ishlanma, krossvord\n"
            "📚 Matematika va boshqa fanlar boʻyicha kutubxona\n\n"
            f"🌐 Sayt: {SITE_URL}\n📢 Kanal: @bilimkaliti_uz\n\nBoshlash uchun START ni bosing.")


async def bot_profile() -> None:
    """Bot tavsifi, buyruqlar va «🌐 Sayt» menyu tugmasi (har ishga tushganda yangilanadi)."""
    for call in (lambda: bot.set_my_short_description(short_description=BOT_SHORT[:120]),
                 lambda: bot.set_my_description(description=BOT_DESC[:512]),
                 lambda: bot.set_my_commands([BotCommand(command="start", description="Bosh menyu"),
                                              BotCommand(command="sayt", description="Saytni ochish"),
                                              BotCommand(command="id", description="Telegram ID raqamim")]),
                 lambda: bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="🌐 Sayt", web_app=WebAppInfo(url=SITE_URL)))):
        try:
            await call()
        except Exception as e:
            log.warning("bot_profile: %s", e)


async def on_startup(app: web.Application) -> None:
    asyncio.create_task(bot_profile())
    if not BASE_URL:
        log.error("BASE_URL topilmadi: webhook oʻrnatilmadi.")
        return
    url = BASE_URL + WEBHOOK_PATH
    # Uyqudan uyg'onganda kelgan xabarlar yo'qolmasin: navbatdagi xabarlar o'chirilmaydi.
    try:
        info = await bot.get_webhook_info()
        if info.url == url:
            log.info("Webhook joyida, kutilayotgan xabarlar: %s", info.pending_update_count)
            return
    except Exception as e:
        log.warning("get_webhook_info: %s", e)
    await bot.set_webhook(url)
    log.info("Webhook oʻrnatildi: %s", BASE_URL)


# ===================== KUN JUMBOGʻI (har kuni kanalga) =====================
# Har kuni ertalab bitta mantiqiy savol kanalga «viktorina» (quiz) koʻrinishida joylanadi
# va saytning bosh sahifasida ham chiqadi. Render uxlab qolsa, GitHub Actions uni uygʻotadi
# (.github/workflows/kun-jumbogi.yml). Bir kunda faqat bitta jumboq chiqadi.
DAILY_CHANNEL = os.environ.get("DAILY_CHANNEL", "@bilimkaliti_uz").strip()
DAILY_HOUR = int(os.environ.get("DAILY_HOUR", "7") or 7)   # Toshkent vaqti bilan, shu soatdan keyin
DAILY_LOCK = asyncio.Lock()
UZ_MONTHS = ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr"]


def _tash_now() -> datetime.datetime:
    return datetime.datetime.utcnow() + datetime.timedelta(hours=5)


def _uz_date(d: str) -> str:
    try:
        y, m, dd = (int(x) for x in d.split("-"))
        return f"{dd}-{UZ_MONTHS[m - 1]}"
    except Exception:
        return d


def valid_puzzle(p) -> dict | None:
    if not isinstance(p, dict):
        return None
    q = str(p.get("q", "")).strip()
    o = [str(x).strip()[:100] for x in (p.get("o") or []) if str(x).strip()] if isinstance(p.get("o"), list) else []
    try:
        a = int(p.get("a"))
    except (TypeError, ValueError):
        return None
    e = str(p.get("e", "")).strip()
    if not (10 <= len(q) <= 260) or len(o) != 4 or len(set(o)) != 4 or not 0 <= a < 4:
        return None
    return {"q": q, "o": o, "a": a, "e": e[:190]}


def _shuffle_opts(rng, right, wrong: list) -> tuple[list, int]:
    opts = [str(right)] + [str(w) for w in wrong]
    order = list(range(4))
    rng.shuffle(order)
    return [opts[i] for i in order], order.index(0)


def _wrong(rng, right: int, spread: int = 6) -> list[int]:
    out = set()
    while len(out) < 3:
        w = right + rng.choice([-1, 1]) * rng.randint(1, spread)
        if w != right and w >= 0:
            out.add(w)
    return list(out)


def local_puzzle(seed: str) -> dict:
    """Internet/AI boʻlmasa ham ishlaydigan jumboqlar (har kuni boshqacha)."""
    rng = random.Random("bk-daily-" + seed)
    kind = rng.randrange(8)
    if kind == 0:
        a, d = rng.randint(2, 20), rng.randint(3, 9)
        seq = [a + d * i for i in range(5)]
        r = a + d * 5
        q, e = f"Ketma-ketlikni davom ettiring: {', '.join(map(str, seq))}, …", f"Har safar {d} qoʻshiladi: {seq[-1]} + {d} = {r}."
    elif kind == 1:
        a, k = rng.randint(1, 4), rng.choice([2, 3])
        seq = [a * k ** i for i in range(5)]
        r = a * k ** 5
        q, e = f"Keyingi son qaysi? {', '.join(map(str, seq))}, …", f"Har bir son oldingisidan {k} marta katta: {seq[-1]} × {k} = {r}."
    elif kind == 2:
        n = rng.randint(4, 9)
        seq = [i * i for i in range(n - 4, n)]
        r = n * n
        q, e = f"Qonuniyatni toping: {', '.join(map(str, seq))}, …", f"Bular ketma-ket sonlarning kvadratlari: {n} × {n} = {r}."
    elif kind == 3:
        x, y = rng.randint(6, 25), rng.randint(2, 9)
        r = x
        q, e = (f"Akasi ukasidan {y} yosh katta. Ikkalasining yoshi yigʻindisi {2 * x + y} ga teng. Ukasi necha yoshda?",
                f"({2 * x + y} − {y}) : 2 = {x}. Ukasi {x} yoshda, akasi {x + y} yoshda.")
    elif kind == 4:
        legs_c, legs_r = rng.randint(3, 12), rng.randint(3, 12)
        heads, legs = legs_c + legs_r, 2 * legs_c + 4 * legs_r
        r = legs_r
        q, e = (f"Hovlida tovuqlar va quyonlar bor: jami {heads} ta bosh va {legs} ta oyoq. Nechta quyon bor?",
                f"Hammasi tovuq boʻlsa, {2 * heads} ta oyoq boʻlardi. Ortiqcha {legs - 2 * heads} ta oyoq — har quyonda 2 tadan: {r} ta quyon.")
    elif kind == 5:
        n = rng.choice([5, 6, 7, 8, 10])
        r = n
        q, e = (f"{n} ta mushuk {n} daqiqada {n} ta sichqon tutadi. 100 ta mushuk 100 ta sichqonni necha daqiqada tutadi?",
                f"Har bir mushuk {n} daqiqada bitta sichqon tutadi. 100 ta mushuk 100 ta sichqonni ham {n} daqiqada tutadi.")
    elif kind == 6:
        n = rng.randint(5, 12)
        r = n - 1
        q, e = (f"Daraxt tanasini {n} boʻlakka arralash kerak. Har bir kesish 1 daqiqa. Necha daqiqa ketadi?",
                f"{n} boʻlak uchun {n - 1} marta kesish kerak — {r} daqiqa.")
    else:
        n = rng.randint(4, 8)
        r = n * (n - 1) // 2
        q, e = (f"{n} doʻst uchrashdi va har biri qolganlar bilan bir martadan qoʻl berib koʻrishdi. Jami nechta qoʻl siqish boʻldi?",
                f"Har biri {n - 1} kishi bilan koʻrishadi, lekin har bir juft ikki marta sanalmaydi: {n} × {n - 1} : 2 = {r}.")
    opts, ai = _shuffle_opts(rng, r, _wrong(rng, r, 4 if r < 15 else 8))
    return {"q": q, "o": opts, "a": ai, "e": e[:190]}


async def ai_puzzle(day: str) -> dict | None:
    if not GEMINI_KEY:
        return None
    system = ("Sen boshlangʻich va 5–7-sinf oʻquvchilari uchun mantiqiy jumboqlar tuzuvchi oʻqituvchisan. "
              "Faqat oʻzbek tilida (lotin yozuvida), qisqa va aniq yoz. Savol 1–2 jumla, uzun hisob-kitobsiz, "
              "aqlni charxlaydigan boʻlsin. Javob bir maʼnoli va 100% toʻgʻri boʻlishi shart: kerakli barcha maʼlumot "
              "savolda aniq yozilsin, ikki xil tushunish mumkin boʻlgan (masalan, oila aʼzolarini sanash) savollar tuzma.")
    prompt = (f"Bugungi sana: {day}. Bitta «Kun jumbogʻi» tuz: mantiq, sonli qonuniyat, qiziqarli masala yoki hazil-savol. "
              "JSON qaytar: {\"q\": savol (260 belgidan qisqa), \"o\": [4 ta qisqa variant], \"a\": toʻgʻri variant indeksi 0–3, "
              "\"e\": qisqa yechim (180 belgidan qisqa)}. Variantlar bir-biridan farq qilsin.")
    try:
        text = await gemini_call([{"role": "user", "parts": [{"text": prompt}]}], system=system, max_tokens=1024, temperature=1.0)
        p = valid_puzzle(parse_json_text(text))
        if not p:
            return None
        # Ikkinchi tekshiruv: AI jumboqni mustaqil yechadi; javob mos kelmasa yoki noaniq boʻlsa — tashlanadi.
        check = ("Quyidagi jumboqni diqqat bilan, bosqichma-bosqich yech. Agar savol ikki xil tushunilishi mumkin boʻlsa "
                 "yoki toʻgʻri javob variantlarda boʻlmasa, ok=false qaytar.\n\n"
                 f"Savol: {p['q']}\nVariantlar: " + "; ".join(f"{i}) {o}" for i, o in enumerate(p["o"])) +
                 '\n\nJSON qaytar: {"a": toʻgʻri variant indeksi 0–3, "ok": true/false}')
        v = parse_json_text(await gemini_call([{"role": "user", "parts": [{"text": check}]}], max_tokens=2048, temperature=0.0))
        if not isinstance(v, dict) or v.get("ok") is False or int(v.get("a", -1)) != p["a"]:
            log.info("ai_puzzle rad etildi: %s / %s", p, v)
            return None
        return p
    except Exception as e:
        log.warning("ai_puzzle: %s", e)
        return None


async def daily_get(create: bool) -> dict | None:
    global LIB_DIRTY
    lib = await lib_load()
    today = _today()
    d = lib.get("daily")
    if d and d.get("d") == today and (d.get("posted") or not create):
        return d
    if not create or _tash_now().hour < DAILY_HOUR:
        return d
    async with DAILY_LOCK:
        d = lib.get("daily")
        if not (d and d.get("d") == today):
            p = await ai_puzzle(today) or local_puzzle(today)
            d = {"d": today, **p, "posted": False, "tries": 0}
        if not d.get("posted"):
            if DAILY_CHANNEL:
                try:
                    msg = await bot.send_poll(
                        DAILY_CHANNEL, question=f"🧩 Kun jumbogʻi · {_uz_date(today)}\n\n{d['q']}"[:300],
                        options=d["o"], type="quiz", correct_option_id=d["a"],
                        explanation=(d.get("e") or None), is_anonymous=True)
                    d["posted"], d["mid"] = True, msg.message_id
                    stat_inc("daily")
                except Exception as e:
                    log.warning("daily post: %s", e)
                    d["err"] = str(e)[:200]
                    d["tries"] = int(d.get("tries") or 0) + 1
                    if d["tries"] >= 6:
                        d["posted"] = True   # bugun boshqa urinmaymiz
            else:
                d["posted"] = True
        async with LIB_LOCK:
            lib["daily"] = d
            if LIB_CHAT:
                try:
                    await lib_save_index()
                except Exception as e:
                    log.warning("daily save: %s", e)
                    LIB_DIRTY = True
    return d


async def api_daily(request: web.Request) -> web.Response:
    d = await daily_get(True)
    if not d:
        return web.json_response({"ok": True, "p": None})
    return web.json_response({"ok": True, "p": {k: d.get(k) for k in ("d", "q", "o", "a", "e")},
                              "today": d.get("d") == _today(), "channel": DAILY_CHANNEL,
                              "posted": bool(d.get("mid")), "err": d.get("err", "") if not d.get("mid") else ""})


async def daily_loop(app: web.Application) -> None:
    async def loop():
        await asyncio.sleep(30)
        while True:
            try:
                await daily_get(True)
            except Exception as e:
                log.warning("daily loop: %s", e)
            await asyncio.sleep(900)
    app["daily_task"] = asyncio.create_task(loop())


# ===================== UY VAZIFASI =====================
# Oʻqituvchi toʻplamdan uy vazifasi havolasini oladi. Oʻquvchi uyda oʻynaydi,
# natija darhol oʻqituvchining Telegramiga keladi va saytdagi «Uy vazifalari» sahifasida koʻrinadi.
# Savollar kutubxona kanalida JSON fayl boʻlib saqlanadi, roʻyxat — LIB["hw"].
HW_MAX = 400
HW_PER_TEACHER = 40
HW_RES_MAX = 120
HW_GAMES = {"minora", "xazina", "raketa", "mozaika", "bomba", "tez", "juft"}
HW_ITEMS: dict[str, dict] = {}
HW_RATE: dict[str, float] = {}


def _hw() -> dict:
    return LIB.setdefault("hw", {})


async def hw_payload(hid: str, m: dict) -> dict:
    if hid not in HW_ITEMS:
        d = json.loads((await bot.download(m["f"])).read().decode("utf-8"))
        HW_ITEMS[hid] = d if isinstance(d, dict) else {}
    return HW_ITEMS[hid]


async def api_hw_create(request: web.Request) -> web.Response:
    data = await read_json(request)
    u = site_user(data)
    if not u:
        return jerr("auth", 401)
    if not LIB_CHAT:
        return jerr("Uy vazifasi hali ulanmagan (LIBRARY_CHAT_ID kerak).", 503)
    items = [it for it in norm_items(data.get("items")) if "o" in it or "a" in it]
    if len(items) < 3:
        return jerr("Uy vazifasi uchun kamida 3 ta test yoki son-javobli savol kerak.")
    g = str(data.get("g", "minora"))
    if g not in HW_GAMES:
        g = "minora"
    if g == "bomba" and sum(1 for it in items if "a" in it and 1 <= it["a"] <= 9) < 4:
        g = "minora"
    name = clip(data.get("name"), 60) or "Uy vazifasi"
    note = clip(data.get("note"), 200)
    lib = await lib_load()
    hw = lib.setdefault("hw", {})
    mine = [k for k, m in hw.items() if m.get("u") == u["u"]]
    if len(mine) >= HW_PER_TEACHER:
        return jerr(f"Koʻpi bilan {HW_PER_TEACHER} ta uy vazifasi saqlanadi. Eskilarini oʻchiring.")
    hid = secrets.token_hex(4)
    payload = {"name": name, "note": note, "g": g, "tn": u["n"], "items": items}
    async with LIB_LOCK:
        try:
            doc = await bot.send_document(
                LIB_CHAT, BufferedInputFile(json.dumps(payload, ensure_ascii=False).encode("utf-8"), filename=f"uy-{hid}.json"),
                caption=f"📝 Uy vazifasi: {name}\n{len(items)} ta savol · ✍️ {u['n']}"[:1000], disable_notification=True)
        except Exception as e:
            log.warning("hw create: %s", e)
            return jerr("Saqlab boʻlmadi. Bot kutubxona kanalida administrator ekanini tekshiring.", 502)
        hw[hid] = {"f": doc.document.file_id, "mid": doc.message_id, "u": u["u"], "n": name, "g": g,
                   "c": len(items), "t": int(time.time()), "r": []}
        HW_ITEMS[hid] = payload
        if len(hw) > HW_MAX:
            for k in sorted(hw, key=lambda k: hw[k].get("t", 0))[:len(hw) - HW_MAX]:
                hw.pop(k, None)
        await lib_save_index()
    stat_inc("hw")
    return web.json_response({"ok": True, "id": hid})


async def api_hw_get(request: web.Request) -> web.Response:
    hid = clip((await read_json(request)).get("id"), 20)
    lib = await lib_load()
    m = (lib.get("hw") or {}).get(hid)
    if not m:
        return jerr("Uy vazifasi topilmadi yoki oʻchirilgan.", 404)
    try:
        p = await hw_payload(hid, m)
    except Exception as e:
        log.warning("hw get: %s", e)
        return jerr("Yuklab boʻlmadi", 502)
    return web.json_response({"ok": True, "hw": {"id": hid, "name": p.get("name") or m["n"], "note": p.get("note", ""),
                                                 "g": m.get("g", "minora"), "tn": p.get("tn", ""), "items": p.get("items", [])}})


async def api_hw_submit(request: web.Request) -> web.Response:
    global LIB_DIRTY
    data = await read_json(request)
    hid = clip(data.get("id"), 20)
    lib = await lib_load()
    m = (lib.get("hw") or {}).get(hid)
    if not m:
        return jerr("Uy vazifasi topilmadi", 404)
    name = re.sub(r"\s+", " ", clip(data.get("name"), 60)) or "Oʻquvchi"
    cls = clip(data.get("cls"), 20)
    ip = request.headers.get("X-Forwarded-For", request.remote or "").split(",")[0].strip()
    key = f"{hid}:{ip}:{name.lower()}"
    now = time.time()
    if now - HW_RATE.get(key, 0) < 20:
        return web.json_response({"ok": True, "dup": True})
    HW_RATE[key] = now
    if len(HW_RATE) > 5000:
        for k in [k for k, t in HW_RATE.items() if now - t > 600]:
            HW_RATE.pop(k, None)

    def num(v, hi=100000):
        try:
            return max(0, min(hi, int(v)))
        except (TypeError, ValueError):
            return 0
    right, total, score, sec = num(data.get("right"), 500), num(data.get("total"), 500), num(data.get("score")), num(data.get("sec"), 36000)
    right = min(right, total)
    wrong = [clip(re.sub(r"<[^>]+>", "", str(x)), 120) for x in (data.get("wrong") or [])[:12]] if isinstance(data.get("wrong"), list) else []
    pct = round(100 * right / total) if total else 0
    rec = {"n": name, "k": cls, "r": right, "t": total, "s": score, "p": pct, "sec": sec, "ts": int(now), "w": wrong[:8]}
    m.setdefault("r", []).append(rec)
    m["r"] = m["r"][-HW_RES_MAX:]
    LIB_DIRTY = True
    stat_inc("hw_done")
    icon = "🟢" if pct >= 80 else "🟡" if pct >= 50 else "🔴"
    txt = (f"📝 Uy vazifasi: «{m['n']}»\n\n{icon} {name}{' (' + cls + ')' if cls else ''}\n"
           f"✅ {right}/{total} toʻgʻri ({pct}%) · ball: {score}" + (f" · ⏱ {sec // 60}:{sec % 60:02d}" if sec else ""))
    if wrong:
        txt += "\n\n❌ Xato qilingan savollar:\n" + "\n".join("• " + w for w in wrong[:6])
    txt += f"\n\nBarcha natijalar: {SITE_URL}#/uy"
    try:
        await bot.send_message(m["u"], txt[:4000], disable_web_page_preview=True)
    except Exception as e:
        log.warning("hw notify: %s", e)
    return web.json_response({"ok": True, "pct": pct})


async def api_hw_list(request: web.Request) -> web.Response:
    data = await read_json(request)
    u = site_user(data)
    if not u:
        return jerr("auth", 401)
    lib = await lib_load()
    out = [{"id": k, "name": m.get("n"), "g": m.get("g"), "c": m.get("c"), "t": m.get("t"), "r": m.get("r", [])}
           for k, m in (lib.get("hw") or {}).items() if m.get("u") == u["u"]]
    out.sort(key=lambda x: -(x.get("t") or 0))
    return web.json_response({"ok": True, "on": bool(LIB_CHAT), "hw": out})


async def api_hw_delete(request: web.Request) -> web.Response:
    data = await read_json(request)
    u = site_user(data)
    if not u:
        return jerr("auth", 401)
    hid = clip(data.get("id"), 20)
    lib = await lib_load()
    m = (lib.get("hw") or {}).get(hid)
    if not m or (m.get("u") != u["u"] and u["u"] != ADMIN_ID):
        return jerr("Ruxsat yoʻq", 403)
    async with LIB_LOCK:
        lib["hw"].pop(hid, None)
        HW_ITEMS.pop(hid, None)
        try:
            await bot.delete_message(LIB_CHAT, m["mid"])
        except Exception:
            pass
        await lib_save_index()
    return web.json_response({"ok": True})


async def lib_shutdown(app: web.Application) -> None:
    """Uyqudan oldin uy vazifasi natijalarini ham saqlab qoʻyadi."""
    if LIB_DIRTY and LIB_CHAT and LIB is not None:
        try:
            async with LIB_LOCK:
                await asyncio.wait_for(lib_save_index(), 20)
        except Exception as e:
            log.warning("lib shutdown: %s", e)


@web.middleware
async def no_cache(request: web.Request, handler):
    response = await handler(request)
    if request.path.startswith("/games/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


def build_app() -> web.Application:
    app = web.Application(middlewares=[cors, no_cache], client_max_size=20 * 1024 * 1024)
    app.router.add_get("/", index)
    app.router.add_post("/api/key", api_key)
    app.router.add_post("/api/sets", api_sets)
    for path, fn in (("/api/ping", api_ping), ("/api/login/start", api_login_start), ("/api/login/check", api_login_check),
                     ("/api/me", api_me), ("/api/ai", api_ai), ("/api/chat", api_chat), ("/api/send", api_send),
                     ("/api/lib/list", api_lib_list), ("/api/lib/get", api_lib_get), ("/api/lib/play", api_lib_play),
                     ("/api/lib/publish", api_lib_publish), ("/api/lib/delete", api_lib_delete),
                     ("/api/sets/save", api_sets_save), ("/api/sets/delete", api_sets_delete),
                     ("/api/hit", api_hit), ("/api/admin/stats", api_admin_stats), ("/api/darslik", api_darslik),
                     ("/api/daily", api_daily), ("/api/hw/create", api_hw_create), ("/api/hw/get", api_hw_get),
                     ("/api/hw/submit", api_hw_submit), ("/api/hw/list", api_hw_list), ("/api/hw/delete", api_hw_delete)):
        app.router.add_post(path, fn)
    app.router.add_get("/api/daily", api_daily)
    app.router.add_static("/games/", GAMES_DIR)
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    app.on_startup.append(on_startup)
    app.on_startup.append(lib_flush_loop)
    app.on_startup.append(stat_loop)
    app.on_startup.append(daily_loop)
    app.on_shutdown.insert(0, stat_shutdown)
    app.on_shutdown.insert(1, lib_shutdown)
    return app


def main() -> None:
    web.run_app(build_app(), host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
