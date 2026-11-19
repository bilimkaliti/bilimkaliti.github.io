# -*- coding: utf-8 -*-
"""Matematika savollar bazasi: games/baza/matematika.json
Har bir mavzu: 3 daraja (d=1 oson, 2 oʻrta, 3 qiyin), har darajada 10 tagacha savol.
Hisob-kitob savollari dastur bilan yaratiladi (javob xatosiz), nazariy savollar qoʻlda yozilgan.
Ishga tushirish: python3 src_baza/matematika.py
"""
import json, random, os
from fractions import Fraction as F
from math import gcd

N = 10  # har darajada savollar soni
R = random.Random(2026)
ri = lambda a, b: R.randint(a, b)
ch = R.choice

def sp(n):  # 12345 -> "12 345"
    s = str(abs(n)); out = ''
    while len(s) > 3: out = ' ' + s[-3:] + out; s = s[:-3]
    return ('−' if n < 0 else '') + s + out

def num(q, a):
    assert isinstance(a, int) and 0 <= a <= 9999, (q, a)
    return {'q': q, 'a': a}

def mc(q, right, wrongs):
    right = str(right); ws = []
    for w in wrongs:
        w = str(w)
        if w != right and w not in ws: ws.append(w)
    if len(ws) < 3: return None
    o = ws[:3]; c = R.randrange(4); o.insert(c, right)
    return {'q': q, 'o': o, 'c': c}

def nwr(a, k=(1, -1, 10, -10, 2)):  # sonli xato variantlar
    return [a + d for d in k if a + d >= 0]

SUP = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
def up(n): return str(n).translate(SUP)
def cf(c, v): return v if c == 1 else f'{c}{v}'
def neg(n): return ('−' + str(-n)) if n < 0 else str(n)
def par(n): return f'({neg(n)})' if n < 0 else str(n)

def fr(x):
    x = F(x)
    if x.denominator == 1: return neg(x.numerator)
    s = '−' if x < 0 else ''; x = abs(x)
    w, r = divmod(x.numerator, x.denominator)
    return s + (f'{w} {r}/{x.denominator}' if w else f'{r}/{x.denominator}')

def fwr(x):  # kasr uchun xato variantlar
    x = F(x); n, d = x.numerator, x.denominator
    c = [F(n + 1, d), F(max(n - 1, 1), d), F(n, d + 1), F(d, n) if n else F(1, d + 1), F(n + d, d), F(n, d * 2), F(n * 2, d)]
    return [fr(v) for v in c if v != x and v > 0]

def dec(x, nd=2):  # o'nli kasr vergul bilan
    s = f'{x:.{nd}f}'.rstrip('0').rstrip('.')
    return s.replace('.', ',')

def collect(gen, n=N, tries=400):
    out, seen = [], set()
    for _ in range(tries):
        it = gen()
        if it is None: continue
        key = it['q'] + ('|'.join(sorted(it['o'])) if 'o' in it and it['q'].startswith('Qaysi') else '')
        if key in seen: continue
        seen.add(key); out.append(it)
        if len(out) >= n: break
    return out

def fixed(lst):  # qoʻlda yozilgan savollar (aralashtirilgan)
    l = [x for x in lst if x]; R.shuffle(l); return l[:N]

TOPICS = []
def topic(bob, tid, name, g1, g2, g3):
    items = []
    for d, g in ((1, g1), (2, g2), (3, g3)):
        lst = g() if callable(g) and getattr(g, 'fixed', False) else (fixed(g) if isinstance(g, list) else collect(g))
        assert len(lst) >= 5, (tid, d, len(lst))
        for it in lst: it['d'] = d; items.append(it)
    TOPICS.append({'id': tid, 'bob': bob, 'name': name, 'items': items})

B1 = 'Natural sonlar ustida amallar'; B2 = 'Sonlar'; B3 = 'Sonning boʻlinishi'; B4 = 'Kasrlar'; B5 = 'Oʻnli kasrlar'
B6 = 'Algebraik ifoda va tenglamalar'; B7 = 'Matnli masalalar'; B9 = 'Tenglamalar sistemasi va masalalar'
B10 = 'Planimetriya'; B11 = 'Stereometriya'

# ================= 1-BOB =================
def add(lo1, hi1, lo2, hi2):
    def g():
        a, b = ri(lo1, hi1), ri(lo2, hi2)
        return num(f'{sp(a)} + {sp(b)} = ?', a + b) if a + b <= 9999 else None
    return g
topic(B1, 'qoshish', 'Natural sonlarni qoʻshish', add(12, 89, 11, 89), add(120, 899, 45, 899), add(1200, 6999, 150, 2999))

def sub(lo, hi, lo2, hi2):
    def g():
        a, b = ri(lo, hi), ri(lo2, hi2)
        return num(f'{sp(a)} − {sp(b)} = ?', a - b) if a > b else None
    return g
topic(B1, 'ayirish', 'Natural sonlarni ayirish', sub(30, 99, 11, 60), sub(300, 999, 45, 299), sub(2000, 9999, 199, 1999))

topic(B1, 'kopaytirish', 'Natural sonlarni koʻpaytirish',
      lambda: num(f'{(a:=ri(3,9))} · {(b:=ri(3,9))} = ?', a * b),
      lambda: num(f'{(a:=ri(12,99))} · {(b:=ri(3,9))} = ?', a * b),
      lambda: (lambda a, b: num(f'{a} · {b} = ?', a * b) if a * b <= 9999 else None)(ri(12, 99), ri(11, 99)))

topic(B1, 'bolish', 'Natural sonlarni boʻlish',
      lambda: (lambda a, b: num(f'{a * b} : {b} = ?', a))(ri(3, 9), ri(3, 9)),
      lambda: (lambda a, b: num(f'{a * b} : {b} = ?', a))(ri(12, 99), ri(3, 9)),
      lambda: (lambda a, b: num(f'{sp(a * b)} : {b} = ?', a) if a * b <= 9999 else None)(ri(21, 199), ri(11, 48)))

def ar1():
    a, b, c = ri(2, 20), ri(2, 9), ri(2, 9)
    return ch([num(f'{a} + {b} · {c} = ?', a + b * c), num(f'{a * c + b * c} − {b} · {c} = ?', a * c)])
def ar2():
    a, b, c = ri(10, 30), ri(2, 9), ri(2, 9)
    if a <= b: return None
    return ch([num(f'({a} − {b}) · {c} = ?', (a - b) * c), num(f'({a} + {b}) · {c} = ?', (a + b) * c), num(f'{c * b * 2} : {b} + {a} = ?', c * 2 + a)])
def ar3():
    b, c = ri(2, 8), ri(2, 8); a = (b + c) * ri(2, 9); d, e = ri(3, 9), ri(3, 9)
    return ch([num(f'{a} : ({b} + {c}) + {d} · {e} = ?', a // (b + c) + d * e), num(f'{d} · {e} − {a} : ({b} + {c}) = ?', d * e - a // (b + c)) if d * e > a // (b + c) else None])
topic(B1, 'aralash', 'Natural sonlar ustida aralash amallar', ar1, ar2, ar3)

def te1():
    x, a = ri(5, 60), ri(3, 40)
    return ch([num(f'x + {a} = {x + a}. x = ?', x), num(f'x − {a} = {x}. x = ?', x + a), num(f'{x + a} − x = {a}. x = ?', x)])
def te2():
    x, a = ri(3, 15), ri(2, 9)
    return ch([num(f'{a}x = {a * x}. x = ?', x), num(f'x : {a} = {x}. x = ?', x * a), num(f'{a * x} : x = {a}. x = ?', x)])
def te3():
    x, a, b = ri(2, 15), ri(2, 9), ri(1, 30)
    return ch([num(f'{a}x + {b} = {a * x + b}. x = ?', x), num(f'{a}x − {b} = {a * x - b}. x = ?', x) if a * x > b else None, num(f'{a}(x + {b}) = {a * (x + b)}. x = ?', x)])
topic(B1, 'tenglama1', 'Chiziqli tenglamalar (sodda)', te1, te2, te3)

# ================= 2-BOB =================
def xona():
    n = ri(1000, 9999); s = str(n); k = ri(0, 3)
    nm = ['minglar', 'yuzlar', 'oʻnlar', 'birlar'][k]
    return num(f'{sp(n)} sonida {nm} xonasidagi raqam nechaga teng?', int(s[k]))
def xona3():
    n = ri(1000, 9999)
    return ch([num(f'{sp(n)} sonida nechta yuzlik bor? (jami)', n // 100), num(f'{sp(n)} sonida nechta oʻnlik bor? (jami)', n // 10) if n // 10 <= 9999 else None])
nolsonlar1 = [mc('Eng kichik natural son qaysi?', 1, [0, 2, 10]), num('Eng katta bir xonali son nechaga teng?', 9), num('Eng kichik ikki xonali son nechaga teng?', 10),
              num('Eng katta ikki xonali son nechaga teng?', 99), mc('Nol natural sonmi?', 'Yoʻq', ['Ha', 'Faqat juft boʻlsa', 'Baʼzan']),
              num('Eng kichik uch xonali son nechaga teng?', 100), num('Eng katta uch xonali son nechaga teng?', 999), num('Eng kichik toʻrt xonali son nechaga teng?', 1000),
              num('Ikki xonali sonlar nechta?', 90), num('Bir xonali natural sonlar nechta?', 9), mc('Natural sonlar qatori qaysi son bilan boshlanadi?', 1, [0, 2, '−1'])]
nolsonlar3 = [num('Uch xonali sonlar nechta?', 900), num('Raqamlari har xil boʻlgan eng katta uch xonali son?', 987), num('Raqamlari har xil boʻlgan eng kichik uch xonali son?', 102),
              num('Eng katta toʻrt xonali son nechaga teng?', 9999), num('Raqamlari yigʻindisi 27 ga teng uch xonali son?', 999), num('Eng kichik toʻrt xonali juft son?', 1000),
              num('Eng katta uch xonali toq son?', 999), num('Eng katta ikki xonali juft son?', 98), num('Raqamlari har xil boʻlgan eng katta ikki xonali son?', 98),
              num('Raqamlari har xil boʻlgan eng kichik toʻrt xonali son?', 1023), num('1 dan 20 gacha nechta toq son bor?', 10)]
topic(B2, 'natural', 'Nol va natural sonlar, xona birliklari', nolsonlar1, xona, lambda: ch([xona3, lambda: ch(nolsonlar3)])())

def tq1():
    a, b = ri(100, 9999), ri(100, 9999)
    if R.random() < .15: b = a
    return mc(f'{sp(a)} ☐ {sp(b)}. Qaysi belgi qoʻyiladi?', '>' if a > b else '<' if a < b else '=', ['>', '<', '=', '≥'])
def tq2():
    n = ri(101, 9989)
    if R.random() < .5: return num(f'{sp(n)} ni oʻnlargacha yaxlitlang.', round(n / 10 + 1e-9) * 10 if n % 10 != 5 else (n // 10 + 1) * 10)
    return num(f'{sp(n)} ni yuzlargacha yaxlitlang.', ((n + 50) // 100) * 100)
def tq3():
    n = ri(1001, 9499)
    return ch([num(f'{sp(n)} ni minglargacha yaxlitlang.', ((n + 500) // 1000) * 1000), num(f'{sp(n)} ni yuzlargacha yaxlitlang.', ((n + 50) // 100) * 100)])
topic(B2, 'taqqoslash', 'Natural sonlarni taqqoslash va yaxlitlash', tq1, tq2, tq3)

def seq1():
    a, d = ri(1, 20), ri(2, 12); s = [a + d * i for i in range(5)]
    return num(f'Ketma-ketlikni davom ettiring: {", ".join(map(str, s[:4]))}, ?', s[4])
def seq2():
    t = ri(0, 2)
    if t == 0: a, q = ri(1, 5), ri(2, 3); s = [a * q ** i for i in range(5)]
    elif t == 1: a, d = ri(60, 120), ri(3, 9); s = [a - d * i for i in range(5)]
    else: a = ri(1, 5); s = [a, a + 1, a + 3, a + 6, a + 10]
    return num(f'Ketma-ketlikni davom ettiring: {", ".join(map(str, s[:4]))}, ?', s[4])
def seq3():
    t = ri(0, 3)
    if t == 0: k = ri(1, 5); s = [(k + i) ** 2 for i in range(5)]
    elif t == 1: a, b = ri(1, 4), ri(1, 5); s = [a, b]; [s.append(s[-1] + s[-2]) for _ in range(4)]; s = s[:6]
    elif t == 2: a = ri(1, 9); s = [a, a * 2 + 1]; [s.append(s[-1] * 2 + 1) for _ in range(3)]
    else: k = ri(1, 4); s = [(k + i) ** 3 for i in range(5)]
    return num(f'Qonuniyatni toping: {", ".join(map(str, s[:-1]))}, ?', s[-1]) if s[-1] <= 9999 else None
topic(B2, 'boshqotirma', 'Boshqotirmalar: sonlar ketma-ketligi', seq1, seq2, seq3)

def bs1():
    a, b = ri(2, 30), ri(2, 30)
    t = ri(0, 2)
    if t == 0: return mc(f'{neg(-a)} ☐ {neg(-b)}. Qaysi belgi?', '>' if -a > -b else '<' if -a < -b else '=', ['>', '<', '=', '≥'])
    if t == 1: return mc(f'{neg(-a)} ☐ {b}. Qaysi belgi?', '<', ['>', '=', '≥'])
    return num(f'|{neg(-a)}| = ?', a)
def bs2():
    a, b = ri(-20, 20), ri(-20, 20)
    if a == 0 or b == 0 or (a > 0 and b > 0): return None
    op = ch(['+', '−']); r = a + b if op == '+' else a - b
    return mc(f'{neg(a)} {op} {par(b)} = ?', neg(r), [neg(-r), neg(r + 1), neg(r - 1), neg(r + 2)])
def bs3():
    a, b = ri(-12, 12), ri(-12, 12)
    if a == 0 or b == 0 or (a > 0 and b > 0): return None
    if R.random() < .5: return mc(f'{neg(a)} · {par(b)} = ?', neg(a * b), [neg(-a * b), neg(a * b + a), neg(a + b)])
    return mc(f'{neg(a * b)} : {par(b)} = ?', neg(a), [neg(-a), neg(a + 1), neg(a * b + b) if a * b + b != a else neg(a - 1)])
topic(B2, 'butun', 'Butun sonlar', bs1, bs2, bs3)

def so1():
    a = ri(1, 30)
    return ch([num(f'Son oʻqida 0 dan {neg(-a)} gacha masofa necha birlik?', a), num(f'|{neg(-a)}| + {a} = ?', 2 * a), mc(f'Son oʻqida {neg(-a)} soni 0 dan qaysi tomonda joylashgan?', 'Chapda', ['Oʻngda', 'Yuqorida', '0 bilan ustma-ust'])])
def so2():
    a, b = ri(-20, -1), ri(1, 25)
    return ch([num(f'Son oʻqida {neg(a)} va {b} nuqtalar orasidagi masofa necha birlik?', b - a), num(f'{neg(a)} va {b} orasida nechta butun son bor?', b - a - 1)])
def so3():
    a, b = ri(-30, -1), ri(1, 30)
    if (a + b) % 2: return None
    m = (a + b) // 2
    return ch([mc(f'Son oʻqida {neg(a)} va {b} nuqtalarning oʻrtasida qaysi son turadi?', neg(m), [neg(-m) if m else '1', neg(m + 1), neg(m - 2)]),
               num(f'|{neg(a)}| + |{b}| = ?', -a + b), mc(f'{neg(a)} sonining qarama-qarshisi qaysi?', str(-a), [neg(a), '0', neg(a - 1)])])
topic(B2, 'sonoqi', 'Son oʻqi va modul', so1, so2, so3)

topic(B2, 'daraja', 'Sonning darajasi',
      lambda: (lambda a, n: num(f'{a}{up(n)} = ?', a ** n) if a ** n <= 1000 else None)(ri(2, 12), ch([2, 2, 3])),
      lambda: ch([(lambda a: num(f'{a}² = ?', a * a))(ri(11, 25)), (lambda a, n: num(f'{a}{up(n)} = ?', a ** n))(ch([2, 3]), ri(4, 6)), (lambda n: num(f'10{up(n)} = ?', 10 ** n))(ri(2, 3))]),
      lambda: ch([(lambda a, b: num(f'{a}² + {b}³ = ?', a * a + b ** 3))(ri(2, 12), ri(2, 6)), (lambda a, b: num(f'{a}³ − {b}² = ?', a ** 3 - b * b) if a ** 3 > b * b else None)(ri(3, 9), ri(2, 9)),
                  (lambda n: num(f'2{up(n)} = ?', 2 ** n))(ri(7, 13)), (lambda a: num(f'Qaysi sonning kvadrati {a * a} ga teng?', a))(ri(11, 25))]))

fak1 = [num('3! = ?', 6), num('4! = ?', 24), num('1! = ?', 1), num('0! = ?', 1), num('2! = ?', 2), num('5! = ?', 120),
        mc('5! qanday hisoblanadi?', '1·2·3·4·5', ['5·5', '5+4+3+2+1', '5²']), mc('n! (n faktorial) nima?', '1 dan n gacha sonlar koʻpaytmasi', ['n ning kvadrati', '1 dan n gacha sonlar yigʻindisi', 'n · 2']),
        num('3! + 2! = ?', 8), num('4! − 3! = ?', 18)]
fak2 = [num('6! = ?', 720), num('7! = ?', 5040), num('5! : 4! = ?', 5), num('6! : 5! = ?', 6), num('3! · 2! = ?', 12), num('4! + 4! = ?', 48),
        num('5! − 4! = ?', 96), num('3 ta kitobni javonga necha xil usulda terish mumkin?', 6), num('4 ta oʻquvchini bir qatorga necha xil usulda turgʻizish mumkin?', 24), num('(2 + 1)! = ?', 6), num('2 · 3! = ?', 12)]
def fak3():
    n = ri(5, 12); k = ch([1, 2])
    if k == 1: return num(f'{n}! : {n - 1}! = ?', n)
    return num(f'{n}! : {n - 2}! = ?', n * (n - 1))
fak3l = collect(fak3, 8) + [num('5 ta kitobni javonga necha xil usulda terish mumkin?', 120), num('A, B, C harflaridan nechta har xil "soʻz" (tartib) tuzish mumkin?', 6)]
topic(B2, 'faktorial', 'Faktorial', fak1, fak2, fak3l)

def roman(n):
    v = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
    s = ''
    for a, r in v:
        while n >= a: s += r; n -= a
    return s
def rim(lo, hi):
    def g():
        n = ri(lo, hi)
        if R.random() < .6: return num(f'{roman(n)} rim raqami qaysi songa teng?', n)
        return mc(f'{n} soni rim raqamlarida qanday yoziladi?', roman(n), [roman(n + 1), roman(max(1, n - 1)), roman(n + 10) if n + 10 <= 3999 else roman(n - 10), roman(n + 5)])
    return g
topic(B2, 'rim', 'Rim raqamlari', rim(1, 20), rim(21, 100), rim(101, 2030))

# ================= 3-BOB =================
def qb1():
    b = ri(3, 9); q = ri(2, 9); r = ri(1, b - 1)
    return num(f'{b * q + r} ni {b} ga boʻlganda qoldiq nechaga teng?', r)
def qb2():
    b = ri(6, 15); q = ri(5, 30); r = ri(1, b - 1)
    return ch([num(f'{b * q + r} ni {b} ga boʻlganda qoldiq nechaga teng?', r), num(f'{b * q + r} ni {b} ga boʻlganda toʻliqsiz boʻlinma nechaga teng?', q)])
def qb3():
    b = ri(4, 12); q = ri(5, 20); r = ri(1, b - 1)
    return ch([num(f'Qaysi sonni {b} ga boʻlganda boʻlinma {q}, qoldiq {r} boʻladi?', b * q + r), num(f'{b} ga boʻlganda qoldiq eng koʻpi bilan nechaga teng boʻlishi mumkin?', b - 1)])
topic(B3, 'qoldiq', 'Qoldiqli boʻlish', qb1, qb2, qb3)

def bel(divs, lo=100, hi=9999):
    def g():
        k = ch(divs); good = ri(lo // k + 1, hi // k) * k
        bad = set()
        while len(bad) < 3:
            x = ri(lo, hi)
            if x % k: bad.add(x)
        return mc(f'Qaysi son {k} ga qoldiqsiz boʻlinadi?', sp(good), [sp(x) for x in bad])
    return g
belt = [mc('Son 2 ga boʻlinishi uchun oxirgi raqami qanday boʻlishi kerak?', 'Juft', ['Toq', '5', 'Faqat 0']),
        mc('Son 5 ga boʻlinishi uchun oxirgi raqami qanday boʻlishi kerak?', '0 yoki 5', ['Faqat 5', 'Juft', '1 yoki 5']),
        mc('Son 3 ga boʻlinishi uchun nima kerak?', 'Raqamlari yigʻindisi 3 ga boʻlinsin', ['Oxirgi raqami 3 boʻlsin', 'Juft boʻlsin', 'Oxirgi ikki raqami 3 ga boʻlinsin']),
        mc('Son 4 ga boʻlinishi uchun nima kerak?', 'Oxirgi ikki raqamidan tuzilgan son 4 ga boʻlinsin', ['Oxirgi raqami 4 boʻlsin', 'Raqamlari yigʻindisi 4 ga boʻlinsin', 'Juft boʻlsin'])]
def bel3():
    if R.random() < .35: return ch(belt)
    return bel([4, 6, 9, 15, 25])()
topic(B3, 'belgilar', 'Boʻlinish belgilari', bel([2, 5, 10]), bel([3, 9]), bel3)

def divisors(n): return [d for d in range(1, n + 1) if n % d == 0]
def isprime(n): return n > 1 and all(n % d for d in range(2, int(n ** .5) + 1))
def bv1():
    n = ch([12, 18, 20, 24, 30, 36, 16, 28, 40, 42, 45, 48])
    ds = divisors(n); good = ch(ds[1:-1]); bad = [x for x in range(2, n) if n % x][:]
    R.shuffle(bad)
    return mc(f'Qaysi son {n} ning boʻluvchisi?', good, bad[:3])
def bv2():
    n = ch([12, 18, 20, 24, 30, 36, 16, 28, 40, 42, 45, 48, 50, 60, 64, 72, 100])
    return ch([num(f'{n} ning nechta natural boʻluvchisi bor?', len(divisors(n))), num(f'{n} ning 1 dan va oʻzidan farqli eng katta boʻluvchisi?', divisors(n)[-2])])
def bv3():
    t = ri(0, 2)
    if t == 0:
        p = ch([p for p in range(20, 100) if isprime(p)]); bad = R.sample([x for x in range(20, 100) if not isprime(x) and x % 2], 3)
        return mc('Qaysi son tub son?', p, bad)
    if t == 1:
        n = ch([12, 18, 20, 24, 30, 36, 28, 40, 42, 60, 84, 90])
        return num(f'{n} ning nechta tub boʻluvchisi bor?', len([d for d in divisors(n) if isprime(d)]))
    n = ch([6, 8, 10, 12, 14, 15, 16, 18, 20])
    return num(f'{n} ning barcha natural boʻluvchilari yigʻindisi?', sum(divisors(n)))
topic(B3, 'boluvchi', 'Boʻluvchilar va tub sonlar', bv1, bv2, bv3)

def ek1():
    g = ri(2, 9); a, b = g * ri(1, 6), g * ri(1, 6)
    if a == b: return None
    return num(f'EKUB({a}; {b}) = ?', gcd(a, b))
def ek2():
    a, b = ri(2, 15), ri(2, 15)
    if a == b: return None
    l = a * b // gcd(a, b)
    return num(f'EKUK({a}; {b}) = ?', l) if l <= 200 else None
def ek3():
    t = ri(0, 2); a, b = ri(4, 20), ri(4, 20)
    if a == b: return None
    l = a * b // gcd(a, b)
    if t == 0 and l <= 120: return num(f'Bir avtobus har {a} daqiqada, ikkinchisi har {b} daqiqada bekatga keladi. Ular birga kelgandan keyin necha daqiqadan soʻng yana birga keladi?', l)
    if t == 1 and gcd(a, b) > 1: return num(f'{a * 3} ta olma va {b * 3} ta nokni eng koʻpi bilan nechta bolaga teng boʻlib berish mumkin?', gcd(a * 3, b * 3))
    if t == 2 and l <= 200: return num(f'{a} ga ham, {b} ga ham boʻlinadigan eng kichik natural son?', l)
    return None
topic(B3, 'ekub', 'EKUB va EKUK', ek1, ek2, ek3)

# ================= 4-BOB =================
def kq1():
    d = ri(2, 10); n = d * ri(2, 12)
    return num(f'{n} ning 1/{d} qismi nechaga teng?', n // d)
def kq2():
    d = ri(3, 10); c = ri(2, d - 1); n = d * ri(2, 12)
    if gcd(c, d) != 1: return None
    return num(f'{n} ning {c}/{d} qismi nechaga teng?', n // d * c)
def kq3():
    d = ri(3, 10); c = ri(2, d - 1); n = d * ri(2, 12)
    if gcd(c, d) != 1: return None
    return ch([num(f'Sonning {c}/{d} qismi {n // d * c} ga teng. Shu sonni toping.', n),
               num(f'Sinfda {n} ta oʻquvchi bor, ularning {c}/{d} qismi qizlar. Qizlar necha nafar?', n // d * c)])
topic(B4, 'kasr', 'Kasrlar: sonning qismi', kq1, kq2, kq3)

def kx1():
    a, b = ri(1, 7), ri(2, 9)
    if a >= b or gcd(a, b) != 1: return None
    k = ri(2, 6)
    return mc(f'{a * k}/{b * k} kasrni qisqartiring.', f'{a}/{b}', [f'{a * k // 2 if a * k % 2 == 0 else a + 1}/{b * k // 2 if b * k % 2 == 0 else b + 1}', f'{a}/{b * k}', f'{a * k}/{b}', f'{a + 1}/{b}'])
def kx2():
    a, b = ri(1, 9), ri(2, 12)
    if a >= b or gcd(a, b) != 1: return None
    k = ri(2, 8)
    return ch([num(f'{a}/{b} = x/{b * k}. x = ?', a * k), num(f'{a}/{b} = {a * k}/x. x = ?', b * k)])
def kx3():
    a, b = ri(1, 9), ri(2, 12)
    if a >= b or gcd(a, b) != 1: return None
    k, m = ri(2, 9), ri(2, 9)
    if k == m: return None
    return ch([num(f'{a * k}/{b * k} = {a * m}/x. x = ?', b * m), mc(f'Qaysi kasr {a}/{b} ga teng?', f'{a * k}/{b * k}', [f'{a + k}/{b + k}', f'{a * k}/{b * m}', f'{a * k}/{b + k}'])])
topic(B4, 'kasrxossa', 'Kasrning asosiy xossasi, qisqartirish', kx1, kx2, kx3)

def fq(x, y, op):
    return {'+': x + y, '−': x - y, '·': x * y, ':': x / y}[op]
def kk(lo, hi, ops, mixed=False):
    def g():
        a, b, c, d = ri(1, hi), ri(lo, hi), ri(1, hi), ri(lo, hi)
        x, y = F(a, b), F(c, d)
        if x.denominator == 1 or y.denominator == 1: return None
        op = ch(ops); r = fq(x, y, op)
        if r <= 0: return None
        if not mixed and (x > 1 or y > 1): return None
        return mc(f'{fr(x)} {op} {fr(y)} = ?', fr(r), fwr(r))
    return g
topic(B4, 'kasrkopbol', 'Kasrlarni koʻpaytirish va boʻlish', kk(2, 9, ['·']), kk(2, 9, [':', '·']), kk(2, 9, [':', '·'], True))

def ks1():
    d = ri(3, 15); a, b = ri(1, d - 1), ri(1, d - 1)
    op = ch(['+', '−'])
    if op == '−' and a <= b: return None
    r = F(a, d) + F(b, d) if op == '+' else F(a, d) - F(b, d)
    return mc(f'{a}/{d} {op} {b}/{d} = ?', fr(r), fwr(r) + [f'{a + b if op == "+" else a - b}/{d + d}'])
topic(B4, 'kasrqosh', 'Kasrlarni qoʻshish va ayirish', ks1, kk(2, 8, ['+', '−']), kk(2, 9, ['+', '−'], True))

def um1():
    a, b = ri(2, 12), ri(2, 12)
    if a == b: return None
    l = a * b // gcd(a, b)
    return num(f'1/{a} va 1/{b} kasrlarning eng kichik umumiy maxraji?', l) if l <= 120 else None
def um2():
    a, b, c, d = ri(1, 9), ri(2, 10), ri(1, 9), ri(2, 10)
    x, y = F(a, b), F(c, d)
    if a >= b or c >= d or x == y or gcd(a, b) > 1 or gcd(c, d) > 1: return None
    return mc(f'{a}/{b} ☐ {c}/{d}. Qaysi belgi?', '>' if x > y else '<', ['>', '<', '=', '≥'])
def um3():
    fs = set()
    while len(fs) < 4:
        a, b = ri(1, 9), ri(2, 10)
        if a < b: fs.add(F(a, b))
    fs = list(fs)
    if R.random() < .5: return mc('Qaysi kasr eng katta?', fr(max(fs)), [fr(x) for x in fs if x != max(fs)])
    return mc('Qaysi kasr eng kichik?', fr(min(fs)), [fr(x) for x in fs if x != min(fs)])
topic(B4, 'umumiymaxraj', 'Umumiy maxraj va kasrlarni taqqoslash', um1, um2, um3)

def ka1():
    a, b = F(ri(1, 5), ri(2, 6)), F(ri(1, 5), ri(2, 6))
    if a.denominator == 1 or b.denominator == 1: return None
    n = ri(2, 6); r = a * n
    return mc(f'{fr(a)} · {n} = ?', fr(r), fwr(r))
def ka2():
    w, a, b = ri(1, 5), ri(1, 7), ri(2, 9)
    if a >= b or gcd(a, b) > 1: return None
    x = w + F(a, b)
    return ch([mc(f'{w} {a}/{b} ni notoʻgʻri kasrga aylantiring.', f'{x.numerator}/{b}', [f'{w * a + b}/{b}', f'{w + a}/{b}', f'{x.numerator + 1}/{b}']),
               mc(f'{x.numerator}/{b} ni aralash songa aylantiring.', fr(x), [fr(x + 1), fr(x - F(1, b)) if x - F(1, b) > 0 else fr(x + 2), f'{w} {b}/{a}'])])
def ka3():
    a, b, c = F(ri(1, 4), ri(2, 5)), F(ri(1, 4), ri(2, 5)), F(ri(1, 4), ri(2, 5))
    if 1 in (a.denominator, b.denominator, c.denominator): return None
    t = ri(0, 1)
    r = a + b * c if t == 0 else (a + b) * c
    q = f'{fr(a)} + {fr(b)} · {fr(c)} = ?' if t == 0 else f'({fr(a)} + {fr(b)}) · {fr(c)} = ?'
    return mc(q, fr(r), fwr(r) + [fr((a + b) * c if t == 0 else a + b * c)])
topic(B4, 'kasraralash', 'Kasrlar ustida aralash amallar', ka1, ka2, ka3)

# ================= 5-BOB =================
def ok1():
    t = ri(0, 2)
    if t == 0:
        n = ri(1, 99); d = 10 if n < 10 else 100
        x = n / d
        if gcd(n, d) == 1 or True:
            return mc(f'{n}/{d} ni oʻnli kasr koʻrinishida yozing.', dec(x), [dec(n / (d * 10), 3), dec(n / (d / 10)), dec(x + .1)])
    if t == 1:
        a, b = ri(1, 999) / 100, ri(1, 999) / 100
        if a == b: return None
        return mc(f'{dec(a)} ☐ {dec(b)}. Qaysi belgi?', '>' if a > b else '<', ['>', '<', '=', '≥'])
    x = ri(11, 999) / 100
    return mc(f'{dec(x)} ni oʻndan birlargacha yaxlitlang.', dec(round(x + 1e-9, 1), 1), [dec(int(x * 10) / 10 if round(x + 1e-9, 1) != int(x * 10) / 10 else int(x * 10) / 10 + .1, 1), dec(round(x), 0) if round(x) != round(x + 1e-9, 1) else dec(x + .2, 1), dec(round(x + 1e-9, 1) + .1, 1)])
def ok2():
    pairs = [('1/2', '0,5'), ('1/4', '0,25'), ('3/4', '0,75'), ('1/5', '0,2'), ('2/5', '0,4'), ('3/5', '0,6'), ('4/5', '0,8'), ('1/8', '0,125'), ('1/20', '0,05'), ('7/20', '0,35'), ('3/25', '0,12'), ('1/50', '0,02')]
    a, b = ch(pairs); others = [p[1] for p in pairs if p[1] != b]
    return mc(f'{a} kasr qaysi oʻnli kasrga teng?', b, R.sample(others, 3))
def ok3():
    n = ri(2, 99); x = n / 100
    if R.random() < .5:
        f = F(n, 100)
        return mc(f'{dec(x)} ni qisqarmas oddiy kasrga aylantiring.', fr(f), [f'{n}/10', fr(F(n, 1000)), f'{f.numerator + 1}/{f.denominator}'])
    vals = R.sample(range(101, 999), 4); vs = [v / 1000 for v in vals]
    return mc('Qaysi son eng katta?', dec(max(vs), 3), [dec(v, 3) for v in vs if v != max(vs)])
topic(B5, 'onli', 'Oʻnli kasrlar: yozish va taqqoslash', ok1, ok2, ok3)

def oq(nd, hi):
    def g():
        a, b = ri(1, hi * 10 ** nd) / 10 ** nd, ri(1, hi * 10 ** nd) / 10 ** nd
        op = ch(['+', '−'])
        if op == '−' and a <= b: a, b = b, a
        if a == b: return None
        r = round(a + b if op == '+' else a - b, nd)
        return mc(f'{dec(a, nd)} {op} {dec(b, nd)} = ?', dec(r, nd), [dec(r + 1, nd), dec(r + 10 ** -nd, nd), dec(r * 10, nd), dec(abs(r - .1), nd)])
    return g
def oq3():
    a = ri(11, 99) / 10; b = ri(101, 999) / 100
    op = ch(['+', '−'])
    if op == '−' and a <= b: a, b = b, a
    r = round(a + b if op == '+' else a - b, 2)
    return mc(f'{dec(a)} {op} {dec(b)} = ?', dec(r), [dec(r + .9), dec(round(r - .09, 2)), dec(r * 10), dec(r + 1)])
topic(B5, 'onliqosh', 'Oʻnli kasrlarni qoʻshish va ayirish', oq(1, 9), oq(1, 50), oq3)

def okb1():
    x = ri(11, 999) / 100; k = ch([10, 100, 1000]); op = ch(['·', ':'])
    r = x * k if op == '·' else x / k
    return mc(f'{dec(x)} {op} {k} = ?', dec(r, 5), [dec(x * k / 10 if op == '·' else x / k * 10, 5), dec(x * k * 10 if op == '·' else x / k / 10, 5), dec(x / k if op == '·' else x * k, 5)])
def okb2():
    a, b = ri(2, 9) / 10, ri(2, 9)
    if R.random() < .5:
        r = a * b; return mc(f'{dec(a)} · {b} = ?', dec(r), [dec(r * 10), dec(r / 10), dec(r + .1)])
    r = a * b
    return mc(f'{dec(r)} : {b} = ?', dec(a), [dec(a * 10), dec(a / 10), dec(a + .1)])
def okb3():
    a, b = ri(2, 9) / 10, ri(2, 9) / 10
    r = round(a * b, 2)
    if R.random() < .5: return mc(f'{dec(a)} · {dec(b)} = ?', dec(r), [dec(r * 10), dec(r / 10, 3), dec(a + b)])
    return mc(f'{dec(r)} : {dec(a)} = ?', dec(b), [dec(b * 10), dec(b / 10, 3), dec(b + .1)])
topic(B5, 'onlikop', 'Oʻnli kasrlarni koʻpaytirish va boʻlish', okb1, okb2, okb3)

# ================= 6-BOB =================
def dx1():
    m, n = ri(2, 9), ri(2, 9)
    return ch([num(f'a{up(m)} · a{up(n)} = aˣ. x = ?', m + n), num(f'2{up(m)} · 2{up(n)} = 2ˣ. x = ?', m + n)])
def dx2():
    m, n = ri(2, 9), ri(2, 9)
    return ch([num(f'a{up(m + n)} : a{up(n)} = aˣ. x = ?', m), num(f'(a{up(m)}){up(n)} = aˣ. x = ?', m * n)])
def dx3():
    m, n, k = ri(2, 6), ri(2, 6), ri(2, 4)
    return ch([num(f'(a{up(m)} · a{up(n)}){up(k)} = aˣ. x = ?', (m + n) * k), num(f'a{up(m)} · a{up(n)} : a{up(k)} = aˣ. x = ?', m + n - k), num(f'{m}{up(n + 1)} : {m}{up(n)} = ?', m),
               num(f'5{up(n + 2)} : 5{up(n)} = ?', 25), num(f'(2³)² : 2⁴ = ?', 4)])
topic(B6, 'darajaxossa', 'Daraja va uning xossalari', dx1, dx2, dx3)

def sgn(n): return f'+ {n}' if n >= 0 else f'− {-n}'
def qo1():
    a, b = ri(2, 9), ri(1, 9)
    return mc(f'{a}(x + {b}) = ?', f'{a}x + {a * b}', [f'{a}x + {b}', f'{a + b}x', f'x + {a * b}'])
def qo2():
    a, b = ri(2, 9), ri(1, 9)
    if R.random() < .5: return mc(f'−{a}(x − {b}) = ?', f'−{a}x + {a * b}', [f'−{a}x − {a * b}', f'{a}x + {a * b}', f'−{a}x − {b}'])
    return mc(f'{a * b}x + {a * ri(1, 1) * b * 2} ifodani koʻpaytuvchilarga ajrating.', f'{a * b}(x + 2)', [f'{a}(x + {b * 2})', f'{a * b}(x + {a * b * 2})', f'2(x + {a * b})'])
def qo3():
    k = ri(2, 9); a, b = ri(2, 9), ri(2, 9)
    if gcd(a, b) > 1: return None
    t = ri(0, 1)
    if t == 0: return mc(f'{k * a}x + {k * b}y ni koʻpaytuvchilarga ajrating.', f'{k}({a}x + {b}y)', [f'{a}({k}x + {b}y)', f'{k}({a}x + {k * b}y)', f'{k * a}(x + {b}y)'])
    return mc(f'{a}x(x + {b}) = ?', f'{a}x² + {a * b}x', [f'{a}x² + {b}x', f'{a}x + {a * b}x', f'{a}x² + {a * b}'])
topic(B6, 'qavs', 'Qavs ochish va koʻpaytuvchilarga ajratish', qo1, qo2, qo3)

def ox(nt, var):
    def g():
        cs = [ri(1, 12) for _ in range(nt)]; sg = [1] + [ch([1, -1]) for _ in range(nt - 1)]
        r = sum(c * s for c, s in zip(cs, sg))
        if r <= 1: return None
        q = cf(cs[0], var) + ''.join(f' {"+" if s > 0 else "−"} {cf(c, var)}' for c, s in zip(cs[1:], sg[1:]))
        return mc(f'Soddalashtiring: {q}', cf(r, var), [cf(r + 2, var), cf(sum(cs), var) if sum(cs) != r else cf(r - 1, var), f'{cf(r, var)}²', cf(abs(r - 2), var)])
    return g
def ox3():
    a, b, c, d = ri(2, 9), ri(1, 9), ri(1, 6), ri(1, 9)
    if a <= c: return None
    return mc(f'Soddalashtiring: {a}x + {b} − {cf(c, "x")} + {d}', f'{cf(a - c, "x")} + {b + d}', [f'{a + c}x + {b + d}', f'{cf(a - c, "x")} + {b + d + 1}', f'{a - c + b + d}x'])
topic(B6, 'oxshash', 'Oʻxshash hadlarni ixchamlash', ox(2, 'a'), ox(3, 'x'), ox3)

def tl1():
    x, a, b = ri(2, 12), ri(2, 9), ri(1, 20)
    return num(f'{a}x + {b} = {a * x + b}. x = ?', x)
def tl2():
    x, a, b = ri(2, 12), ri(2, 9), ri(1, 9)
    return ch([num(f'{a}(x − {b}) = {a * (x - b)}. x = ?', x) if x > b else None, num(f'{a}x − {b} = {a * x - b}. x = ?', x) if a * x > b else None])
def tl3():
    x, a, c, b = ri(1, 12), ri(3, 9), ri(1, 8), ri(1, 20)
    if a <= c: return None
    d = (a - c) * x + b
    return num(f'{a}x + {b} = {cf(c, "x")} + {d}. x = ?', x)
topic(B6, 'tenglama2', 'Chiziqli tenglamalar', tl1, tl2, tl3)

def pr1():
    a, b, k = ri(1, 9), ri(1, 9), ri(2, 6)
    return num(f'x : {b * k} = {a} : {b}. x = ?', a * k)
def pr2():
    a, b, k = ri(1, 12), ri(2, 12), ri(2, 9)
    return ch([num(f'{a * k} : x = {a} : {b}. x = ?', b * k), num(f'x/{b * k} = {a}/{b}. x = ?', a * k)])
def pr3():
    t = ri(0, 1); p, k = ri(2, 9), ri(3, 9)
    if t == 0: return num(f'{k} kg olma {p * k} ming soʻm. {k + 2} kg olma necha ming soʻm?', p * (k + 2))
    a, b = ri(2, 9), ri(2, 9)
    return num(f'Proporsiyaning chetki hadlari {a} va {b * 2}, oʻrta hadlaridan biri {b}. Ikkinchi oʻrta hadni toping.', 2 * a)
topic(B6, 'proporsiya', 'Proporsiya', pr1, pr2, pr3)

# ================= 7-8-BOB: masalalar =================
def sm1():
    a, b = ri(3, 12), ri(3, 15)
    return ch([num(f'Bir qutida {a} ta qalam bor. {b} ta qutida nechta qalam bor?', a * b),
               num(f'Savatda {a * b} ta olma bor. Ularni {b} ta bolaga teng boʻlinsa, har biriga nechta tegadi?', a),
               num(f'Ali {a * 3} ta, Vali undan {a} ta koʻp yongʻoq terdi. Vali nechta yongʻoq terdi?', a * 4),
               num(f'Kutubxonada {a * 10} ta kitob bor edi. {b} tasi berildi. Nechta qoldi?', a * 10 - b) if a * 10 > b else None])
def sm2():
    a, b, c = ri(3, 12), ri(2, 9), ri(2, 9)
    return ch([num(f'Daftar {a} ming, ruchka {b} ming soʻm. {c} ta daftar va 1 ta ruchka necha ming soʻm?', a * c + b),
               num(f'Bir qatorda {a} ta stul, {b} qator bor. {c} ta stul boʻsh. Nechta oʻquvchi oʻtiribdi?', a * b - c) if a * b > c else None,
               num(f'Avtobusda {a * 3} kishi bor edi. Bekatda {b} kishi tushdi, {c} kishi chiqdi. Endi nechta kishi bor?', a * 3 - b + c) if a * 3 > b else None])
def sm3():
    a, b = ri(2, 9), ri(2, 9); s = a + b
    return ch([num(f'Ikki sonning yigʻindisi {s * 3}, biri ikkinchisidan 2 marta katta. Kichigini toping.', s) if True else None,
               num(f'Ikki sonning yigʻindisi {a * 2 + b * 2}, ayirmasi {abs(a - b) * 2}. Kattasini toping.', max(a, b) * 2) if a != b else None,
               num(f'Usta kuniga {a * 5} ta detal yasaydi. {a * 5 * b} ta detalni necha kunda yasaydi?', b)])
topic(B7, 'masala', 'Toʻrt amalga doir sodda masalalar', sm1, sm2, sm3)

def ys1():
    a, b = ri(6, 15), ri(2, 9)
    return ch([num(f'Ali {a} yoshda, akasi undan {b} yosh katta. Akasi necha yoshda?', a + b), num(f'Nodira {a} yoshda. {b} yildan keyin u necha yoshda boʻladi?', a + b),
               num(f'Bobur {a + b} yoshda. {b} yil oldin u necha yoshda boʻlgan?', a)])
def ys2():
    a, k = ri(6, 12), ri(3, 5)
    return ch([num(f'Oʻgʻil {a} yoshda, ota undan {k} marta katta. Ota necha yoshda?', a * k), num(f'Ona {a * k} yoshda, qizi undan {k} marta yosh. Qizi necha yoshda?', a),
               num(f'Aka {a + 5} yoshda, uka {a} yoshda. 10 yildan keyin yoshlari farqi necha boʻladi?', 5)])
def ys3():
    a, k = ri(7, 12), ri(3, 5)
    return ch([num(f'Ota oʻgʻlidan {k} marta katta. Yoshlari yigʻindisi {a * (k + 1)}. Ota necha yoshda?', a * k),
               num(f'Ota {a * k} yoshda, oʻgʻli {a} yoshda. Necha yildan keyin yoshlari yigʻindisi {a * (k + 1) + 20} boʻladi?', 10),
               num(f'Opa {a + 6} yoshda, singil {a} yoshda. Necha yil oldin opa singlidan 2 marta katta boʻlgan?', a - 6) if a > 6 else None])
topic(B7, 'yosh', 'Yoshga doir masalalar', ys1, ys2, ys3)

def tp1():
    a, p, k = ri(2, 6), ri(2, 9), ri(2, 4)
    return ch([num(f'{a} ta daftar {a * p} ming soʻm. {a * k} ta daftar necha ming soʻm?', a * k * p),
               num(f'Mashina {a} soatda {a * p * 10} km yuradi. Shu tezlikda {a + 1} soatda necha km yuradi?', (a + 1) * p * 10)])
def tp2():
    w, d = ch([(2, 12), (3, 8), (4, 6), (6, 4), (2, 10), (4, 10), (5, 6), (3, 10), (6, 10), (8, 3)])
    k = ch([x for x in (2, 3, 4, 6, 8, 12) if w * d % x == 0 and x != w])
    return num(f'{w} ishchi ishni {d} kunda bajaradi. {k} ishchi shu ishni necha kunda bajaradi?', w * d // k)
def tp3():
    v, t = ch([(60, 4), (40, 6), (80, 3), (30, 8), (20, 12), (90, 2), (50, 6), (120, 2)])
    k = ch([x for x in (20, 30, 40, 60, 80, 100, 120, 240) if v * t % x == 0 and x != v])
    return ch([num(f'Mashina {v} km/soat tezlik bilan {t} soatda yetib boradi. {k} km/soat tezlikda necha soatda yetib boradi?', v * t // k),
               mc(f'Tezlik oshsa, bir xil masofani bosib oʻtish vaqti qanday oʻzgaradi?', 'Kamayadi (teskari proporsional)', ['Oshadi', 'Oʻzgarmaydi', 'Ikki marta oshadi'])])
topic(B7, 'proporsional', 'Toʻgʻri va teskari proporsional miqdorlar', tp1, tp2, tp3)

ol = [(1000, 'm', 'km'), (100, 'sm', 'm'), (10, 'mm', 'sm'), (1000, 'g', 'kg'), (1000, 'kg', 't'), (60, 'min', 'soat'), (60, 's', 'min'), (100, 'kg', 'sentner'), (1000, 'm', 'km')]
def ol1():
    k, s, b = ch(ol); n = ri(2, 9)
    return num(f'{n} {b} = ? {s}', n * k)
def ol2():
    k, s, b = ch(ol); n = ri(2, 9); m = ri(1, k - 1)
    if n * k + m > 9999: return None
    return ch([num(f'{n} {b} {m} {s} = ? {s}', n * k + m), num(f'{n * k} {s} = ? {b}', n)])
def ol3():
    t = ri(0, 3)
    if t == 0: n = ri(2, 9); return num(f'{n} m² = ? dm²', n * 100)
    if t == 1: n = ri(2, 90); return num(f'{n * 100} dm² = ? m²', n)
    if t == 2: n = ri(1, 9); return num(f'{n} l = ? ml', n * 1000)
    n = ri(1, 9); return num(f'{n} dm³ = ? l', n)
topic(B7, 'olchov', 'Oʻlchov birliklari', ol1, ol2, ol3)

def ms1():
    k, a = ch([10, 100, 1000]), ri(2, 9)
    return num(f'Masshtab 1 : {k}. Xaritada {a} sm. Haqiqiy uzunlik necha sm?', a * k) if a * k <= 9999 else None
def ms2():
    a = ri(2, 15); k = ch([100000, 1000000])
    km = a * k // 100000
    return num(f'Masshtab 1 : {sp(k)}. Xaritada {a} sm. Haqiqiy masofa necha km?', km)
def ms3():
    km, k = ri(2, 30) * 10, ch([1000000, 500000, 2000000])
    sm = km * 100000 / k
    if sm != int(sm): return None
    return num(f'Haqiqiy masofa {km} km. Masshtab 1 : {sp(k)} boʻlgan xaritada bu necha sm?', int(sm))
topic(B7, 'masshtab', 'Masshtab', ms1, ms2, ms3)

def fz1():
    p = ch([10, 50, 20, 25, 100]); n = ch([100, 200, 300, 400, 500, 600, 800, 1000, 40, 60, 80])
    return num(f'{n} ning {p} % i nechaga teng?', n * p // 100) if n * p % 100 == 0 else None
def fz2():
    p = ch([5, 15, 30, 40, 60, 75, 12, 35]); n = ri(1, 40) * 20
    return num(f'{n} ning {p} % i nechaga teng?', n * p // 100) if n * p % 100 == 0 else None
def fz3():
    p = ch([5, 10, 20, 25, 40, 50]); n = ri(2, 40) * 10
    if (n * p) % 100: return None
    return ch([num(f'Qaysi sonning {p} % i {n * p // 100} ga teng?', n), num(f'{n * p // 100} soni {n} ning necha foizi?', p),
               num(f'Sinfda {n // 10 * 10 if n <= 40 else 40} oʻquvchi, ularning {p} % i aʼlochi. Aʼlochilar nechta?', (n if n <= 40 else 40) * p // 100) if (n if n <= 40 else 40) * p % 100 == 0 else None])
topic(B7, 'foiz', 'Qism va foiz', fz1, fz2, fz3)

def fy1():
    p, n = ch([10, 20, 25, 50]), ri(2, 30) * 20
    return num(f'Narxi {n} ming soʻm boʻlgan koʻylakka {p} % chegirma qilindi. Chegirma necha ming soʻm?', n * p // 100) if n * p % 100 == 0 else None
def fy2():
    p, n = ch([10, 20, 25, 30, 40, 50]), ri(2, 30) * 20
    if n * p % 100: return None
    return ch([num(f'Narxi {n} ming soʻm. {p} % chegirmadan keyin necha ming soʻm boʻladi?', n - n * p // 100),
               num(f'Narxi {n} ming soʻm edi, {p} % qimmatlashdi. Yangi narx necha ming soʻm?', n + n * p // 100)])
def fy3():
    a, b = ri(2, 20) * 10, ch([10, 20, 25, 50])
    s = a + a * b // 100
    if a * b % 100: return None
    return ch([num(f'Doʻkon mahsulotni {a} ming soʻmga olib, {s} ming soʻmga sotdi. Foyda necha foiz?', b),
               num(f'Mahsulot {a} ming soʻmga olinib, {b} % foyda bilan sotildi. Sotish narxi necha ming soʻm?', s),
               num(f'Narx {b} % ga tushgandan keyin {a - a * b // 100} ming soʻm boʻldi. Dastlabki narx necha ming soʻm edi?', a)])
topic(B7, 'foyda', 'Foyda, zarar va chegirmaga doir masalalar', fy1, fy2, fy3)

def vq1():
    h, m = ri(1, 5), ri(1, 59)
    return ch([num(f'{h} soat {m} minut = ? minut', h * 60 + m), num(f'{h} soat = ? minut', h * 60), num(f'{h} minut = ? sekund', h * 60)])
def vq2():
    h, m, d = ri(7, 15), ch([0, 10, 15, 20, 30, 40, 45, 50]), ch([25, 35, 40, 45, 50, 70, 80, 90])
    t = h * 60 + m + d; r = f'{t // 60}:{t % 60:02d}'
    return mc(f'Dars {h}:{m:02d} da boshlanib, {d} minut davom etdi. U soat nechada tugadi?', r, [f'{(t + 5) // 60}:{(t + 5) % 60:02d}', f'{(t - 10) // 60}:{(t - 10) % 60:02d}', f'{(t + 60) // 60}:{(t + 60) % 60:02d}'])
def vq3():
    t = ri(0, 2)
    if t == 0: d = ri(2, 6); return num(f'{d} sutka = ? soat', d * 24)
    if t == 1: w = ri(2, 9); return num(f'{w} hafta = ? kun', w * 7)
    h1, m1 = ri(7, 12), ch([0, 15, 20, 30, 45]); h2, m2 = h1 + ri(1, 5), ch([0, 10, 15, 30, 40])
    return num(f'Poyezd {h1}:{m1:02d} da joʻnab, {h2}:{m2:02d} da yetib keldi. Yoʻlda necha minut yurdi?', h2 * 60 + m2 - h1 * 60 - m1)
topic(B7, 'vaqt', 'Vaqtga doir masalalar', vq1, vq2, vq3)

# ================= 9-BOB =================
def ss1():
    x, y = ri(1, 15), ri(1, 15)
    if x <= y: return None
    return ch([num(f'x + y = {x + y}, x − y = {x - y}. x = ?', x), num(f'x + y = {x + y}, x − y = {x - y}. y = ?', y)])
def ss2():
    x, y, a = ri(1, 12), ri(1, 12), ri(2, 5)
    return ch([num(f'x + y = {x + y}, {a}x + y = {a * x + y}. x = ?', x), num(f'y = {a}x, x + y = {x * (a + 1)}. x = ?', x)])
def ss3():
    x, y, a, b = ri(1, 10), ri(1, 10), ri(2, 5), ri(2, 5)
    return ch([num(f'{a}x + {b}y = {a * x + b * y}, x + y = {x + y}. y = ?', y) if a != b else None,
               num(f'Daftar va ruchka birga {x + y} ming soʻm. 2 daftar va 1 ruchka {2 * x + y} ming soʻm. Daftar necha ming soʻm?', x)])
topic(B9, 'sistema', 'Chiziqli tenglamalar sistemasi', ss1, ss2, ss3)

def hr1():
    v, t = ch([20, 30, 40, 50, 60, 70, 80, 90, 5, 4, 12]), ri(2, 6)
    return ch([num(f'Tezlik {v} km/soat. {t} soatda necha km yuradi?', v * t), num(f'{v * t} km masofani {t} soatda bosib oʻtdi. Tezlik necha km/soat?', v),
               num(f'{v * t} km masofani {v} km/soat tezlikda necha soatda bosib oʻtadi?', t)])
def hr2():
    a, b, t = ch([40, 50, 60, 70, 80]), ch([30, 40, 50, 60, 90]), ri(2, 5)
    return ch([num(f'Ikki mashina bir-biriga qarab {a} va {b} km/soat tezlikda yurdi. {t} soatda uchrashdi. Oraliq masofa necha km edi?', (a + b) * t),
               num(f'Ikki shahar oraligʻi {(a + b) * t} km. Ikki mashina bir-biriga qarab {a} va {b} km/soat tezlikda yurdi. Necha soatda uchrashadi?', t)])
def hr3():
    v, u, t = ch([10, 12, 15, 18, 20]), ch([2, 3]), ri(2, 5)
    a, b = ch([60, 70, 80, 90]), ch([40, 50, 60])
    if a == b: return None
    return ch([num(f'Kater tezligi {v} km/soat, daryo oqimi {u} km/soat. Oqim boʻyicha {t} soatda necha km yuradi?', (v + u) * t),
               num(f'Kater tezligi {v} km/soat, daryo oqimi {u} km/soat. Oqimga qarshi {t} soatda necha km yuradi?', (v - u) * t),
               num(f'Ikki mashina bir joydan bir yoʻnalishda {a} va {b} km/soat tezlikda yoʻlga chiqdi. {t} soatdan keyin ular orasidagi masofa necha km boʻladi?', abs(a - b) * t)])
topic(B9, 'harakat', 'Harakatga doir masalalar', hr1, hr2, hr3)

def ish1():
    a, d = ri(5, 30), ri(2, 9)
    return ch([num(f'Usta kuniga {a} ta detal yasaydi. {d} kunda nechta detal yasaydi?', a * d), num(f'{a * d} ta detalni {d} kunda yasadi. Kuniga nechta yasagan?', a)])
def ish2():
    a, d = ri(2, 12), ri(2, 9)
    return ch([num(f'Bir ishchi soatiga {a} ta, ikkinchisi {d} ta detal yasaydi. Birgalikda {ri(2, 2)} soatda nechta yasaydi?', (a + d) * 2),
               num(f'Ishni bajarish uchun {a * d} soat kerak. {d} kishi teng ishlasa, har biri necha soat ishlaydi?', a)])
ish3l = [(6, 3, 2), (12, 6, 4), (4, 4, 2), (10, 15, 6), (20, 30, 12), (6, 12, 4), (12, 4, 3), (30, 60, 20), (3, 6, 2), (20, 5, 4), (8, 8, 4), (18, 9, 6), (24, 12, 8), (10, 10, 5), (12, 12, 6), (15, 30, 10)]
def ish3():
    a, b, c = ch(ish3l)
    return ch([num(f'Bir quvur hovuzni {a} soatda, ikkinchisi {b} soatda toʻldiradi. Ikkalasi birga necha soatda toʻldiradi?', c),
               num(f'Ali ishni {a} kunda, Vali {b} kunda bajaradi. Birga necha kunda bajarishadi?', c)])
topic(B9, 'ish', 'Ishga doir masalalar', ish1, ish2, ish3)

# ================= 10-BOB: planimetriya =================
nuq1 = [num('Kesmaning nechta uchi bor?', 2), num('Nurning nechta uchi (boshlangʻich nuqtasi) bor?', 1), mc('Toʻgʻri chiziqning uchi bormi?', 'Yoʻq, u cheksiz', ['Ha, 2 ta', 'Ha, 1 ta', 'Ha, 3 ta']),
        num('Ikki nuqta orqali nechta toʻgʻri chiziq oʻtkazish mumkin?', 1), num('Bir nuqta orqali nechta toʻgʻri chiziq oʻtkazish mumkin? (0 – cheksiz)', 0),
        mc('Ikki nuqta orasidagi eng qisqa yoʻl nima?', 'Kesma', ['Nur', 'Siniq chiziq', 'Egri chiziq']), mc('AB nur qaysi nuqtadan boshlanadi?', 'A', ['B', 'Oʻrtasidan', 'Ikkala nuqtadan']),
        num('Ikki toʻgʻri chiziq nechta nuqtada kesishishi mumkin (eng koʻpi)?', 1), mc('Kesishmaydigan va bir tekislikda yotuvchi ikki toʻgʻri chiziq qanday ataladi?', 'Parallel', ['Perpendikulyar', 'Kesishuvchi', 'Teng']),
        num('1 dm necha sm?', 10)]
def nuq2():
    a = ri(2, 30) * 2
    return ch([num(f'AB = {a} sm, C nuqta AB ning oʻrtasi. AC = ? sm', a // 2), num(f'AB = {a} sm, C nuqta AB da yotadi, AC = {a // 2 - 1} sm. CB = ? sm', a - a // 2 + 1),
               num(f'AC = {a} sm, CB = {a // 2 + 3} sm, C nuqta AB kesmada yotadi. AB = ? sm', a + a // 2 + 3)])
def nuq3():
    n = ri(3, 8)
    return ch([num(f'Toʻgʻri chiziqda {n} ta nuqta belgilandi. Nechta kesma hosil boʻladi?', n * (n - 1) // 2),
               num(f'Toʻgʻri chiziqda {n} ta nuqta belgilandi. U nechta boʻlakka (kesma va nurlarga) boʻlinadi?', n + 1),
               num(f'Tekislikda {n} ta nuqta bor, hech qaysi uchtasi bir toʻgʻri chiziqda emas. Ular orqali nechta toʻgʻri chiziq oʻtadi?', n * (n - 1) // 2)])
topic(B10, 'nuqta', 'Nuqta, toʻgʻri chiziq, kesma va nur', nuq1, nuq2, nuq3)

bur1 = [num('Toʻgʻri burchak necha gradus?', 90), num('Yoyiq burchak necha gradus?', 180), num('Toʻliq burchak (aylana) necha gradus?', 360),
        mc('50° li burchak qanday burchak?', 'Oʻtkir', ['Oʻtmas', 'Toʻgʻri', 'Yoyiq']), mc('120° li burchak qanday burchak?', 'Oʻtmas', ['Oʻtkir', 'Toʻgʻri', 'Yoyiq']),
        mc('90° li burchak qanday burchak?', 'Toʻgʻri', ['Oʻtkir', 'Oʻtmas', 'Yoyiq']), mc('Oʻtkir burchak nimadan kichik?', '90° dan', ['180° dan', '45° dan', '360° dan']),
        mc('Burchak qanday asbob bilan oʻlchanadi?', 'Transportir', ['Chizgʻich', 'Sirkul', 'Tarozi']), num('Soat 3:00 da strelkalar orasidagi burchak necha gradus?', 90),
        num('Soat 6:00 da strelkalar orasidagi burchak necha gradus?', 180), num('Toʻgʻri burchakning yarmi necha gradus?', 45)]
def bur2():
    a = ri(15, 165)
    return ch([num(f'Qoʻshni burchaklardan biri {a}°. Ikkinchisi necha gradus?', 180 - a), num(f'Vertikal burchaklardan biri {a}°. Ikkinchisi necha gradus?', a),
               num(f'{a}° li burchak bissektrisasi uni qanday burchaklarga ajratadi? (gradusi)', a // 2) if a % 2 == 0 else None])
def bur3():
    a = ri(10, 80); h = ri(1, 11)
    return ch([num(f'Qoʻshni burchaklardan biri ikkinchisidan {a * 2}° katta. Kattasi necha gradus?', 90 + a) if a < 90 else None,
               num(f'Soat {h}:00 da strelkalar orasidagi kichik burchak necha gradus?', min(h * 30, 360 - h * 30)),
               num(f'Ikki toʻgʻri chiziq kesishganda hosil boʻlgan burchaklardan biri {a}°. Qolgan burchaklardan kattasi necha gradus?', 180 - a)])
topic(B10, 'burchak', 'Burchaklar', bur1, bur2, bur3)

def uc1():
    a, b = ri(20, 80), ri(20, 80)
    if a + b >= 170: return None
    return num(f'Uchburchakning ikki burchagi {a}° va {b}°. Uchinchi burchagi necha gradus?', 180 - a - b)
ucq = [num('Uchburchak ichki burchaklari yigʻindisi necha gradus?', 180), num('Teng tomonli uchburchakning har bir burchagi necha gradus?', 60),
       mc('Burchaklaridan biri 90° boʻlgan uchburchak qanday ataladi?', 'Toʻgʻri burchakli', ['Oʻtkir burchakli', 'Oʻtmas burchakli', 'Teng tomonli']),
       mc('Burchaklaridan biri 100° boʻlgan uchburchak qanday ataladi?', 'Oʻtmas burchakli', ['Oʻtkir burchakli', 'Toʻgʻri burchakli', 'Teng tomonli'])]
def uc2():
    a = ri(20, 70)
    if R.random() < .3: return ch(ucq)
    return ch([num(f'Toʻgʻri burchakli uchburchakning bir oʻtkir burchagi {a}°. Ikkinchisi necha gradus?', 90 - a),
               num(f'Teng yonli uchburchak asosidagi burchagi {a}°. Uchidagi burchagi necha gradus?', 180 - 2 * a)])
def uc3():
    a = ri(10, 80) * 2
    if a >= 180: return None
    k = ri(1, 4)
    return ch([num(f'Teng yonli uchburchak uchidagi burchagi {a}°. Asosidagi burchagi necha gradus?', (180 - a) // 2),
               num(f'Uchburchak burchaklari 1 : {k} : {k + 1} nisbatda. Eng kichik burchagi necha gradus?', 180 // (2 * k + 2)) if 180 % (2 * k + 2) == 0 else None,
               num(f'Uchburchakning tashqi burchagi {a}°. Unga qoʻshni ichki burchagi necha gradus?', 180 - a)])
topic(B10, 'uchburchak', 'Uchburchak burchaklari', uc1, uc2, uc3)

def pe1():
    a, b = ri(2, 20), ri(2, 20)
    return ch([num(f'Kvadratning tomoni {a} sm. Perimetri necha sm?', 4 * a), num(f'Toʻgʻri toʻrtburchakning tomonlari {a} sm va {b} sm. Perimetri necha sm?', 2 * (a + b)) if a != b else None])
def pe2():
    a, b, c = ri(3, 20), ri(3, 20), ri(3, 20)
    if a + b <= c or a + c <= b or b + c <= a: return None
    return ch([num(f'Uchburchak tomonlari {a}, {b} va {c} sm. Perimetri necha sm?', a + b + c), num(f'Kvadrat perimetri {4 * a} sm. Tomoni necha sm?', a),
               num(f'Muntazam oltiburchakning tomoni {a} sm. Perimetri necha sm?', 6 * a)])
def pe3():
    a, b = ri(2, 20), ri(2, 20)
    if a == b: return None
    return ch([num(f'Toʻgʻri toʻrtburchak perimetri {2 * (a + b)} sm, bir tomoni {a} sm. Ikkinchi tomoni necha sm?', b),
               num(f'Toʻgʻri toʻrtburchakning eni {a} sm, boʻyi undan {b} sm uzun. Perimetri necha sm?', 2 * (2 * a + b)),
               num(f'Teng tomonli uchburchak perimetri {3 * a} sm. Tomoni necha sm?', a)])
topic(B10, 'perimetr', 'Perimetr', pe1, pe2, pe3)

def yz1():
    a, b = ri(2, 15), ri(2, 15)
    return ch([num(f'Kvadratning tomoni {a} sm. Yuzi necha sm²?', a * a), num(f'Toʻgʻri toʻrtburchakning tomonlari {a} va {b} sm. Yuzi necha sm²?', a * b)])
def yz2():
    a, b = ri(2, 20), ri(2, 20)
    return ch([num(f'Toʻgʻri toʻrtburchak yuzi {a * b} sm², bir tomoni {a} sm. Ikkinchi tomoni necha sm?', b), num(f'Kvadrat yuzi {a * a} sm². Tomoni necha sm?', a),
               num(f'Toʻgʻri burchakli uchburchak katetlari {a * 2} va {b} sm. Yuzi necha sm²?', a * b)])
def yz3():
    a, b = ri(2, 15), ri(2, 15)
    return ch([num(f'Kvadrat perimetri {4 * a} sm. Yuzi necha sm²?', a * a), num(f'Toʻgʻri toʻrtburchak yuzi {a * b} sm², bir tomoni {a} sm. Perimetri necha sm?', 2 * (a + b)),
               num(f'Xona {a} m ga {b} m. Polga necha m² gilam kerak?', a * b), num(f'Kvadrat tomoni 2 marta oshirilsa, yuzi necha marta oshadi?', 4)])
topic(B10, 'yuz', 'Toʻgʻri toʻrtburchak va kvadratning yuzi', yz1, yz2, yz3)

def ay1():
    r = ri(2, 30)
    return ch([num(f'Aylana radiusi {r} sm. Diametri necha sm?', 2 * r), num(f'Aylana diametri {2 * r} sm. Radiusi necha sm?', r),
               mc('Aylana markazini aylana nuqtasi bilan tutashtiruvchi kesma nima deyiladi?', 'Radius', ['Diametr', 'Vatar', 'Urinma']),
               mc('Aylananing eng uzun vatari qaysi?', 'Diametr', ['Radius', 'Urinma', 'Yoy'])])
def ay2():
    r = ri(1, 20)
    return ch([num(f'Radiusi {r} sm boʻlgan aylana uzunligini toping (π ≈ 3).', 6 * r), num(f'Radiusi {r} sm boʻlgan doira yuzini toping (π ≈ 3).', 3 * r * r)])
def ay3():
    r = ch([1, 2, 5, 10, 20, 50])
    return ch([mc(f'Radiusi {r} sm aylana uzunligi (π ≈ 3,14)?', dec(2 * 3.14 * r) + ' sm', [dec(3.14 * r) + ' sm', dec(3.14 * r * r) + ' sm', dec(2 * 3.14 * r + 1) + ' sm']),
               mc(f'Radiusi {r} sm doira yuzi (π ≈ 3,14)?', dec(3.14 * r * r) + ' sm²', [dec(2 * 3.14 * r) + ' sm²', dec(3.14 * r * r * 2) + ' sm²', dec(3.14 * r) + ' sm²'])])
topic(B10, 'aylana', 'Aylana va doira', ay1, ay2, ay3)

sim1 = [num('Kvadratning nechta simmetriya oʻqi bor?', 4), num('Teng tomonli uchburchakning nechta simmetriya oʻqi bor?', 3), num('Toʻgʻri toʻrtburchakning (kvadrat emas) nechta simmetriya oʻqi bor?', 2),
        mc('Aylananing nechta simmetriya oʻqi bor?', 'Cheksiz koʻp', ['1 ta', '2 ta', '4 ta']), mc('Qaysi harfning vertikal simmetriya oʻqi bor?', 'A', ['F', 'R', 'G']),
        mc('Qaysi harfning simmetriya oʻqi yoʻq?', 'F', ['A', 'H', 'O']), num('Teng yonli uchburchakning (teng tomonli emas) nechta simmetriya oʻqi bor?', 1),
        mc('Qaysi raqamning gorizontal simmetriya oʻqi bor?', '3', ['7', '4', '2']), num('Muntazam oltiburchakning nechta simmetriya oʻqi bor?', 6),
        mc('Koʻzgudagi aks qaysi simmetriyaga misol?', 'Oʻqqa nisbatan simmetriya', ['Burilish', 'Parallel koʻchirish', 'Oʻxshashlik'])]
def sim2():
    x, y = ri(1, 9), ri(1, 9)
    ax = ch(['Ox', 'Oy'])
    r = f'({x}; −{y})' if ax == 'Ox' else f'(−{x}; {y})'
    return mc(f'A({x}; {y}) nuqtaning {ax} oʻqiga nisbatan simmetrik nuqtasi?', r, [f'(−{x}; −{y})', f'({y}; {x})', f'({x}; −{y})' if ax == 'Oy' else f'(−{x}; {y})'])
def sim3():
    x, y = ri(1, 9), ri(1, 9)
    if R.random() < .5: return mc(f'A({x}; {y}) nuqtaning koordinata boshiga nisbatan simmetrik nuqtasi?', f'(−{x}; −{y})', [f'({x}; −{y})', f'(−{x}; {y})', f'({y}; {x})'])
    a = ri(1, 20)
    return num(f'Toʻgʻri chiziqdan {a} sm uzoqlikdagi nuqta va uning shu chiziqqa nisbatan simmetrigi orasidagi masofa necha sm?', 2 * a)
topic(B10, 'simmetriya', 'Toʻgʻri chiziqqa nisbatan simmetriya', sim1, sim2, sim3)

# ================= 11-BOB: stereometriya =================
kub1 = [num('Kubning nechta qirrasi bor?', 12), num('Kubning nechta yogʻi bor?', 6), num('Kubning nechta uchi bor?', 8), mc('Kubning yoqlari qanday shakl?', 'Kvadrat', ['Uchburchak', 'Toʻgʻri toʻrtburchak (kvadrat emas)', 'Doira']),
        num('Kubning bir uchida nechta qirra tutashadi?', 3)]
def kub1g():
    a = ri(2, 12)
    return ch([num(f'Kub qirrasi {a} sm. Barcha qirralari yigʻindisi necha sm?', 12 * a), ch(kub1)])
def kub2():
    a = ri(2, 15)
    return ch([num(f'Kub qirrasi {a} sm. Hajmi necha sm³?', a ** 3) if a ** 3 <= 9999 else None, num(f'Kub qirrasi {a} sm. Bir yogʻining yuzi necha sm²?', a * a)])
def kub3():
    a = ri(2, 21)
    return ch([num(f'Kub hajmi {a ** 3} sm³. Qirrasi necha sm?', a) if a <= 10 else None, num(f'Kub qirrasi {a} sm. Toʻla sirti necha sm²?', 6 * a * a) if a <= 10 else None,
               num(f'Kub qirralari yigʻindisi {12 * a} sm. Qirrasi necha sm?', a), num('Kub qirrasi 2 marta oshirilsa, hajmi necha marta oshadi?', 8)])
topic(B11, 'kub', 'Kub', kub1g, kub2, kub3)

def pp1():
    a, b, c = ri(2, 10), ri(2, 10), ri(2, 10)
    return ch([num(f'Parallelepiped oʻlchamlari {a}, {b} va {c} sm. Hajmi necha sm³?', a * b * c), num('Toʻgʻri burchakli parallelepipedning nechta yogʻi bor?', 6),
               num('Toʻgʻri burchakli parallelepipedning nechta qirrasi bor?', 12)])
def pp2():
    a, b, c = ri(2, 12), ri(2, 12), ri(2, 12)
    return ch([num(f'Parallelepiped oʻlchamlari {a}, {b} va {c} sm. Barcha qirralari yigʻindisi necha sm?', 4 * (a + b + c)),
               num(f'Parallelepiped hajmi {a * b * c} sm³, asosi {a} sm ga {b} sm. Balandligi necha sm?', c)])
def pp3():
    a, b, c = ri(2, 12), ri(2, 12), ri(2, 12)
    s = 2 * (a * b + b * c + a * c)
    return ch([num(f'Parallelepiped oʻlchamlari {a}, {b} va {c} sm. Toʻla sirti necha sm²?', s),
               num(f'Akvarium {a * 10} sm × {b * 10} sm × {c * 10} sm. Unga necha litr suv sigʻadi?', a * b * c) if max(a, b, c) <= 6 else None])
topic(B11, 'parallelepiped', 'Toʻgʻri burchakli parallelepiped', pp1, pp2, pp3)

PN = {3: 'Uchburchakli', 4: 'Toʻrtburchakli', 5: 'Beshburchakli', 6: 'Oltiburchakli', 7: 'Yettiburchakli', 8: 'Sakkizburchakli', 10: 'Oʻnburchakli', 12: 'Oʻn ikki burchakli'}
def pz(ns):
    def g():
        n = ch(ns); w = ch([('nechta yogʻi', n + 2), ('nechta qirrasi', 3 * n), ('nechta uchi', 2 * n), ('nechta yon yogʻi', n)])
        return num(f'{PN[n]} prizmaning {w[0]} bor?', w[1])
    return g
def pz3():
    if R.random() < .4:
        S, h = ri(3, 30), ri(2, 12)
        return num(f'Prizma asosining yuzi {S} sm², balandligi {h} sm. Hajmi necha sm³?', S * h)
    n = ch([5, 6, 7, 8, 10, 12])
    k = ch([('qirrasi', 3 * n), ('uchi', 2 * n), ('yogʻi', n + 2)])
    return num(f'Prizmaning {k[1]} ta {k[0]} bor. Asosi necha burchakli?', n)
topic(B11, 'prizma', 'Prizma', pz([3, 4]), pz([5, 6, 8]), pz3)

# ---- sinflar (Oʻzbekiston maktab dasturi boʻyicha taxminiy) ----
SINF = {
 'qoshish': [5], 'ayirish': [5], 'kopaytirish': [5], 'bolish': [5], 'aralash': [5], 'tenglama1': [5],
 'natural': [5], 'taqqoslash': [5], 'boshqotirma': [5, 6], 'butun': [6], 'sonoqi': [6], 'daraja': [5, 7], 'faktorial': [6, 7], 'rim': [5],
 'qoldiq': [5], 'belgilar': [6], 'boluvchi': [6], 'ekub': [6],
 'kasr': [5], 'kasrxossa': [5, 6], 'kasrkopbol': [6], 'kasrqosh': [5, 6], 'umumiymaxraj': [6], 'kasraralash': [6],
 'onli': [5], 'onliqosh': [5], 'onlikop': [5, 6],
 'darajaxossa': [7], 'qavs': [6, 7], 'oxshash': [6, 7], 'tenglama2': [6, 7], 'proporsiya': [6],
 'masala': [5], 'yosh': [5, 6], 'proporsional': [6], 'olchov': [5], 'masshtab': [6], 'foiz': [5, 6], 'foyda': [6], 'vaqt': [5],
 'sistema': [7], 'harakat': [5, 6], 'ish': [6],
 'nuqta': [5], 'burchak': [5], 'uchburchak': [6, 7], 'perimetr': [5], 'yuz': [5], 'aylana': [6], 'simmetriya': [6],
 'kub': [5], 'parallelepiped': [5], 'prizma': [6],
}
for t in TOPICS:
    t['sinf'] = SINF[t['id']]

# ---- tekshiruv va yozish ----
ids = [t['id'] for t in TOPICS]; assert len(ids) == len(set(ids))
for t in TOPICS:
    for it in t['items']:
        if 'o' in it:
            assert len(it['o']) == 4 and len(set(it['o'])) == 4 and 0 <= it['c'] < 4, (t['id'], it)
        else:
            assert 0 <= it['a'] <= 9999
bobs = []
for t in TOPICS:
    if t['bob'] not in bobs: bobs.append(t['bob'])
out = {'fan': 'Matematika', 'v': 1, 'bolimlar': bobs, 'topics': TOPICS}
p = os.path.join(os.path.dirname(__file__), '..', 'games', 'baza', 'matematika.json')
os.makedirs(os.path.dirname(p), exist_ok=True)
json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(len(TOPICS), 'mavzu,', sum(len(t['items']) for t in TOPICS), 'savol,', os.path.getsize(p) // 1024, 'KB')
for t in TOPICS:
    c = [sum(1 for i in t['items'] if i['d'] == d) for d in (1, 2, 3)]
    if min(c) < 10: print('  kam:', t['id'], c)
