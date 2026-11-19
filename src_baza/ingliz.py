# -*- coding: utf-8 -*-
"""Ingliz tili (1–9-sinf) savollar bazasi: games/baza/ingliz.json
Lugʻat va grammatika jadvallaridan yasaladi. Ishga tushirish: python3 src_baza/ingliz.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Baza

B = Baza('Ingliz tili', 'ingliz', 2028)
R = B.R; ch = R.choice; mc = B.mc
L = 'Lugʻat (soʻzlar)'; G = 'Grammatika'

# ---------- lugʻat yordamchilari ----------
def typo(w):
    """notoʻgʻri yozilishlar"""
    out = set(); v = 'aeiou'
    for _ in range(40):
        t = R.randrange(4); s = list(w)
        if t == 0 and len(w) > 3: i = R.randrange(1, len(w)); del s[i]
        elif t == 1 and len(w) > 2: i = R.randrange(len(w) - 1); s[i], s[i + 1] = s[i + 1], s[i]
        elif t == 2: i = R.randrange(len(w)); s.insert(i, s[i])
        else:
            idx = [i for i, c in enumerate(w) if c in v]
            if not idx: continue
            i = ch(idx); s[i] = ch([x for x in v if x != w[i]])
        x = ''.join(s)
        if x != w and ' ' not in x.strip() or (' ' in w and x != w): out.add(x)
        if len(out) >= 3: break
    return [x for x in out if x != w]

def vocab(pairs):
    en = [a for a, b in pairs]; uz = [b for a, b in pairs]
    def g1():
        a, b = ch(pairs); return mc(f'«{a}» soʻzining tarjimasi qaysi?', b, R.sample([x for x in uz if x != b], 3))
    def g2():
        a, b = ch(pairs); return mc(f'«{b}» inglizcha qanday?', a, R.sample([x for x in en if x != a], 3))
    def g3():
        a, b = ch(pairs)
        if R.random() < .5 and len(a) >= 4:
            t = typo(a)
            if len(t) >= 3: return mc(f'«{b}» soʻzi inglizchada qaysi qatorda toʻgʻri yozilgan?', a, t)
        return g2()
    return g1, g2, g3

def topicv(tid, name, sinf, pairs, k=''):
    g1, g2, g3 = vocab(pairs); B.topic(L, tid, name, sinf, g1, g2, g3, k)

# ======================= 1–4-SINF =======================
COL = [('red', 'qizil'), ('blue', 'koʻk'), ('green', 'yashil'), ('yellow', 'sariq'), ('black', 'qora'), ('white', 'oq'), ('orange', 'toʻq sariq'),
       ('brown', 'jigarrang'), ('pink', 'pushti'), ('grey', 'kulrang'), ('purple', 'binafsha')]
topicv('ranglar', 'Colours — Ranglar', [1, 2], COL, 'colour color rang')

NUMW = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',
        'seventeen', 'eighteen', 'nineteen', 'twenty']
def nm(lo, hi):
    def g():
        n = R.randint(lo, hi); t = R.randrange(3)
        if t == 0: return mc(f'{n} inglizcha qanday?', NUMW[n - 1], R.sample([x for x in NUMW[max(0, lo - 3):hi + 2] if x != NUMW[n - 1]], 3))
        if t == 1: return mc(f'«{NUMW[n - 1]}» qaysi son?', str(n), R.sample([str(x) for x in range(max(1, n - 4), min(20, n + 4) + 1) if x != n], 3))
        a, b = R.randint(1, 10), R.randint(1, 10)
        if a + b > 20: return None
        return mc(f'{NUMW[a - 1]} + {NUMW[b - 1]} = ?', NUMW[a + b - 1], R.sample([x for x in NUMW if x != NUMW[a + b - 1]], 3))
    return g
def nm3():
    n = R.randint(4, 20); t = typo(NUMW[n - 1])
    if R.random() < .5 and len(t) >= 3: return mc(f'{n} soni inglizchada qaysi qatorda toʻgʻri yozilgan?', NUMW[n - 1], t)
    a, b = R.randint(5, 20), R.randint(1, 9)
    if a <= b: return None
    return mc(f'{NUMW[a - 1]} − {NUMW[b - 1]} = ?', NUMW[a - b - 1], R.sample([x for x in NUMW if x != NUMW[a - b - 1]], 3))
B.topic(L, 'sonlar', 'Numbers 1–20 — Sonlar', [1, 2], nm(1, 10), nm(1, 20), nm3, 'number son raqam')

ANI = [('cat', 'mushuk'), ('dog', 'it'), ('cow', 'sigir'), ('horse', 'ot'), ('sheep', 'qoʻy'), ('bird', 'qush'), ('fish', 'baliq'), ('lion', 'sher'),
       ('tiger', 'yoʻlbars'), ('bear', 'ayiq'), ('rabbit', 'quyon'), ('monkey', 'maymun'), ('elephant', 'fil'), ('chicken', 'tovuq'), ('duck', 'oʻrdak'),
       ('frog', 'qurbaqa'), ('mouse', 'sichqon'), ('wolf', 'boʻri'), ('fox', 'tulki'), ('camel', 'tuya')]
topicv('hayvonlar', 'Animals — Hayvonlar', [1, 2], ANI, 'animal hayvon')

FAM = [('mother', 'ona'), ('father', 'ota'), ('grandmother', 'buvi'), ('grandfather', 'bobo'), ('son', 'oʻgʻil'), ('daughter', 'qiz (farzand)'),
       ('baby', 'chaqaloq'), ('parents', 'ota-ona'), ('family', 'oila'), ('brother', 'aka yoki uka'), ('sister', 'opa yoki singil'), ('uncle', 'amaki yoki togʻa'), ('aunt', 'xola yoki amma')]
topicv('oila', 'Family — Oila', [2, 3], FAM, 'family oila')

BODY = [('head', 'bosh'), ('eye', 'koʻz'), ('ear', 'quloq'), ('nose', 'burun'), ('mouth', 'ogʻiz'), ('hand', 'qoʻl (kaft)'), ('leg', 'oyoq'), ('hair', 'soch'),
        ('face', 'yuz'), ('teeth', 'tishlar'), ('finger', 'barmoq'), ('neck', 'boʻyin'), ('shoulder', 'yelka'), ('knee', 'tizza')]
topicv('tana', 'Body — Tana aʼzolari', [2, 3], BODY, 'body tana')

SCH = [('book', 'kitob'), ('pen', 'ruchka'), ('pencil', 'qalam'), ('ruler', 'chizgʻich'), ('bag', 'sumka'), ('desk', 'parta'), ('board', 'doska'),
       ('eraser', 'oʻchirgʻich'), ('notebook', 'daftar'), ('teacher', 'oʻqituvchi'), ('pupil', 'oʻquvchi'), ('classroom', 'sinf xonasi'), ('school', 'maktab')]
topicv('maktab', 'School things — Maktab buyumlari', [2, 3], SCH, 'school maktab')

FOOD = [('bread', 'non'), ('milk', 'sut'), ('water', 'suv'), ('apple', 'olma'), ('egg', 'tuxum'), ('meat', 'goʻsht'), ('tea', 'choy'), ('juice', 'sharbat'),
        ('sugar', 'shakar'), ('rice', 'guruch'), ('cheese', 'pishloq'), ('soup', 'shoʻrva'), ('grapes', 'uzum'), ('melon', 'qovun'), ('carrot', 'sabzi'),
        ('potato', 'kartoshka'), ('tomato', 'pomidor'), ('salt', 'tuz'), ('butter', 'sariyogʻ')]
topicv('ovqat', 'Food and drinks — Oziq-ovqat', [3, 4], FOOD, 'food ovqat')

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
DUZ = ['dushanba', 'seshanba', 'chorshanba', 'payshanba', 'juma', 'shanba', 'yakshanba']
def dy1():
    i = R.randrange(7); return mc(f'«{DAYS[i]}» qaysi kun?', DUZ[i], R.sample([x for x in DUZ if x != DUZ[i]], 3))
def dy2():
    i = R.randrange(7)
    if R.random() < .5: return mc(f'«{DUZ[i]}» inglizcha qanday?', DAYS[i], R.sample([x for x in DAYS if x != DAYS[i]], 3))
    return mc(f'What day comes after {DAYS[i]}?', DAYS[(i + 1) % 7], R.sample([x for x in DAYS if x != DAYS[(i + 1) % 7]], 3))
def dy3():
    i = R.randrange(7); t = R.randrange(3)
    if t == 0: return mc(f'What day comes before {DAYS[i]}?', DAYS[i - 1], R.sample([x for x in DAYS if x != DAYS[i - 1]], 3))
    if t == 1: return mc('How many days are there in a week?', 'seven', ['five', 'six', 'eight'])
    tp = typo(DAYS[i]); return mc(f'«{DUZ[i]}» inglizchada qaysi qatorda toʻgʻri yozilgan?', DAYS[i], tp) if len(tp) >= 3 else None
B.topic(L, 'kunlar', 'Days of the week — Hafta kunlari', [3, 4], dy1, dy2, dy3, 'days hafta kun')

# ---- to be ----
BE = [('I', 'am'), ('You', 'are'), ('He', 'is'), ('She', 'is'), ('It', 'is'), ('We', 'are'), ('They', 'are'), ('My mother', 'is'), ('My friends', 'are'),
      ('The cat', 'is'), ('Ali and Vali', 'are'), ('Tom', 'is')]
BEC = ['happy', 'at school', 'at home', 'in the garden', 'hungry', 'tired', 'from Uzbekistan']
def be1():
    s, v = ch(BE[:7]); return mc(f'{s} ___ {ch(BEC)}.', v, [x for x in ['am', 'is', 'are', 'be'] if x != v])
def be2():
    s, v = ch(BE); return mc(f'{s} ___ {ch(BEC)}.', v, [x for x in ['am', 'is', 'are', 'be'] if x != v])
def be3():
    s, v = ch(BE); t = R.randrange(3)
    if t == 0: return mc(f'___ {s.lower() if s not in ("I", "Tom", "Ali and Vali") else s} {ch(BEC)}?', v.capitalize(), [x.capitalize() for x in ['am', 'is', 'are', 'be'] if x != v])
    if t == 1:
        neg = {'am': "am not", 'is': "isn't", 'are': "aren't"}[v]; return mc(f'{s} ___ {ch(BEC)}. (inkor)', neg, [x for x in ["am not", "isn't", "aren't", "don't"] if x != neg])
    sh = {'I': "I'm", 'You': "You're", 'He': "He's", 'She': "She's", 'It': "It's", 'We': "We're", 'They': "They're"}
    s, v = ch(BE[:7]); return mc(f'«{s} {v}» qisqa shakli qaysi?', sh[s], R.sample([x for x in sh.values() if x != sh[s]], 3))
B.topic(G, 'tobe', 'To be: am / is / are', [3, 4, 5], be1, be2, be3, 'to be am is are')

AN = ['apple', 'egg', 'orange', 'elephant', 'umbrella', 'ice cream', 'onion', 'owl', 'eye', 'island']
A_ = ['book', 'cat', 'dog', 'pen', 'banana', 'car', 'house', 'girl', 'bag', 'table', 'yellow car']
def ar1():
    w = ch(AN + A_); r = 'an' if w in AN else 'a'; return mc(f'___ {w}', r, ['a', 'an', 'the', '—'] if False else [x for x in ['a', 'an', 'the', 'some'] if x != r])
def ar2():
    t = R.randrange(2)
    if t == 0: return mc('Qaysi soʻz oldidan «an» qoʻyiladi?', ch(AN), R.sample(A_, 3))
    return mc('Qaysi soʻz oldidan «a» qoʻyiladi?', ch(A_), R.sample(AN, 3))
ar3 = [mc('___ hour', 'an', ['a', 'the', 'some']), mc('___ university', 'a', ['an', 'some', 'the']), mc('___ honest man', 'an', ['a', 'some', 'the']),
       mc('___ uniform', 'a', ['an', 'some', 'the']), mc('«an» qachon ishlatiladi?', 'Unli tovush bilan boshlanuvchi soʻz oldidan', ['Har doim', 'Koʻplikdagi soʻz oldidan', 'Undosh bilan boshlanuvchi soʻz oldidan']),
       mc('I have ___ old car.', 'an', ['a', 'some', 'many']), mc('She is ___ English teacher.', 'an', ['a', 'some', 'many']), mc('It is ___ big elephant.', 'a', ['an', 'some', 'many']),
       mc('He eats ___ egg every morning.', 'an', ['a', 'some', 'many']), mc('This is ___ useful book.', 'a', ['an', 'some', 'many']), mc('The sun is ___ star.', 'a', ['an', 'some', 'many'])]
B.topic(G, 'artikl', 'Articles: a / an', [3, 4], ar1, ar2, ar3, 'article a an artikl')

MON = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
MUZ = ['yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun', 'iyul', 'avgust', 'sentabr', 'oktabr', 'noyabr', 'dekabr']
SEA = {'winter': [11, 0, 1], 'spring': [2, 3, 4], 'summer': [5, 6, 7], 'autumn': [8, 9, 10]}
SUZ = {'winter': 'qish', 'spring': 'bahor', 'summer': 'yoz', 'autumn': 'kuz'}
def mo1():
    i = R.randrange(12); return mc(f'«{MON[i]}» qaysi oy?', MUZ[i], R.sample([x for x in MUZ if x != MUZ[i]], 3))
def mo2():
    t = R.randrange(3); i = R.randrange(12)
    if t == 0: return mc(f'«{MUZ[i]}» inglizcha qanday?', MON[i], R.sample([x for x in MON if x != MON[i]], 3))
    if t == 1: s = ch(list(SUZ)); return mc(f'«{s}» qaysi fasl?', SUZ[s], [x for x in SUZ.values() if x != SUZ[s]])
    return mc(f'What month comes after {MON[i]}?', MON[(i + 1) % 12], R.sample([x for x in MON if x != MON[(i + 1) % 12]], 3))
def mo3():
    i = R.randrange(12); s = [k for k, v in SEA.items() if i in v][0]; t = R.randrange(3)
    if t == 0: return mc(f'{MON[i]} is in ___ (Oʻzbekistonda).', s, [x for x in SEA if x != s])
    if t == 1: return mc('How many months are there in a year?', 'twelve', ['ten', 'eleven', 'four'])
    tp = typo(MON[i]); return mc(f'«{MUZ[i]}» inglizchada qaysi qatorda toʻgʻri yozilgan?', MON[i], tp) if len(tp) >= 3 else None
B.topic(L, 'oylar', 'Months and seasons — Oylar va fasllar', [4, 5], mo1, mo2, mo3, 'months seasons oy fasl')

CLO = [('shirt', 'koʻylak'), ('trousers', 'shim'), ('jacket', 'kurtka'), ('hat', 'shlyapa'), ('cap', 'kepka'), ('shoes', 'tufli'), ('socks', 'paypoq'),
       ('skirt', 'yubka'), ('coat', 'palto'), ('scarf', 'sharf'), ('gloves', 'qoʻlqop'), ('boots', 'etik'), ('dress', 'koʻylak (ayollar)')]
CLO = [x for x in CLO if x[0] != 'dress']
topicv('kiyim', 'Clothes — Kiyimlar', [4, 5], CLO, 'clothes kiyim')

PL = {'cat': 'cats', 'book': 'books', 'dog': 'dogs', 'pen': 'pens', 'girl': 'girls', 'box': 'boxes', 'bus': 'buses', 'watch': 'watches', 'dish': 'dishes',
      'tomato': 'tomatoes', 'potato': 'potatoes', 'baby': 'babies', 'city': 'cities', 'family': 'families', 'man': 'men', 'woman': 'women', 'child': 'children',
      'tooth': 'teeth', 'foot': 'feet', 'mouse': 'mice', 'person': 'people', 'sheep': 'sheep', 'fish': 'fish', 'knife': 'knives', 'leaf': 'leaves', 'wolf': 'wolves', 'boy': 'boys', 'day': 'days'}
REG = ['cat', 'book', 'dog', 'pen', 'girl', 'boy', 'day']; ES = ['box', 'bus', 'watch', 'dish', 'tomato', 'potato', 'baby', 'city', 'family']
IRR = ['man', 'woman', 'child', 'tooth', 'foot', 'mouse', 'person', 'sheep', 'fish', 'knife', 'leaf', 'wolf']
def wr(w):
    r = PL[w]; c = {w + 's', w + 'es', w[:-1] + 'ies' if w.endswith('y') else w + 'ies', w + 'en', w}
    return [x for x in c if x != r]
def pl(words):
    def g():
        w = ch(words); return mc(f'«{w}» soʻzining koʻplik shakli qaysi?', PL[w], wr(w))
    return g
B.topic(G, 'koplik', 'Plural nouns — Koʻplik shakli', [4, 5], pl(REG + ES[:4]), pl(ES), pl(IRR), 'plural koʻplik')

CAN = [('A fish can ___.', 'swim', ['fly', 'climb trees', 'sing']), ('A bird can ___.', 'fly', ['swim under water', 'read', 'drive']),
       ('A horse can ___.', 'run fast', ['fly', 'read', 'write']), ('A monkey can ___.', 'climb trees', ['fly', 'read books', 'drive a car']),
       ('A cat can’t ___.', 'fly', ['run', 'jump', 'sleep']), ('A fish can’t ___.', 'walk', ['swim', 'eat', 'breathe in water']),
       ('A dog can ___.', 'bark', ['fly', 'read', 'write']), ('A baby can’t ___.', 'drive a car', ['cry', 'sleep', 'eat'])]
def cn1():
    q, a, w = ch(CAN); return mc(q, a, w)
HAV = [('I', 'have'), ('You', 'have'), ('He', 'has'), ('She', 'has'), ('It', 'has'), ('We', 'have'), ('They', 'have'), ('My sister', 'has'), ('My parents', 'have')]
def cn2():
    s, v = ch(HAV); o = ch(['a cat', 'two brothers', 'a red bag', 'blue eyes', 'a new bike', 'many books'])
    return mc(f'{s} ___ got {o}.', v, [x for x in ['have', 'has', 'is', 'are'] if x != v])
def cn3():
    t = R.randrange(3)
    if t == 0: s, v = ch(HAV); return mc(f'___ {s.lower() if s not in ("I",) else s} got a pet?', 'Has' if v == 'has' else 'Have', [x for x in ['Have', 'Has', 'Is', 'Do'] if x != ('Has' if v == 'has' else 'Have')])
    if t == 1: return mc('Can you swim? — Yes, I ___.', 'can', ["can't", 'do', 'am'])
    return ch([mc('«can» soʻzining maʼnosi?', 'qila olmoq', ['qilmoq kerak', 'qilishni xohlamoq', 'qilgan']), mc("«can't» = ?", 'cannot', ['can not to', 'can no', 'could']),
               mc('He can ___ English well.', 'speak', ['speaks', 'speaking', 'to speak']), mc('She ___ play the piano. (qila oladi)', 'can', ['cans', 'is can', 'can to'])])
B.topic(G, 'can', 'Can / can’t, have got / has got', [4, 5], cn1, cn2, cn3, 'can have got has got')

# ======================= 5–6-SINF =======================
V3S = {'play': 'plays', 'go': 'goes', 'watch': 'watches', 'study': 'studies', 'have': 'has', 'do': 'does', 'read': 'reads', 'live': 'lives',
       'swim': 'swims', 'wash': 'washes', 'fly': 'flies', 'like': 'likes', 'work': 'works', 'cry': 'cries', 'fix': 'fixes'}
SUBJ3 = ['He', 'She', 'My brother', 'Ali', 'My mother', 'Lola']; SUBJ = ['I', 'You', 'We', 'They', 'My friends']
OBJ = {'play': 'football', 'go': 'to school', 'watch': 'TV', 'study': 'English', 'have': 'breakfast', 'do': 'homework', 'read': 'books', 'live': 'in Tashkent',
       'swim': 'in the river', 'wash': 'the dishes', 'fly': 'to London', 'like': 'apples', 'work': 'at a hospital', 'cry': 'a lot', 'fix': 'cars'}
def ps1():
    v = ch(list(V3S)); s = ch(SUBJ3 + SUBJ); r = V3S[v] if s in SUBJ3 else v
    return mc(f'{s} ___ {OBJ[v]} every day. ({v})', r, [x for x in {v, V3S[v], v + 'ing', v + 'ed' if not v.endswith('e') else v + 'd'} if x != r])
def ps2():
    v = ch(list(V3S)); s = ch(SUBJ3 + SUBJ); t = R.randrange(2)
    if t == 0: r = 'Does' if s in SUBJ3 else 'Do'; return mc(f'___ {s.lower() if s not in ("I", "Ali") else s} {v} {OBJ[v]}?', r, [x for x in ['Do', 'Does', 'Is', 'Are'] if x != r])
    r = "doesn't" if s in SUBJ3 else "don't"; return mc(f'{s} ___ {v} {OBJ[v]}.', r, [x for x in ["don't", "doesn't", "isn't", "aren't"] if x != r])
def ps3():
    v = ch(list(V3S)); t = R.randrange(3)
    if t == 0: return mc(f'«{v}» feʼlining he/she shakli qaysi?', V3S[v], [x for x in {v, v + 's', v + 'es', v[:-1] + 'ies' if v.endswith('y') else v + 'ies'} if x != V3S[v]])
    if t == 1: return mc('Present Simple qachon ishlatiladi?', 'Doimiy, takrorlanuvchi ish-harakat uchun', ['Hozir sodir boʻlayotgan ish uchun', 'Oʻtgan ish uchun', 'Kelajakdagi reja uchun'])
    s = ch(SUBJ3); v = ch(list(V3S)); return mc(f'{s} ___ {v} {OBJ[v]} on Sundays. (inkor)', "doesn't", ["don't", "isn't", "not"])
B.topic(G, 'present', 'Present Simple', [5, 6], ps1, ps2, ps3, 'present simple hozirgi oddiy zamon')

THERE = [('a book on the desk', 'is'), ('three cats in the garden', 'are'), ('a big tree near our house', 'is'), ('many people in the park', 'are'),
         ('an apple in my bag', 'is'), ('two windows in the room', 'are'), ('a park in our town', 'is'), ('some children in the classroom', 'are'),
         ('some milk in the fridge', 'is'), ('some water in the glass', 'is'), ('a lot of books in the library', 'are')]
MM = [('apples', 'many'), ('water', 'much'), ('books', 'many'), ('money', 'much'), ('children', 'many'), ('time', 'much'), ('sugar', 'much'), ('cars', 'many'),
      ('milk', 'much'), ('friends', 'many'), ('bread', 'much'), ('pencils', 'many')]
def th1():
    p, v = ch(THERE[:8]); return mc(f'There ___ {p}.', v, [x for x in ['is', 'are', 'am', 'be'] if x != v])
def th2():
    n, v = ch(MM); return mc(f'How ___ {n} are there?' if v == 'many' else f'How ___ {n} is there?', v, ['much', 'many', 'a lot', 'some'] if False else [x for x in ['much', 'many', 'a', 'any'] if x != v])
def th3():
    t = R.randrange(3)
    if t == 0: p, v = ch(THERE[8:]); return mc(f'There ___ {p}.', v, [x for x in ['is', 'are', 'am', 'be'] if x != v])
    if t == 1: p, v = ch(THERE); q = 'Is' if v == 'is' else 'Are'; return mc(f'___ there {p}?', q, [x for x in ['Is', 'Are', 'Do', 'Does'] if x != q])
    n, v = ch(MM); return mc(f'I don’t have ___ {n}.', v, [x for x in ['much', 'many', 'a', 'an'] if x != v])
B.topic(G, 'there', 'There is / There are, much / many', [5, 6], th1, th2, th3, 'there is are much many')

PREP = [('ostida', 'under'), ('ustida', 'on'), ('ichida', 'in'), ('yonida', 'next to'), ('orqasida', 'behind'), ('oldida', 'in front of')]
OBJS = [('The cat', 'the table', 'stol'), ('The ball', 'the box', 'quti'), ('The book', 'the bag', 'sumka'), ('The pen', 'the desk', 'parta'), ('The cup', 'the table', 'stol'), ('The phone', 'the bed', 'karavot')]
PL_ = ['in', 'on', 'under', 'next to', 'behind', 'in front of', 'between']
def pr1():
    u, e = ch(PREP[:3]); s, o, ou = ch(OBJS); return mc(f'{s} is ___ {o}. ({ou} {u})', e, [x for x in PL_ if x != e][:5] and R.sample([x for x in PL_ if x != e], 3))
def pr2():
    u, e = ch(PREP); s, o, ou = ch(OBJS); return mc(f'{s} is ___ {o}. ({ou} {u})', e, R.sample([x for x in PL_ if x != e], 3))
pr3 = [mc('«between» maʼnosi?', 'orasida', ['ustida', 'ostida', 'orqasida']), mc('«behind» maʼnosi?', 'orqasida', ['oldida', 'ichida', 'ustida']),
       mc('«in front of» maʼnosi?', 'oldida', ['orqasida', 'ostida', 'yonida']), mc('«next to» maʼnosi?', 'yonida', ['ichida', 'ustida', 'orqasida']),
       mc('The shop is ___ the bank and the school. (orasida)', 'between', ['behind', 'under', 'in']), mc('«under» maʼnosi?', 'ostida', ['ustida', 'yonida', 'oldida']),
       mc('My keys are ___ my pocket. (ichida)', 'in', ['on', 'under', 'behind']), mc('The picture is ___ the wall. (devorda)', 'on', ['in', 'under', 'between']),
       mc('Ali sits ___ me. (yonimda)', 'next to', ['under', 'in', 'between']), mc('The garden is ___ the house. (orqasida)', 'behind', ['in', 'on', 'under'])]
B.topic(G, 'joy', 'Prepositions of place: in, on, under…', [5], pr1, pr2, pr3, 'prepositions place predlog joy')

JOB = [('doctor', 'shifokor'), ('teacher', 'oʻqituvchi'), ('driver', 'haydovchi'), ('cook', 'oshpaz'), ('farmer', 'dehqon'), ('pilot', 'uchuvchi'),
       ('builder', 'quruvchi'), ('engineer', 'muhandis'), ('nurse', 'hamshira'), ('artist', 'rassom'), ('singer', 'qoʻshiqchi'), ('dentist', 'tish shifokori'), ('policeman', 'militsioner (politsiyachi)')]
topicv('kasb', 'Jobs — Kasblar', [5, 6], JOB, 'jobs profession kasb')

HOU = [('kitchen', 'oshxona'), ('bedroom', 'yotoqxona'), ('bathroom', 'vannaxona'), ('living room', 'mehmonxona (xona)'), ('garden', 'bogʻ'), ('window', 'deraza'),
       ('door', 'eshik'), ('roof', 'tom'), ('floor', 'pol'), ('wall', 'devor'), ('table', 'stol'), ('chair', 'stul'), ('bed', 'karavot'), ('sofa', 'divan')]
topicv('uy', 'House and rooms — Uy va xonalar', [5], HOU, 'house room uy xona')

QW = [('___ is your name?', 'What'), ('___ do you live?', 'Where'), ('___ old are you?', 'How'), ('___ is your birthday?', 'When'), ('___ is that boy?', 'Who'),
      ('___ are you sad?', 'Why'), ('___ apples are there?', 'How many'), ('___ is your favourite colour?', 'What'), ('___ is the bus station?', 'Where'),
      ('___ do you go to bed?', 'When'), ('___ is your teacher?', 'Who'), ('___ much is this bag?', 'How'), ('___ did you come late?', 'Why'), ('___ brothers have you got?', 'How many')]
QWL = ['What', 'Where', 'When', 'Who', 'Why', 'How', 'How many']
def qw():
    q, a = ch(QW); return mc(q, a, R.sample([x for x in QWL if x != a], 3))
qw3 = [mc('«Where» maʼnosi?', 'qayerda', ['qachon', 'kim', 'nima uchun']), mc('«When» maʼnosi?', 'qachon', ['qayerda', 'nima', 'qanday']), mc('«Why» maʼnosi?', 'nima uchun', ['qachon', 'kim', 'qayerda']),
       mc('«Who» maʼnosi?', 'kim', ['nima', 'qaysi', 'qanday']), mc('«How many» maʼnosi?', 'nechta', ['qancha (pul)', 'qanday', 'qachon']), mc('— ___ is it? — It’s a pen.', 'What', ['Who', 'Where', 'When']),
       mc('— ___ is your mother? — She is fine.', 'How', ['What', 'Who', 'Where']), mc('— ___ is he? — He is my brother.', 'Who', ['What', 'Where', 'How']),
       mc('— ___ are you from? — I’m from Uzbekistan.', 'Where', ['What', 'When', 'Who']), mc('— ___ do you get up? — At 7 o’clock.', 'When', ['Where', 'Who', 'What colour'])]
B.topic(G, 'soroq', 'Question words: What, Where, When…', [5, 6], qw, qw, qw3, 'question words soʻroq')

ING = {'play': 'playing', 'read': 'reading', 'run': 'running', 'swim': 'swimming', 'write': 'writing', 'make': 'making', 'sit': 'sitting', 'dance': 'dancing',
       'cry': 'crying', 'eat': 'eating', 'sleep': 'sleeping', 'cook': 'cooking', 'lie': 'lying', 'die': 'dying', 'stop': 'stopping', 'come': 'coming'}
SB = [('I', 'am'), ('He', 'is'), ('She', 'is'), ('We', 'are'), ('They', 'are'), ('The children', 'are'), ('My father', 'is'), ('You', 'are')]
def pc1():
    s, b = ch(SB); v = ch(['play', 'read', 'eat', 'sleep', 'cook']); r = f'{b} {ING[v]}'
    return mc(f'Look! {s} ___ now. ({v})', r, [x for x in [v, f'{b} {v}', ING[v], V3S.get(v, v + 's')] if x != r])
def pc2():
    v = ch(list(ING)); return mc(f'«{v}» + -ing = ?', ING[v], [x for x in {v + 'ing', v[:-1] + 'ing', v + v[-1] + 'ing', v + 'eing', v + 's'} if x != ING[v] and x != v[:-1] + 'ing' or (x == v[:-1] + 'ing' and v.endswith('e') and x != ING[v])])
def pc3():
    s, b = ch(SB); t = R.randrange(3)
    if t == 0: q = b.capitalize(); return mc(f'___ {s if s == "I" else s.lower()} watching TV now?', q, [x for x in ['Am', 'Is', 'Are', 'Do'] if x != q])
    if t == 1: return mc('Present Continuous qachon ishlatiladi?', 'Hozir, ayni paytda boʻlayotgan ish uchun', ['Har kuni takrorlanadigan ish uchun', 'Oʻtgan ish uchun', 'Doimiy haqiqat uchun'])
    neg = {'am': 'am not', 'is': "isn't", 'are': "aren't"}[b]; return mc(f'{s} ___ sleeping now. (inkor)', neg, [x for x in ['am not', "isn't", "aren't", "don't"] if x != neg])
B.topic(G, 'continuous', 'Present Continuous', [6], pc1, pc2, pc3, 'present continuous hozirgi davom zamon')

ED = {'play': 'played', 'watch': 'watched', 'study': 'studied', 'stop': 'stopped', 'live': 'lived', 'cry': 'cried', 'visit': 'visited', 'clean': 'cleaned',
      'dance': 'danced', 'plan': 'planned', 'help': 'helped', 'walk': 'walked', 'open': 'opened', 'carry': 'carried', 'like': 'liked', 'want': 'wanted'}
TY = ['yesterday', 'last week', 'two days ago', 'last Sunday', 'in 2020']
def pe1():
    v = ch(list(ED)); return mc(f'«{v}» feʼlining oʻtgan zamon (Past Simple) shakli?', ED[v], [x for x in {v + 'ed', v + 'd', v + 's', v + 'ing', v[:-1] + 'ied'} if x != ED[v]])
def pe2():
    v = ch(list(ED)); s = ch(['I', 'She', 'We', 'They', 'My father']); return mc(f'{s} ___ {OBJ.get(v, "my grandmother")} {ch(TY)}. ({v})', ED[v], [x for x in {v, V3S.get(v, v + 's'), ING.get(v, v + 'ing'), 'will ' + v} if x != ED[v]])
def pe3():
    t = R.randrange(3); v = ch(list(ED))
    if t == 0: return mc(f'___ you {v} {OBJ.get(v, "your friend")} yesterday?', 'Did', ['Do', 'Does', 'Were'])
    if t == 1: return mc(f'She ___ {v} {OBJ.get(v, "them")} last week. (inkor)', "didn't", ["don't", "doesn't", "wasn't"])
    return mc('Past Simple qachon ishlatiladi?', 'Oʻtmishda tugagan ish uchun', ['Hozir boʻlayotgan ish uchun', 'Kelajak uchun', 'Doimiy odat uchun'])
B.topic(G, 'pastreg', 'Past Simple: regular verbs (-ed)', [6], pe1, pe2, pe3, 'past simple oʻtgan zamon ed')

CMP = {'big': ('bigger', 'biggest'), 'tall': ('taller', 'tallest'), 'small': ('smaller', 'smallest'), 'fast': ('faster', 'fastest'), 'hot': ('hotter', 'hottest'),
       'happy': ('happier', 'happiest'), 'easy': ('easier', 'easiest'), 'good': ('better', 'best'), 'bad': ('worse', 'worst'),
       'beautiful': ('more beautiful', 'most beautiful'), 'interesting': ('more interesting', 'most interesting'), 'expensive': ('more expensive', 'most expensive'),
       'long': ('longer', 'longest'), 'old': ('older', 'oldest'), 'cold': ('colder', 'coldest'), 'nice': ('nicer', 'nicest'), 'young': ('younger', 'youngest')}
def cwr(a, r):
    c = {a + 'er', a + 'r', 'more ' + a, a + a[-1] + 'er', a[:-1] + 'ier', a + 'est', 'most ' + a, 'the ' + a}
    return [x for x in c if x != r]
def cm1():
    a = ch(['big', 'tall', 'small', 'fast', 'long', 'old', 'cold', 'young']); return mc(f'«{a}» — qiyosiy daraja (comparative)?', CMP[a][0], cwr(a, CMP[a][0]))
def cm2():
    a = ch(list(CMP)); t = R.randrange(2)
    if t == 0: return mc(f'«{a}» — qiyosiy daraja (comparative)?', CMP[a][0], cwr(a, CMP[a][0]))
    return mc(f'«{a}» — orttirma daraja (superlative)?', CMP[a][1], cwr(a, CMP[a][1]))
cm3 = [mc('An elephant is ___ than a dog.', 'bigger', ['big', 'biggest', 'more big']), mc('This is the ___ day of my life.', 'best', ['good', 'better', 'goodest']),
       mc('Summer is ___ than winter.', 'hotter', ['hot', 'hottest', 'more hot']), mc('This book is ___ than that one.', 'more interesting', ['interestinger', 'most interesting', 'interesting']),
       mc('Ali is the ___ boy in our class.', 'tallest', ['taller', 'tall', 'more tall']), mc('My test was ___ than yours.', 'worse', ['bad', 'badder', 'worst']),
       mc('Tashkent is ___ than Nukus.', 'bigger', ['big', 'more big', 'biggest']), mc('Which is the ___ month of the year? — January.', 'coldest', ['colder', 'cold', 'most cold']),
       mc('Maths is ___ than English for me.', 'easier', ['easyer', 'more easy', 'easiest']), mc('Qiyosiy darajada «than» nima maʼno beradi?', '…dan (koʻra)', ['eng', 'juda', 'va'])]
B.topic(G, 'daraja', 'Comparatives and superlatives', [6, 7], cm1, cm2, cm3, 'comparative superlative daraja')

CTR = [('Uzbekistan', 'Uzbek', 'Tashkent'), ('England', 'English', 'London'), ('France', 'French', 'Paris'), ('Germany', 'German', 'Berlin'),
       ('China', 'Chinese', 'Beijing'), ('Japan', 'Japanese', 'Tokyo'), ('Russia', 'Russian', 'Moscow'), ('Turkey', 'Turkish', 'Ankara'),
       ('Italy', 'Italian', 'Rome'), ('Spain', 'Spanish', 'Madrid'), ('Kazakhstan', 'Kazakh', 'Astana'), ('Egypt', 'Egyptian', 'Cairo')]
def ct1():
    c, n, p = ch(CTR); return mc(f'What is the capital of {c}?', p, R.sample([x[2] for x in CTR if x[2] != p], 3))
def ct2():
    c, n, p = ch(CTR); return mc(f'People from {c} are ___.', n if c != 'England' else 'English', R.sample([x[1] for x in CTR if x[1] != n], 3))
def ct3():
    c, n, p = ch(CTR); t = R.randrange(2)
    if t == 0: return mc(f'{p} is the capital of ___.', c, R.sample([x[0] for x in CTR if x[0] != c], 3))
    tp = typo(c); return mc('Qaysi davlat nomi toʻgʻri yozilgan?', c, tp) if len(tp) >= 3 else None
B.topic(L, 'davlat', 'Countries, nationalities, capitals', [6, 7], ct1, ct2, ct3, 'country nationality capital davlat poytaxt')

# ======================= 7–9-SINF =======================
IRV = [('go', 'went', 'gone'), ('see', 'saw', 'seen'), ('eat', 'ate', 'eaten'), ('drink', 'drank', 'drunk'), ('write', 'wrote', 'written'), ('take', 'took', 'taken'),
       ('give', 'gave', 'given'), ('come', 'came', 'come'), ('run', 'ran', 'run'), ('swim', 'swam', 'swum'), ('buy', 'bought', 'bought'), ('bring', 'brought', 'brought'),
       ('think', 'thought', 'thought'), ('teach', 'taught', 'taught'), ('catch', 'caught', 'caught'), ('make', 'made', 'made'), ('do', 'did', 'done'), ('have', 'had', 'had'),
       ('speak', 'spoke', 'spoken'), ('break', 'broke', 'broken'), ('begin', 'began', 'begun'), ('sing', 'sang', 'sung'), ('know', 'knew', 'known'), ('fly', 'flew', 'flown'),
       ('find', 'found', 'found'), ('sleep', 'slept', 'slept'), ('sit', 'sat', 'sat'), ('tell', 'told', 'told'), ('say', 'said', 'said'), ('leave', 'left', 'left'),
       ('meet', 'met', 'met'), ('put', 'put', 'put'), ('cut', 'cut', 'cut'), ('become', 'became', 'become'), ('choose', 'chose', 'chosen'), ('draw', 'drew', 'drawn'),
       ('drive', 'drove', 'driven'), ('forget', 'forgot', 'forgotten'), ('grow', 'grew', 'grown'), ('hear', 'heard', 'heard'), ('lose', 'lost', 'lost'),
       ('send', 'sent', 'sent'), ('stand', 'stood', 'stood'), ('throw', 'threw', 'thrown'), ('wear', 'wore', 'worn'), ('win', 'won', 'won'), ('read', 'read', 'read')]
EASY = ['go', 'see', 'eat', 'drink', 'write', 'come', 'run', 'buy', 'make', 'do', 'have', 'read', 'sit', 'swim']
def iwr(v, r, v2, v3):
    c = {v + 'ed', v + 'd', v2, v3, v, v + 's'}
    return [x for x in c if x != r]
def ir1():
    v, a, b = ch([x for x in IRV if x[0] in EASY]); return mc(f'«{v}» feʼlining oʻtgan zamon shakli (V2)?', a, iwr(v, a, a, b))
def ir2():
    v, a, b = ch(IRV); s = ch(['I', 'She', 'We', 'They', 'My brother']); return mc(f'«{v}» → V2 shakli qaysi?', a, iwr(v, a, a, b)) if R.random() < .5 else mc(f'{s} ___ yesterday. ({v})', a, iwr(v, a, a, b))
def ir3():
    v, a, b = ch(IRV); return mc(f'«{v}» feʼlining uchinchi shakli (V3, past participle)?', b, iwr(v, b, a, b))
B.topic(G, 'irregular', 'Irregular verbs (V1 – V2 – V3)', [7, 8], ir1, ir2, ir3, 'irregular verbs notoʻgʻri feʼllar')

FUT = [('Tomorrow I ___ my grandmother.', 'visit'), ('Next year she ___ to university.', 'go'), ('I think it ___ tomorrow.', 'rain'), ('They ___ us next week.', 'help'),
       ('We ___ a new house next summer.', 'buy'), ('He ___ you later.', 'call'), ('I ___ you a letter soon.', 'write'), ('The film ___ at 7 o’clock.', 'start')]
def fu1():
    q, v = ch(FUT); r = 'will ' + v; return mc(q + f' ({v})', r, [v, v + 'ed' if not v.endswith('e') else v + 'd', 'will ' + v + 's', v + 'ing'][:4] if True else [])
fu2 = [mc('Look at the clouds! It ___ rain.', 'is going to', ['will to', 'going', 'is go to']), mc('I ___ visit my uncle next Sunday. (reja)', 'am going to', ['is going to', 'are going to', 'going to']),
       mc('She ___ buy a new dress. (reja)', 'is going to', ['are going to', 'am going to', 'go to']), mc('They ___ play football tomorrow. (reja)', 'are going to', ['is going to', 'am going to', 'going']),
       mc('«will» qaysi zamonni bildiradi?', 'Kelasi zamon', ['Oʻtgan zamon', 'Hozirgi zamon', 'Hozirgi davom zamon']), mc("«won't» = ?", 'will not', ['want not', 'would not', 'was not']),
       mc('___ you help me tomorrow?', 'Will', ['Do', 'Did', 'Are']), mc('I promise I ___ be late.', "won't", ["don't", "didn't", "isn't"])]
fu3 = [mc('«going to» qachon ishlatiladi?', 'Oldindan rejalashtirilgan ish uchun', ['Oʻtgan ish uchun', 'Har kungi odat uchun', 'Hozir boʻlayotgan ish uchun']),
       mc('— The phone is ringing. — I ___ answer it! (hozir qaror)', "'ll", ["'m going to", "'m", "'d"]), mc('We are going ___ the museum on Saturday.', 'to visit', ['visit', 'visiting', 'visited']),
       mc('Next year I ___ 15 years old.', 'will be', ['am', 'was', 'will']), mc('She ___ come to the party. She is ill. (inkor)', "won't", ["isn't", "doesn't", "didn't"]),
       mc('What ___ you do tomorrow?', 'will', ['did', 'do', 'are']), mc('They ___ to travel to Samarkand next week. (reja)', 'are going', ['is going', 'will', 'going'])]
B.topic(G, 'kelasi', 'Future: will / going to', [7], fu1, fu2, fu3, 'future will going to kelasi zamon')

OPP = [('big', 'small'), ('hot', 'cold'), ('tall', 'short'), ('fast', 'slow'), ('happy', 'sad'), ('rich', 'poor'), ('easy', 'difficult'), ('open', 'closed'),
       ('clean', 'dirty'), ('heavy', 'light'), ('early', 'late'), ('cheap', 'expensive'), ('strong', 'weak'), ('empty', 'full'), ('young', 'old'), ('long', 'short'), ('new', 'old')]
def op1():
    a, b = ch(OPP[:8]); return mc(f'«{a}» soʻzining antonimi (opposite) qaysi?', b, R.sample([x[1] for x in OPP if x[1] != b and x[0] != a], 3))
def op2():
    a, b = ch(OPP); t = R.randrange(2)
    if t == 0: return mc(f'«{a}» soʻzining antonimi (opposite) qaysi?', b, R.sample([x[1] for x in OPP if x[1] != b and x[0] != a], 3))
    return mc(f'«{b}» soʻzining antonimi (opposite) qaysi?', a, R.sample([x[0] for x in OPP if x[0] != a and x[1] != b], 3))
op3 = [mc('The opposite of «young» is ___.', 'old', ['new', 'small', 'short']), mc('The opposite of «new» is ___.', 'old', ['young', 'small', 'slow']),
       mc('The glass is not empty. It is ___.', 'full', ['open', 'heavy', 'cheap']), mc('This bag is not heavy. It is ___.', 'light', ['dark', 'empty', 'weak']),
       mc('The shop is not open. It is ___.', 'closed', ['empty', 'cheap', 'dirty']), mc('He is not rich. He is ___.', 'poor', ['weak', 'sad', 'cheap']),
       mc('The test was not easy. It was ___.', 'difficult', ['heavy', 'slow', 'expensive']), mc('My room is not dirty. It is ___.', 'clean', ['empty', 'light', 'full']),
       mc('The car is not cheap. It is ___.', 'expensive', ['heavy', 'difficult', 'strong']), mc('I didn’t come late. I came ___.', 'early', ['fast', 'young', 'soon'])]
B.topic(L, 'antonim', 'Opposites — Antonim sifatlar', [7], op1, op2, op3, 'opposites antonym')

TIM = [('Monday', 'on'), ('5 o’clock', 'at'), ('July', 'in'), ('2020', 'in'), ('winter', 'in'), ('the morning', 'in'), ('night', 'at'), ('my birthday', 'on'),
       ('noon', 'at'), ('Sunday morning', 'on'), ('the evening', 'in'), ('the 1st of September', 'on'), ('half past seven', 'at'), ('summer', 'in'), ('Friday', 'on'), ('midnight', 'at')]
def tm1():
    w, p = ch(TIM); return mc(f'___ {w}', p, [x for x in ['in', 'on', 'at', 'to'] if x != p])
tm2 = tm1
tm3 = [mc('Oylar va yillar oldidan qaysi predlog?', 'in', ['on', 'at', 'to']), mc('Hafta kunlari oldidan qaysi predlog?', 'on', ['in', 'at', 'to']),
       mc('Aniq soat (vaqt) oldidan qaysi predlog?', 'at', ['in', 'on', 'to']), mc('I was born ___ 2012.', 'in', ['on', 'at', 'to']),
       mc('The lesson starts ___ 8:30.', 'at', ['in', 'on', 'to']), mc('We have English ___ Tuesdays.', 'on', ['in', 'at', 'to']),
       mc('It is cold ___ winter.', 'in', ['on', 'at', 'to']), mc('I go to bed ___ 10 o’clock.', 'at', ['in', 'on', 'to']), mc('Navruz is ___ the 21st of March.', 'on', ['in', 'at', 'to']),
       mc('I don’t sleep ___ the afternoon.', 'in', ['on', 'at', 'to'])]
B.topic(G, 'vaqtpre', 'Prepositions of time: in, on, at', [7, 8], tm1, tm2, tm3, 'prepositions time in on at')

PP = [('finish', 'finished'), ('see', 'seen'), ('do', 'done'), ('write', 'written'), ('visit', 'visited'), ('eat', 'eaten'), ('read', 'read'), ('lose', 'lost'), ('buy', 'bought'), ('clean', 'cleaned')]
PS = [('I', 'have'), ('She', 'has'), ('We', 'have'), ('He', 'has'), ('They', 'have'), ('My sister', 'has')]
PPO = {'finish': 'the homework', 'see': 'this film', 'do': 'the exercise', 'write': 'a letter', 'visit': 'Samarkand', 'eat': 'my breakfast', 'read': 'this book',
       'lose': 'my key', 'buy': 'a new bag', 'clean': 'my room'}
def pp1():
    (v, p), (s_, h) = ch(PP), ch(PS); r = f'{h} {p}'; o = 'has' if h == 'have' else 'have'
    return mc(f'{s_} ___ {PPO[v]}. ({v})', r, [f'{o} {p}', f'{h} {v}', f'is {ING.get(v, v + "ing")}'])
def pp2():
    v, a, b = ch(IRV); return mc(f'Present Perfect: I have ___ (V3 of «{v}»).', b, iwr(v, b, a, b))
pp3 = [mc('Present Perfect qanday tuziladi?', 'have / has + V3', ['was / were + V-ing', 'will + V1', 'do / does + V1']),
       mc('Have you ever ___ to London?', 'been', ['be', 'was', 'being']), mc('She has ___ finished her work. (allaqachon)', 'already', ['yet', 'ever', 'ago']),
       mc('Have you done your homework ___?', 'yet', ['already', 'ago', 'never']), mc('I have ___ seen a tiger. (hech qachon)', 'never', ['ever', 'yet', 'already']),
       mc('We have lived here ___ 2015.', 'since', ['for', 'ago', 'from']), mc('They have known each other ___ ten years.', 'for', ['since', 'ago', 'during']),
       mc('___ you ever eaten sushi?', 'Have', ['Did', 'Do', 'Are']), mc('He ___ just come home.', 'has', ['have', 'is', 'did']), mc('I ___ lost my key. I can’t open the door.', 'have', ['has', 'am', 'was'])]
B.topic(G, 'perfect', 'Present Perfect', [8, 9], pp1, pp2, pp3, 'present perfect have has V3')

MOD = [('You ___ stop at a red light. (majburiyat)', 'must'), ('You ___ see a doctor. (maslahat)', 'should'), ('I ___ swim very well. (qobiliyat)', 'can'),
       ('Pupils ___ not run in the corridor. (taqiq)', 'must'), ('You look tired. You ___ go to bed. (maslahat)', 'should'), ('___ I open the window? (ruxsat)', 'May'),
       ('She ___ speak three languages. (qobiliyat)', 'can'), ('We ___ wear a uniform at school. (qoida)', 'must'), ('You ___ eat so many sweets. (maslahat, inkor)', "shouldn't"),
       ('When I was five, I ___ read. (oʻtmishdagi qobiliyat)', 'could')]
MODL = ['must', 'should', 'can', 'may', "shouldn't", 'could', 'will']
def md():
    q, a = ch(MOD); bad = {'can': 'could', 'could': 'can', 'must': "mustn't"}.get(a, '')
    return mc(q, a, R.sample([x for x in MODL if x.lower() != a.lower() and x != bad], 3))
md3 = [mc('«must» nimani bildiradi?', 'majburiyat, zarurat', ['maslahat', 'qobiliyat', 'ruxsat soʻrash']), mc('«should» nimani bildiradi?', 'maslahat', ['qobiliyat', 'majburiyat (qatʼiy)', 'oʻtmish']),
       mc('«can» nimani bildiradi?', 'qobiliyat, imkoniyat', ['maslahat', 'majburiyat', 'kelajak']), mc('«could» qaysi feʼlning oʻtgan shakli?', 'can', ['will', 'must', 'should']),
       mc('Modal feʼldan keyin feʼl qanday keladi?', 'to siz, oddiy shaklda (V1)', ['-ing bilan', 'to bilan', 'V2 shaklida']), mc('He must ___ his homework.', 'do', ['to do', 'does', 'doing']),
       mc("«mustn't» nimani bildiradi?", 'taqiq (mumkin emas)', ['shart emas', 'maslahat', 'qobiliyat']), mc('You ___ smoke here. It is forbidden.', "mustn't", ["don't have to", 'should', 'can'])] + [md() for _ in range(4)]
B.topic(G, 'modal', 'Modal verbs: can, must, should, may', [8], md, md, md3, 'modal verbs can must should may')

PAS = [('The house ___ built in 1990.', 'was'), ('English ___ spoken in many countries.', 'is'), ('The letter ___ written by Ali.', 'was'), ('Cars ___ made in this factory.', 'are'),
       ('The window ___ broken yesterday.', 'was'), ('These books ___ written by Navoiy.', 'were'), ('Cotton ___ grown in Uzbekistan.', 'is'), ('The cakes ___ eaten at the party.', 'were'),
       ('The room ___ cleaned every day.', 'is'), ('The new school ___ opened last year.', 'was'), ('Apples ___ sold at the market.', 'are'), ('The pictures ___ painted by my sister.', 'were')]
def pa():
    q, a = ch(PAS); return mc(q, a, [x for x in ['is', 'are', 'was', 'were', 'be'] if x != a])
pa3 = [mc('Passive Voice qanday tuziladi?', 'to be + V3', ['have + V3', 'will + V1', 'to be + V-ing']), mc('The book was ___ by a famous writer.', 'written', ['wrote', 'write', 'writing']),
       mc('The bridge was ___ in 2015.', 'built', ['build', 'building', 'builded']), mc('The thief was ___ by the police.', 'caught', ['catched', 'catch', 'catching']),
       mc('«Ali wrote the letter» → Passive?', 'The letter was written by Ali.', ['The letter wrote by Ali.', 'Ali was written the letter.', 'The letter is write by Ali.']),
       mc('Passive gapda bajaruvchi qaysi predlog bilan beriladi?', 'by', ['with', 'from', 'of']), mc('Rice ___ in Asia.', 'is grown', ['grows', 'is grow', 'growing']),
       mc('The song was ___ by a famous singer.', 'sung', ['sang', 'sing', 'singed'])] + [pa() for _ in range(4)]
B.topic(G, 'passive', 'Passive Voice', [9], pa, pa, pa3, 'passive voice majhul nisbat')

CND = [('If it rains, I ___ at home.', 'will stay'), ('If you study hard, you ___ the exam.', 'will pass'), ('If she comes, we ___ to the park.', 'will go'),
       ('If I have time, I ___ you.', 'will call'), ('If they hurry, they ___ the bus.', 'will catch'),
       ('If you water the plants, they ___.', 'will grow'), ('If we leave now, we ___ on time.', 'will be'), ('If he asks me, I ___ him.', 'will help'), ('If the weather is nice, we ___ a picnic.', 'will have')]
def cd1():
    q, a = ch(CND); v = a.split()[-1]; return mc(q, a, [v, 'would ' + v, v + 'ing', 'will to ' + v])
cd2 = [mc('If it ___ tomorrow, we will stay at home.', 'rains', ['will rain', 'rained', 'raining']), mc('If you ___ me, I will help you.', 'call', ['will call', 'called', 'calling']),
       mc('If he ___ hard, he will win.', 'trains', ['will train', 'train', 'trained']), mc('If we ___ now, we will be on time.', 'leave', ['will leave', 'left', 'leaving']),
       mc('First Conditional: If + Present Simple, … ?', 'will + V1', ['would + V1', 'Past Simple', 'had + V3']), mc('If you mix red and white, you ___ pink.', 'get', ['got', 'would got', 'getting'])] + [cd1() for _ in range(5)]
cd3 = [mc('If I ___ rich, I would buy a big house.', 'were', ['am', 'will be', 'be']), mc('If I had wings, I ___ fly.', 'would', ['will', 'can', 'did']),
       mc('If she knew the answer, she ___ tell us.', 'would', ['will', 'does', 'is']), mc('Second Conditional qanday vaziyat uchun?', 'Hozirgi paytdagi haqiqatga zid, xayoliy vaziyat', ['Real kelajak', 'Oʻtgan voqea', 'Doimiy haqiqat']),
       mc('If I ___ you, I would study more.', 'were', ['am', 'was being', 'will be']), mc('Zero Conditional: If you heat water to 100°C, it ___.', 'boils', ['will boiled', 'boiled', 'would boils']),
       mc('If we had a car, we ___ travel more.', 'would', ['will', 'are', 'had']), mc('If he ___ more, he would be healthier.', 'exercised', ['exercises', 'will exercise', 'exercising'])] + [cd1() for _ in range(3)]
B.topic(G, 'shart', 'Conditionals (If …)', [9], cd1, cd2, cd3, 'conditionals if shart gap')


PCS = [('I', 'was'), ('He', 'was'), ('She', 'was'), ('We', 'were'), ('They', 'were'), ('My parents', 'were'), ('You', 'were'), ('Ali', 'was')]
PCA = [('watch', 'TV'), ('read', 'a book'), ('cook', 'dinner'), ('play', 'football'), ('sleep', ''), ('do', 'homework')]
PCI = {'watch': 'watching', 'read': 'reading', 'cook': 'cooking', 'play': 'playing', 'sleep': 'sleeping', 'do': 'doing'}
def pcn1():
    (s_, b), (v, o) = ch(PCS), ch(PCA); r = f'{b} {PCI[v]}'; o2 = 'were' if b == 'was' else 'was'
    return mc(f'{s_} ___ {o} at 8 o’clock yesterday. ({v})'.replace('  ', ' '), r, [f'{o2} {PCI[v]}', f'is {PCI[v]}', ED.get(v, {'read': 'read', 'sleep': 'slept', 'do': 'did'}.get(v))])
def pcn2():
    (s_, b), (v, o) = ch(PCS), ch(PCA); r = f'{b} {PCI[v]}'
    return mc(f'{s_} ___ {o} when the phone rang. ({v})'.replace('  ', ' '), r, [f'{"were" if b == "was" else "was"} {PCI[v]}', f'{b} {v}', f'will {v}'])
pcn3 = [mc('Past Continuous qanday tuziladi?', 'was / were + V-ing', ['have + V3', 'did + V1', 'will + V-ing']), mc('Past Continuous nimani bildiradi?', 'Oʻtmishda maʼlum paytda davom etayotgan ishni', ['Hozir boʻlayotgan ishni', 'Kelajakni', 'Doimiy odatni']),
        mc('What ___ you doing at 9 pm yesterday?', 'were', ['was', 'did', 'are']), mc('She ___ sleeping when I came.', 'was', ['were', 'is', 'did']),
        mc('While I ___ dinner, my sister was reading.', 'was cooking', ['cooked', 'am cooking', 'were cooking']), mc('They ___ playing at that time. (inkor)', "weren't", ["wasn't", "didn't", "aren't"]),
        mc('___ he working yesterday at 5?', 'Was', ['Were', 'Did', 'Is']), mc('I was walking home when it ___ to rain.', 'started', ['was starting', 'starts', 'start'])]
B.topic(G, 'pastcont', 'Past Continuous', [8], pcn1, pcn2, pcn3, 'past continuous oʻtgan davom zamon')

SA = [('I have ___ apples.', 'some'), ('There isn’t ___ milk.', 'any'), ('Are there ___ books on the desk?', 'any'), ('Would you like ___ tea?', 'some'),
      ('We don’t have ___ bread.', 'any'), ('She bought ___ flowers.', 'some'), ('Is there ___ sugar?', 'any'), ('There are ___ children in the park.', 'some'),
      ('I didn’t see ___ birds.', 'any'), ('Can I have ___ water, please?', 'some'), ('He hasn’t got ___ friends here.', 'any'), ('There is ___ cheese in the fridge.', 'some')]
def sa():
    q, a = ch(SA); return mc(q, a, [x for x in ['some', 'any', 'a', 'an'] if x != a])
sa3 = [mc('«any» odatda qanday gaplarda ishlatiladi?', 'Inkor va soʻroq gaplarda', ['Faqat darak gaplarda', 'Faqat buyruq gaplarda', 'Hech qayerda']),
       mc('«some» odatda qanday gaplarda ishlatiladi?', 'Darak gaplarda va taklif/iltimosda', ['Faqat inkor gaplarda', 'Faqat soʻroq gaplarda', 'Hech qayerda']),
       mc('There is ___ in the room. (hech kim)', 'nobody', ['somebody', 'anybody', 'everybody']), mc('Is there ___ at home? (kimdir)', 'anybody', ['nobody', 'somebody', 'nothing']),
       mc('I want to eat ___. (biror narsa)', 'something', ['anything', 'nothing', 'nobody']), mc('I don’t know ___ about it.', 'anything', ['something', 'nothing', 'somebody'])] + [sa() for _ in range(4)]
B.topic(G, 'someany', 'Some / any', [7, 8], sa, sa, sa3, 'some any')

REL = [('The man ___ lives next door is a doctor.', 'who'), ('The book ___ I read was interesting.', 'which'), ('This is the house ___ I was born.', 'where'),
       ('The girl ___ sings well is my sister.', 'who'), ('I have a cat ___ likes milk.', 'which'), ('This is the school ___ I study.', 'where'),
       ('The teacher ___ teaches us English is kind.', 'who'), ('The film ___ we watched was funny.', 'which'), ('Samarkand is the city ___ Amir Temur lived.', 'where'),
       ('People ___ work hard succeed.', 'who'), ('The bus ___ goes to the centre is here.', 'which'), ('The park ___ we play football is near.', 'where')]
def rl():
    q, a = ch(REL); return mc(q, a, [x for x in ['who', 'which', 'where', 'when', 'what'] if x != a])
rl3 = [mc('«who» qachon ishlatiladi?', 'Odamlar haqida', ['Narsalar haqida', 'Joy haqida', 'Vaqt haqida']), mc('«which» qachon ishlatiladi?', 'Narsa va hayvonlar haqida', ['Odamlar haqida', 'Joy haqida', 'Sabab haqida']),
       mc('«where» qachon ishlatiladi?', 'Joy haqida', ['Odamlar haqida', 'Narsalar haqida', 'Vaqt haqida']), mc('I remember the day ___ we met.', 'when', ['who', 'which', 'where']),
       mc('«that» qaysi soʻzlar oʻrnida ishlatilishi mumkin?', 'who va which', ['where va when', 'faqat where', 'hech qaysi'])] + [rl() for _ in range(5)]
B.topic(G, 'relative', 'Relative pronouns: who, which, where', [9], rl, rl, rl3, 'relative pronouns who which where')

WF = [('happy', 'unhappy', 'qarama-qarshi maʼno (un-)'), ('possible', 'impossible', 'qarama-qarshi maʼno (im-)'), ('agree', 'disagree', 'qarama-qarshi maʼno (dis-)'),
      ('teach', 'teacher', 'kasb egasi (-er)'), ('sing', 'singer', 'kasb egasi (-er)'), ('kind', 'kindness', 'mavhum ot (-ness)'), ('happy', 'happiness', 'mavhum ot (-ness)'),
      ('care', 'careful', 'sifat (-ful)'), ('help', 'helpful', 'sifat (-ful)'), ('home', 'homeless', 'sifat (-less)'), ('quick', 'quickly', 'ravish (-ly)'), ('slow', 'slowly', 'ravish (-ly)'),
      ('friend', 'friendly', 'sifat (-ly)'), ('danger', 'dangerous', 'sifat (-ous)'), ('build', 'building', 'ot (-ing)')]
def wf1():
    a, b, m = ch(WF); return mc(f'«{a}» → ___ ({m})', b, [x for x in {a + 'er', 'un' + a, a + 'ness', a + 'ful', a + 'ly', 'dis' + a, a + 'less'} if x != b])
def wf2():
    a, b, m = ch(WF); return mc(f'«{b}» soʻzi qaysi soʻzdan yasalgan?', a, R.sample([x[0] for x in WF if x[0] != a], 3))
wf3 = [mc('She speaks very ___. (slow)', 'slowly', ['slow', 'slowness', 'slowful']), mc('Be ___! The road is wet. (care)', 'careful', ['careless', 'carefully', 'caring']),
       mc('My brother is a good ___. (sing)', 'singer', ['singing', 'song', 'singly']), mc('Thank you for your ___. (kind)', 'kindness', ['kindly', 'kindful', 'unkind']),
       mc('It is ___ to swim here. It is dangerous. (possible)', 'impossible', ['unpossible', 'dispossible', 'possibly']), mc('I ___ with you. (agree, inkor)', 'disagree', ['unagree', 'inagree', 'agreeless']),
       mc('The dog was ___. It had no home. (home)', 'homeless', ['homeful', 'homely', 'unhome']), mc('This snake is very ___. (danger)', 'dangerous', ['dangerful', 'dangerly', 'endanger']),
       mc('«-er» qoʻshimchasi koʻpincha nimani yasaydi?', 'Shaxs, kasb egasini', ['Ravishni', 'Inkor maʼnoni', 'Koʻplikni']), mc('«-ly» qoʻshimchasi koʻpincha nimani yasaydi?', 'Ravishni', ['Kasbni', 'Koʻplikni', 'Oʻtgan zamonni'])]
B.topic(L, 'yasalish', 'Word formation: prefixes and suffixes', [8, 9], wf1, wf2, wf3, 'word formation suffix prefix soʻz yasalishi')

B.save()
