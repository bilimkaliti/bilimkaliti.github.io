"""Bilim Kaliti — sinf o'yinlari uchun Telegram bot.

Bot o'yinlarni Telegram ichida (Mini App) ochadi va o'yin boshlanganda
javob kodlarini o'qituvchiga yuboradi.
"""
import ast
import asyncio
import datetime
import hashlib
import hmac
import json
import logging
import operator
import os
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
BTN_AI = "✨ AI bilan savollar"
BTN_OWN = "✍️ Oʻz savollarim"
BTN_SETS = "📦 Toʻplamlarim"

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
AI_DAILY = int(os.environ.get("AI_DAILY", "15") or 15)   # bir o'qituvchiga kuniga nechta AI so'rov
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
AI_USES: dict[int, tuple[str, int]] = {}
SETS_CACHE: dict[int, list[dict]] = {}
SET_LOCKS: dict[int, asyncio.Lock] = {}


def clear_wait(uid: int) -> None:
    for s in (WAIT_FEEDBACK, WAIT_AI, WAIT_OWN):
        s.discard(uid)


def kb(rows: list[list[str]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t) for t in r] for r in rows], resize_keyboard=True)


def menu_kb() -> ReplyKeyboardMarkup:
    return kb([[BTN_CLASSES], [BTN_AI, BTN_OWN], [BTN_SETS, BTN_KEY], [BTN_GAMES], [BTN_FEEDBACK, BTN_HELP]])


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


def set_games_kb(sid: str) -> InlineKeyboardMarkup:
    extra = f"&set={sid}"
    buttons = [InlineKeyboardButton(text=title, web_app=WebAppInfo(url=game_url(slug, gk, extra)))
               for slug, gk, title, _ in GRADE_GAMES if gk != "zanjir"]
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
    await message.answer(
        "Assalomu alaykum! Men «Bilim Kaliti» botiman 🔑\n"
        "Darsda guruhlar bilan oʻynaladigan oʻyinlarni ochib beraman.\n\n"
        "Boshlash uchun «📚 Sinflar» tugmasini bosing.",
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


async def add_set(uid: int, name: str, items: list[dict], src: str) -> tuple[dict, bool]:
    async with lock_for(uid):
        sets = list(await load_sets(uid))
        s = {"id": secrets.token_hex(3), "name": name[:60], "src": src, "t": int(time.time()), "items": items[:MAX_ITEMS]}
        sets.append(s)
        dropped = len(sets) > MAX_SETS
        sets = sets[-MAX_SETS:]
        await save_sets(uid, sets)
    return s, dropped


def set_preview(s: dict, limit: int = 12) -> str:
    lines = [f"📦 «{s['name']}» — {len(s['items'])} ta savol\n"]
    for i, it in enumerate(s["items"][:limit], 1):
        lines.append(f"{i}. {it['q']}  →  {it['a']}")
    if len(s["items"]) > limit:
        lines.append(f"… yana {len(s['items']) - limit} ta")
    small = sum(1 for it in s["items"] if 1 <= it["a"] <= 9)
    lines.append("\nOʻyinni tanlang 👇")
    if small < len(s["items"]):
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
        "Javob — butun son (0–9999). Bekor qilish: «🏠 Bosh menyu».",
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
    await message.answer(set_preview(s), reply_markup=set_games_kb(s["id"]))


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


def ai_left(uid: int) -> int:
    today = datetime.date.today().isoformat()
    day, used = AI_USES.get(uid, (today, 0))
    if day != today:
        used = 0
    limit = AI_DAILY * 4 if uid == ADMIN_ID else AI_DAILY
    return limit - used


def ai_use(uid: int) -> None:
    today = datetime.date.today().isoformat()
    day, used = AI_USES.get(uid, (today, 0))
    AI_USES[uid] = (today, (used if day == today else 0) + 1)


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
    await message.answer(set_preview(s), reply_markup=set_games_kb(s["id"]))


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
    await call.message.edit_text(set_preview(s), reply_markup=set_games_kb(sid))
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
    await call.answer("Oʻchirildi")
    await send_sets_list(uid, edit=call.message)


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
    user = check_init_data(str(data.get("initData", "")))
    if not user or "id" not in user:
        return web.json_response({"ok": False}, status=403)
    sets = await load_sets(int(user["id"]))
    return web.json_response({"ok": True, "sets": [{"id": s["id"], "name": s["name"], "items": s["items"]} for s in sets]})


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
    app.router.add_post("/api/sets", api_sets)
    app.router.add_static("/games/", GAMES_DIR)
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    app.on_startup.append(on_startup)
    web.run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
