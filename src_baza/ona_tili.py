# -*- coding: utf-8 -*-
"""Ona tili va adabiyot (5–9-sinf) savollar bazasi: games/baza/ona-tili.json
Savollar faktlar jadvallaridan yasaladi (har bir fakt bir marta tekshirilgan) + qoʻlda yozilgan savollar.
Ishga tushirish: python3 src_baza/ona_tili.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Baza

B = Baza('Ona tili va adabiyot', 'ona-tili', 2027)
R = B.R; ch = R.choice; mc = B.mc; num = B.num

F1 = 'Fonetika va leksika'; F2 = 'Morfologiya'; F3 = 'Sintaksis'; F4 = 'Adabiyot'

def cls(q_tpl, data, labels):
    """data: {toifa: [soʻzlar]} → «soʻz» qaysi toifaga kiradi? (variantlar — toifalar)"""
    def g():
        lab = ch(list(data)); w = ch(data[lab])
        others = [x for x in labels if x != lab]
        return mc(q_tpl.format(w=w), lab, R.sample(others, 3))
    return g

def pick_one(q_tpl, data, lab):
    """«Qaysi soʻz {lab}?» — bitta toʻgʻri, 3 ta boshqa toifadan"""
    def g():
        w = ch(data[lab]); pool = [x for k, v in data.items() if k != lab for x in v]
        return mc(q_tpl, w, R.sample(pool, 3))
    return g

# ======================= FONETIKA =======================
UNLI = ['a', 'o', 'u', 'i', 'e', 'oʻ']
UNDOSH = ['b', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'x', 'y', 'z', 'gʻ', 'sh', 'ch', 'ng']
JUFT = [('b', 'p'), ('d', 't'), ('g', 'k'), ('z', 's'), ('v', 'f')]   # jarangli – jarangsiz
fon1 = [mc('Oʻzbek tilida nechta unli tovush bor?', '6', ['5', '8', '23']), mc('Qaysi harf unli tovushni bildiradi?', 'oʻ', ['gʻ', 'sh', 'ng']),
        mc('Unli tovush qanday hosil boʻladi?', 'Havo ogʻiz boʻshligʻida toʻsiqqa uchramaydi', ['Havo toʻsiqqa uchraydi', 'Faqat burun orqali chiqadi', 'Lablar yopiq holda']),
        mc('Undosh tovush qanday hosil boʻladi?', 'Havo ogʻiz boʻshligʻida toʻsiqqa uchraydi', ['Havo erkin chiqadi', 'Faqat ovoz bilan', 'Hech qanday toʻsiqsiz'])]
def fon_g1():
    if R.random() < .3: return ch(fon1)
    u = ch(UNLI); return mc('Qaysi harf unli tovushni bildiradi?', u, R.sample(UNDOSH, 3))
def fon_g2():
    t = R.randrange(3)
    if t == 0: d = ch(UNDOSH); return mc('Qaysi harf undosh tovushni bildiradi?', d, R.sample(UNLI, 3))
    j = ch(JUFT)
    if t == 1: return mc(f'«{j[0]}» jarangli undoshining jarangsiz jufti qaysi?', j[1], [x[1] for x in JUFT if x != j])
    return mc(f'«{j[1]}» jarangsiz undoshining jarangli jufti qaysi?', j[0], [x[0] for x in JUFT if x != j])
def fon_g3():
    t = R.randrange(3)
    if t == 0: j = ch(JUFT); return mc('Qaysi undosh jarangli?', j[0], R.sample([x[1] for x in JUFT], 3))
    if t == 1: j = ch(JUFT); return mc('Qaysi undosh jarangsiz?', j[1], R.sample([x[0] for x in JUFT], 3))
    return ch([mc('«sh», «ch», «ng» qanday harflar?', 'Harf birikmalari (bitta tovush)', ['Ikki tovushli harflar', 'Unli harflar', 'Tutuq belgilari']),
               mc('Tutuq belgisi (ʼ) qaysi soʻzda ishlatiladi?', 'maʼno', ['maktab', 'kitob', 'daraxt']),
               mc('«ng» harf birikmasi qaysi soʻzda bor?', 'tong', ['tosh', 'toʻp', 'tuz'])])
B.topic(F1, 'unli', 'Unli va undosh tovushlar', [5], fon_g1, fon_g2, fon_g3, 'fonetika tovush harf unli undosh jarangli')

# ---- boʻgʻin ----
SYL = ['ki-tob', 'mak-tab', 'qa-lam', 'o-na', 'bo-la', 'sa-lom', 'ba-hor', 'ta-rix', 'sha-har', 'u-zum', 'ol-ma', 'qu-yosh', 'va-tan', 'dar-yo',
       'mam-la-kat', 'oʻ-quv-chi', 'dars-lik', 'ka-lit', 'ku-tub-xo-na', 'do-ri-xo-na', 'sa-yo-hat', 'qish-loq', 'pax-ta', 'daf-tar', 'mak-tab-dosh',
       'gul-zor', 'sa-mo-lyot', 'te-le-fon', 'ta-bi-at', 'ki-tob-xon', 'oʻ-qi-tuv-chi', 'tar-vuz', 'ba-liq', 'yul-duz', 'ka-ka-li-k']
SYL = [s for s in SYL if not s.endswith('-k')]
def vow(w):
    return sum(1 for ch_ in w.replace('oʻ', 'o') if ch_ in 'aeiou')
for s in SYL:
    assert vow(s.replace('-', '')) == len(s.split('-')), s
def bg_g1():
    s = ch(SYL); w = s.replace('-', ''); n = len(s.split('-'))
    return mc(f'«{w}» soʻzida nechta boʻgʻin bor?', str(n), [str(x) for x in (1, 2, 3, 4, 5) if x != n])
def bg_g2():
    s = ch([x for x in SYL if len(x.split('-')) >= 2]); w = s.replace('-', ''); p = s.split('-')
    t = R.randrange(2)
    if t == 0:
        s = ch([x for x in SYL if len(x.split('-')) == 2]); w = s.replace('-', ''); p = s.split('-')
        return mc(f'«{w}» soʻzi qanday boʻgʻinlarga ajraladi?', ' – '.join(p), [' – '.join(x) for x in wrong_splits(w, p)])
    return mc('Boʻgʻinlar soni nimaga teng?', 'Unli tovushlar soniga', ['Undoshlar soniga', 'Harflar soniga', 'Soʻzdagi qoʻshimchalar soniga'])
def wrong_splits(w, p):
    """notoʻgʻri boʻgʻin boʻlishlari"""
    cut = len(p[0]); out = []
    for d in (-1, 1, 2, -2):
        c = cut + d
        if 1 <= c < len(w):
            out.append([w[:c], w[c:]] if len(p) == 2 else [w[:c], w[c:]])
    return [x for x in out if '-'.join(x) != '-'.join(p)][:3] or [[w]]
def bg_g3():
    t = R.randrange(3)
    s = ch([x for x in SYL if len(x.split('-')) >= 2]); w = s.replace('-', ''); p = s.split('-')
    if t == 0:
        op = [x for x in p if x[-1] in 'aeiou']
        if not op: return None
        cl = [x for x in p if x[-1] not in 'aeiou'] + ['mak', 'tob', 'lam', 'zor']
        return mc('Qaysi boʻgʻin ochiq (unli bilan tugaydi)?', op[0], R.sample([x for x in cl if x not in op], 3))
    if t == 1:
        cl = [x for x in p if x[-1] not in 'aeiou']
        if not cl: return None
        return mc('Qaysi boʻgʻin yopiq (undosh bilan tugaydi)?', cl[0], R.sample([x for x in ['ki', 'bo', 'o', 'sa', 'ba', 'qa', 'da', 'ta'] if x not in cl], 3))
    return ch([mc('Soʻzni satrdan satrga koʻchirishda nimaga amal qilinadi?', 'Boʻgʻinlab koʻchiriladi', ['Harflab koʻchiriladi', 'Istalgan joydan', 'Faqat oʻzakdan']),
               mc('Qaysi soʻz toʻgʻri koʻchirilgan?', 'mak-tab', ['ma-ktab', 'makt-ab', 'm-aktab']), mc('Qaysi soʻz toʻgʻri koʻchirilgan?', 'daf-tar', ['da-ftar', 'daft-ar', 'd-aftar']),
               mc('Qaysi soʻzni koʻchirib boʻlmaydi?', 'olma emas, «ilm»', ['kitob', 'maktab', 'qalam']) if False else mc('Qaysi soʻzni boʻgʻinga boʻlib koʻchirib boʻlmaydi?', 'ilm', ['kitob', 'maktab', 'qalam'])])
B.topic(F1, 'bogin', 'Boʻgʻin va boʻgʻin koʻchirish', [5], bg_g1, bg_g2, bg_g3, 'fonetika boʻgʻin koʻchirish')

# ======================= LEKSIKA =======================
SIN = [('katta', 'ulkan'), ('chiroyli', 'goʻzal'), ('aqlli', 'dono'), ('quvonch', 'shodlik'), ('qaygʻu', 'gʻam'), ('doʻst', 'oʻrtoq'), ('kuchli', 'baquvvat'),
       ('boy', 'badavlat'), ('Vatan', 'Yurt'), ('gapirmoq', 'soʻzlamoq'), ('kelajak', 'istiqbol'), ('ulugʻ', 'buyuk'), ('qoʻrqoq', 'yuraksiz'), ('mehnat', 'ish'),
       ('yuz', 'bet'), ('tez', 'chaqqon'), ('kulmoq', 'jilmaymoq'), ('baxt', 'saodat'), ('xursand', 'shod'), ('qadrdon', 'aziz')]
ANT = [('katta', 'kichik'), ('issiq', 'sovuq'), ('yaxshi', 'yomon'), ('oq', 'qora'), ('baland', 'past'), ('keng', 'tor'), ('yangi', 'eski'), ('kun', 'tun'),
       ('doʻst', 'dushman'), ('kulmoq', 'yigʻlamoq'), ('kirmoq', 'chiqmoq'), ('ochmoq', 'yopmoq'), ('yosh', 'qari'), ('uzun', 'qisqa'), ('ogʻir', 'yengil'),
       ('shirin', 'achchiq'), ('boy', 'kambagʻal'), ('erta', 'kech'), ('tez', 'sekin'), ('yoz', 'qish'), ('yaqin', 'uzoq'), ('koʻp', 'oz'), ('chap', 'oʻng'), ('quvnoq', 'gʻamgin')]
OMO = [('ot', 'hayvon va ism'), ('yuz', 'bet va son (100)'), ('oʻt', 'olov va maysa'), ('qoʻy', 'hayvon va «qoʻymoq» fe’li'), ('yoz', 'fasl va «yozmoq» fe’li'),
       ('tor', 'cholgʻu asbobi va «keng emas»'), ('chang', 'gʻubor va cholgʻu asbobi'), ('koʻk', 'rang va osmon'), ('soz', 'cholgʻu va «yaxshi, mos»'), ('tush', 'kunduzgi vaqt va uyqudagi koʻrinish')]
OMO_W = [x[0] for x in OMO]; NON_OMO = ['kitob', 'daftar', 'qalam', 'maktab', 'daraxt', 'olma', 'stol', 'deraza', 'quyosh', 'shahar']
LEX = ['Sinonimlar', 'Antonimlar', 'Omonimlar', 'Paronimlar']
def lx_g1():
    t = R.randrange(2)
    if t == 0:
        a, b = ch(SIN); ant = [x[1] for x in ANT if x[0] == a]
        pool = [y for x in SIN if x != (a, b) for y in x if y != a]
        return mc(f'«{a}» soʻzining sinonimi qaysi?', b, ant[:1] + R.sample(pool, 3 - len(ant[:1])))
    a, b = ch(ANT); sin = [x[1] for x in SIN if x[0] == a]
    pool = [y for x in ANT if x != (a, b) for y in x if y != a]
    return mc(f'«{a}» soʻzining antonimi qaysi?', b, sin[:1] + R.sample(pool, 3 - len(sin[:1])))
def lx_g2():
    t = R.randrange(3)
    if t == 0: a, b = ch(SIN); return mc(f'«{a} – {b}» qanday soʻzlar?', 'Sinonimlar', ['Antonimlar', 'Omonimlar', 'Paronimlar'])
    if t == 1: a, b = ch(ANT); return mc(f'«{a} – {b}» qanday soʻzlar?', 'Antonimlar', ['Sinonimlar', 'Omonimlar', 'Paronimlar'])
    return mc('Shakli bir xil, maʼnosi har xil soʻzlar qanday ataladi?', 'Omonimlar', ['Sinonimlar', 'Antonimlar', 'Paronimlar'])
lx3 = [mc('Maʼnosi yaqin, shakli har xil soʻzlar qanday ataladi?', 'Sinonimlar', ['Omonimlar', 'Antonimlar', 'Paronimlar']),
       mc('Qarama-qarshi maʼnoli soʻzlar qanday ataladi?', 'Antonimlar', ['Sinonimlar', 'Omonimlar', 'Paronimlar'])]
def lx_g3():
    if R.random() < .15: return ch(lx3)
    w, m = ch(OMO)
    if R.random() < .5: return mc('Qaysi soʻz omonim?', w, R.sample(NON_OMO, 3))
    return mc(f'«{w}» soʻzining maʼnolari: {m}. Bu qanday soʻz?', 'Omonim', ['Sinonim', 'Antonim', 'Atoqli ot'])
B.topic(F1, 'leksika', 'Sinonim, antonim va omonimlar', [5, 6], lx_g1, lx_g2, lx_g3, 'leksika maʼno sinonim antonim omonim')

# ======================= MORFOLOGIYA =======================
TURKUM = {
 'Ot': ['kitob', 'daftar', 'maktab', 'olma', 'daraxt', 'quyosh', 'doʻstlik', 'bilim', 'shahar', 'bahor', 'qalam', 'togʻ', 'daryo', 'gul', 'qush', 'stol', 'mehnat', 'Toshkent'],
 'Sifat': ['chiroyli', 'qizil', 'katta', 'kichik', 'shirin', 'baland', 'aqlli', 'yashil', 'keng', 'issiq', 'sovuq', 'yangi', 'eski', 'mehribon', 'oq', 'uzun', 'kuchli', 'toza'],
 'Son': ['bir', 'besh', 'oʻn', 'yuz', 'ming', 'birinchi', 'uchinchi', 'ikkita', 'beshta', 'oʻninchi', 'yetti', 'toʻqqiz', 'yigirma'],
 'Olmosh': ['men', 'sen', 'biz', 'siz', 'ular', 'kim', 'nima', 'bu', 'shu', 'oʻsha', 'hamma', 'barcha', 'qayer'],
 'Feʼl': ['oʻqimoq', 'yozmoq', 'bormoq', 'keldi', 'kuldi', 'yugurmoq', 'oʻynamoq', 'gapirdi', 'ishlamoq', 'koʻrmoq', 'uxlamoq', 'oʻqidi', 'yozdi'],
 'Ravish': ['sekin', 'asta-sekin', 'hozir', 'doim', 'hamisha', 'tez-tez', 'ertalab', 'kechqurun', 'yayov', 'birdan', 'ataylab', 'zoʻrgʻa'],
}
TL = list(TURKUM)
TUR_GAP = [('Ali tez-tez kitob oʻqiydi.', 'tez-tez', 'Ravish'), ('Bogʻda qizil gullar ochildi.', 'qizil', 'Sifat'), ('Men uchta olma oldim.', 'uchta', 'Son'),
           ('Ular maktabga ketdi.', 'ular', 'Olmosh'), ('Bolalar hovlida oʻynadi.', 'oʻynadi', 'Feʼl'), ('Daraxtlar kuzda sargʻaydi.', 'daraxtlar', 'Ot'),
           ('Biz ertalab yugurdik.', 'ertalab', 'Ravish'), ('Kecha yangi kitob sotib oldim.', 'yangi', 'Sifat'), ('Sinfimizda yigirma oʻquvchi bor.', 'yigirma', 'Son'),
           ('U doim rost gapiradi.', 'doim', 'Ravish'), ('Bu kitob juda qiziqarli.', 'bu', 'Olmosh'), ('Qushlar janubga uchib ketdi.', 'qushlar', 'Ot')]
def tk_g1():
    lab = ch(['Ot', 'Sifat', 'Feʼl']); w = ch(TURKUM[lab])
    return mc(f'«{w}» soʻzi qaysi soʻz turkumiga kiradi?', lab, R.sample([x for x in TL if x != lab], 3))
tk_g2 = cls('«{w}» soʻzi qaysi soʻz turkumiga kiradi?', TURKUM, TL)
def tk_g3():
    if R.random() < .6:
        s, w, lab = ch(TUR_GAP); return mc(f'«{s}» gapida «{w}» soʻzi qaysi soʻz turkumi?', lab, R.sample([x for x in TL if x != lab], 3))
    return ch([mc('Ot qanday soʻroqlarga javob beradi?', 'kim? nima? qayer?', ['qanday? qanaqa?', 'nima qildi?', 'qachon? qanday?']),
               mc('Sifat qanday soʻroqlarga javob beradi?', 'qanday? qanaqa? qaysi?', ['kim? nima?', 'nima qildi?', 'nechta?']),
               mc('Feʼl qanday soʻroqlarga javob beradi?', 'nima qildi? nima qilyapti?', ['kim? nima?', 'qanday?', 'nechta?']),
               mc('Son qanday soʻroqlarga javob beradi?', 'nechta? qancha? nechanchi?', ['kim? nima?', 'qanday?', 'nima qildi?']),
               mc('Qaysi soʻz turkumi mustaqil emas?', 'Koʻmakchi', ['Ot', 'Sifat', 'Feʼl'])])
B.topic(F2, 'turkum', 'Soʻz turkumlari', [5, 6], tk_g1, tk_g2, tk_g3, 'morfologiya turkum ot sifat feʼl son olmosh ravish')

# ---- soʻz tarkibi ----
TARKIB = [('kitobchalar', 'kitob'), ('maktabimizda', 'maktab'), ('gulzor', 'gul'), ('ishchi', 'ish'), ('paxtakor', 'paxta'), ('bilim', 'bil'),
          ('oʻqituvchi', 'oʻqi'), ('togʻlar', 'togʻ'), ('bogʻbon', 'bogʻ'), ('suvsiz', 'suv'), ('aqlli', 'aql'), ('doʻstlik', 'doʻst'), ('qalamdon', 'qalam'),
          ('yozuvchi', 'yoz'), ('sinfdosh', 'sinf'), ('gullar', 'gul'), ('uylarimizdan', 'uy'), ('kitobxon', 'kitob'), ('ishchan', 'ish'), ('daraxtzor', 'daraxt')]
SOZ_Y = ['-chi', '-zor', '-kor', '-bon', '-dosh', '-li', '-siz', '-lik', '-don', '-xon', '-chan']
SHAKL_Y = ['-lar', '-ni', '-ga', '-da', '-dan', '-ning', '-im', '-ing', '-roq', '-di']
def st_g1():
    w, r = ch(TARKIB)
    wr = list({w[:i] for i in range(2, len(w)) if w[:i] != r and len(w[:i]) != len(r)}) + [w]
    return mc(f'«{w}» soʻzining oʻzagi qaysi?', r, R.sample(wr, min(3, len(wr))) if len(wr) >= 3 else wr)
def st_g2():
    t = R.randrange(2)
    if t == 0: return mc('Qaysi qoʻshimcha yangi soʻz yasaydi?', ch(SOZ_Y), R.sample(SHAKL_Y, 3))
    return mc('Qaysi qoʻshimcha soʻz shaklini oʻzgartiradi (yangi soʻz yasamaydi)?', ch(SHAKL_Y), R.sample(SOZ_Y, 3))
st3 = [mc('Soʻzning maʼno anglatuvchi asosiy qismi nima deyiladi?', 'Oʻzak', ['Qoʻshimcha', 'Boʻgʻin', 'Tovush']),
       mc('«gulzor» soʻzida «-zor» qanday qoʻshimcha?', 'Soʻz yasovchi', ['Shakl yasovchi', 'Kelishik qoʻshimchasi', 'Egalik qoʻshimchasi']),
       mc('«gullar» soʻzida «-lar» qanday qoʻshimcha?', 'Shakl yasovchi (koʻplik)', ['Soʻz yasovchi', 'Kelishik qoʻshimchasi', 'Egalik qoʻshimchasi']),
       mc('«ishchi» soʻzi qanday yasalgan?', 'ish + -chi', ['is + -hchi', 'ishch + -i', 'i + -shchi']),
       mc('«paxtakor» soʻzi qanday yasalgan?', 'paxta + -kor', ['pax + -takor', 'paxtak + -or', 'paxt + -akor']),
       mc('«sinfdosh» soʻzi qanday yasalgan?', 'sinf + -dosh', ['sin + -fdosh', 'sinfd + -osh', 'si + -nfdosh']),
       mc('Qaysi soʻz yasama soʻz?', 'bogʻbon', ['bogʻ', 'togʻ', 'suv']), mc('Qaysi soʻz tub (yasalmagan) soʻz?', 'olma', ['gulzor', 'ishchi', 'aqlli']),
       mc('«aqlli» soʻzi qaysi qoʻshimcha bilan yasalgan?', '-li', ['-lar', '-lik', '-siz']), mc('«suvsiz» soʻzi qaysi qoʻshimcha bilan yasalgan?', '-siz', ['-li', '-lik', '-chi']),
       mc('«doʻstlik» soʻzi qaysi qoʻshimcha bilan yasalgan?', '-lik', ['-li', '-lar', '-siz'])]
B.topic(F2, 'tarkib', 'Soʻz tarkibi: oʻzak va qoʻshimcha', [5], st_g1, st_g2, st3, 'morfologiya oʻzak qoʻshimcha yasovchi')

# ---- ot ----
ATOQLI = ['Toshkent', 'Amudaryo', 'Samarqand', 'Navroʻz', 'Oʻzbekiston', 'Zarafshon', 'Buxoro', 'Sirdaryo', 'Fargʻona', 'Xiva', 'Andijon', 'Nukus']
TURDOSH = ['shahar', 'daryo', 'bola', 'togʻ', 'bayram', 'mamlakat', 'kitob', 'vodiy', 'qishloq', 'koʻl', 'maktab', 'daraxt']
MAVHUM = ['doʻstlik', 'baxt', 'quvonch', 'bilim', 'mehr', 'sevgi', 'qaygʻu', 'orzu', 'tinchlik', 'shodlik']
ANIQ = ['stol', 'daraxt', 'qalam', 'uy', 'olma', 'deraza', 'mashina', 'kitob', 'non', 'kursi']
def ot_g1():
    t = R.randrange(2)
    if t == 0: return mc('Qaysi soʻz atoqli ot?', ch(ATOQLI), R.sample(TURDOSH, 3))
    return mc('Qaysi soʻz turdosh ot?', ch(TURDOSH), R.sample(ATOQLI, 3))
def ot_g2():
    t = R.randrange(3)
    if t == 0: return mc('Qaysi ot mavhum (koʻz bilan koʻrib boʻlmaydigan) tushunchani bildiradi?', ch(MAVHUM), R.sample(ANIQ, 3))
    if t == 1: return mc('Qaysi ot aniq narsani bildiradi?', ch(ANIQ), R.sample(MAVHUM, 3))
    return ch([mc('Atoqli otlar qanday yoziladi?', 'Bosh harf bilan', ['Kichik harf bilan', 'Qoʻshtirnoqda', 'Chiziqcha bilan']),
               mc('Ot qanday soʻroqlarga javob beradi?', 'kim? nima? qayer?', ['qanday?', 'nima qildi?', 'nechta?'])])
def ot_g3():
    w = ch(['kitob', 'gul', 'qush', 'daraxt', 'bola', 'shahar', 'olma']); t = R.randrange(3)
    if t == 0: return mc(f'«{w}lar» soʻzida «-lar» nimani bildiradi?', 'Koʻplikni', ['Egalikni', 'Kelishikni', 'Kichraytirishni'])
    if t == 1: return mc('Qaysi qoʻshimcha otga kichraytirish maʼnosini beradi?', '-cha', ['-lar', '-ni', '-dan'])
    return mc('Qaysi soʻz koʻplik shaklida?', f'{w}lar', [f'{w}ni', f'{w}da', f'{w}cha'])
B.topic(F2, 'ot', 'Ot: turdosh va atoqli, aniq va mavhum', [5], ot_g1, ot_g2, ot_g3, 'morfologiya ot atoqli turdosh')

# ---- kelishiklar ----
KEL = [('Bosh kelishik', '', 'kim? nima?'), ('Qaratqich kelishigi', 'ning', 'kimning? nimaning?'), ('Tushum kelishigi', 'ni', 'kimni? nimani?'),
       ('Joʻnalish kelishigi', 'ga', 'kimga? nimaga? qayerga?'), ('Oʻrin-payt kelishigi', 'da', 'kimda? nimada? qayerda?'), ('Chiqish kelishigi', 'dan', 'kimdan? nimadan? qayerdan?')]
KW_ = ['kitob', 'maktab', 'bogʻ', 'shahar', 'daftar', 'uy', 'Toshkent', 'gul', 'stol', 'bola']
KN = [k[0] for k in KEL]
def kl_g1():
    k = ch(KEL[1:]); w = ch(KW_)
    return mc(f'«{w}{k[1]}» soʻzi qaysi kelishikda?', k[0], R.sample([x for x in KN if x != k[0]], 3))
def kl_g2():
    t = R.randrange(2); k = ch(KEL[1:])
    if t == 0: return mc(f'{k[0]} qoʻshimchasi qaysi?', '-' + k[1], R.sample(['-' + x[1] for x in KEL[1:] if x != k] + ['-lar', '-im'], 3))
    return mc(f'«{k[2]}» soʻroqlari qaysi kelishikka tegishli?', k[0], R.sample([x for x in KN if x != k[0]], 3))
kl3 = [mc('Oʻzbek tilida nechta kelishik bor?', '6', ['5', '7', '4']), mc('Qaysi kelishikning maxsus qoʻshimchasi yoʻq?', 'Bosh kelishik', ['Tushum kelishigi', 'Joʻnalish kelishigi', 'Chiqish kelishigi']),
       mc('«Men kitobni oʻqidim» gapida «kitobni» qaysi kelishikda?', 'Tushum kelishigi', ['Qaratqich kelishigi', 'Joʻnalish kelishigi', 'Bosh kelishik']),
       mc('«Biz maktabdan qaytdik» gapida «maktabdan» qaysi kelishikda?', 'Chiqish kelishigi', ['Oʻrin-payt kelishigi', 'Joʻnalish kelishigi', 'Tushum kelishigi']),
       mc('«Ukam bogʻda oʻynayapti» gapida «bogʻda» qaysi kelishikda?', 'Oʻrin-payt kelishigi', ['Chiqish kelishigi', 'Joʻnalish kelishigi', 'Bosh kelishik']),
       mc('«Daraxtning barglari sargʻaydi» gapida «daraxtning» qaysi kelishikda?', 'Qaratqich kelishigi', ['Tushum kelishigi', 'Bosh kelishik', 'Chiqish kelishigi']),
       mc('«Ali shaharga ketdi» gapida «shaharga» qaysi kelishikda?', 'Joʻnalish kelishigi', ['Oʻrin-payt kelishigi', 'Chiqish kelishigi', 'Tushum kelishigi']),
       mc('«Qushlar uchib ketdi» gapida «qushlar» qaysi kelishikda?', 'Bosh kelishik', ['Tushum kelishigi', 'Qaratqich kelishigi', 'Joʻnalish kelishigi']),
       mc('«kitob» soʻziga joʻnalish kelishigi qoʻshilsa qanday boʻladi?', 'kitobga', ['kitobka', 'kitobda', 'kitobni']),
       mc('«qishloq» soʻziga joʻnalish kelishigi qoʻshilsa qanday boʻladi?', 'qishloqqa', ['qishloqga', 'qishloqka', 'qishloqda']),
       mc('«tilak» soʻziga joʻnalish kelishigi qoʻshilsa qanday boʻladi?', 'tilakka', ['tilakga', 'tilakqa', 'tilakda'])]
B.topic(F2, 'kelishik', 'Kelishiklar', [5, 6], kl_g1, kl_g2, kl3, 'morfologiya ot kelishik qoʻshimcha')

# ---- egalik ----
EG = [('I shaxs birlik', 'im', 'm'), ('II shaxs birlik', 'ing', 'ng'), ('III shaxs', 'i', 'si'), ('I shaxs koʻplik', 'imiz', 'miz'), ('II shaxs koʻplik', 'ingiz', 'ngiz')]
EGN = [e[0] for e in EG]
EWC = ['kitob', 'daftar', 'qalam', 'doʻst', 'uy', 'bogʻ', 'sinf']; EWV = ['ona', 'ota', 'bola', 'xona', 'opa', 'aka', 'uka']
def eg_g1():
    e = ch(EG); w = ch(EWC)
    return mc(f'«{w}{e[1]}» soʻzidagi egalik qoʻshimchasi qaysi shaxsni bildiradi?', e[0], R.sample([x for x in EGN if x != e[0]], 3))
def eg_g2():
    e = ch(EG); w = ch(EWV)
    return mc(f'«{w}{e[2]}» soʻzidagi egalik qoʻshimchasi qaysi shaxsni bildiradi?', e[0], R.sample([x for x in EGN if x != e[0]], 3))
def eg_g3():
    e = ch(EG); t = R.randrange(2)
    if t == 0:
        w = ch(EWC); return mc(f'«{w}» soʻziga {e[0]} egalik qoʻshimchasini qoʻshing.', w + e[1], R.sample([w + x[1] for x in EG if x != e], 3))
    w = ch(EWV); return mc(f'«{w}» soʻziga {e[0]} egalik qoʻshimchasini qoʻshing.', w + e[2], R.sample([w + x[2] for x in EG if x != e], 3))
B.topic(F2, 'egalik', 'Egalik qoʻshimchalari', [6], eg_g1, eg_g2, eg_g3, 'morfologiya ot egalik shaxs')

# ---- sifat ----
DAR = {'Oddiy daraja': ['qizil', 'oq', 'katta', 'shirin', 'baland', 'issiq', 'yashil', 'keng'],
       'Qiyosiy daraja': ['qizilroq', 'oqroq', 'kattaroq', 'shirinroq', 'balandroq', 'issiqroq', 'kengroq', 'yaxshiroq'],
       'Orttirma daraja': ['eng katta', 'juda shirin', 'qip-qizil', 'oppoq', 'eng baland', 'gʻoyat issiq', 'yam-yashil', 'juda keng'],
       'Ozaytirma daraja': ['oqish', 'qizgʻish', 'koʻkish', 'sargʻish', 'koʻkimtir', 'qoramtir', 'koʻkimtil', 'shirintob']}
DAR['Ozaytirma daraja'] = [x for x in DAR['Ozaytirma daraja'] if x not in ('koʻkimtil', 'shirintob')]
DL = list(DAR)
SY = [('aqlli', 'aql', '-li'), ('aqlsiz', 'aql', '-siz'), ('ishchan', 'ish', '-chan'), ('kuchli', 'kuch', '-li'), ('tuzsiz', 'tuz', '-siz'), ('mevali', 'meva', '-li'), ('uyatchan', 'uyat', '-chan')]
def sf_g1():
    t = R.randrange(2)
    if t == 0: return mc('Qaysi soʻz sifat?', ch(TURKUM['Sifat']), R.sample(TURKUM['Ot'] + TURKUM['Feʼl'], 3))
    return mc('Sifat nimani bildiradi?', 'Predmetning belgisini', ['Predmetning nomini', 'Harakatni', 'Miqdorni'])
sf_g2 = cls('«{w}» sifati qaysi darajada?', DAR, DL)
def sf_g3():
    t = R.randrange(3)
    if t == 0: w, r, q = ch(SY); return mc(f'«{w}» sifati qaysi qoʻshimcha bilan yasalgan?', q, R.sample([x for x in ['-li', '-siz', '-chan', '-lar', '-lik', '-dor'] if x != q], 3))
    if t == 1: return mc('Qiyosiy daraja qaysi qoʻshimcha bilan yasaladi?', '-roq', ['-lar', '-li', '-ish'])
    return mc('Qaysi soʻz ozaytirma darajada?', ch(DAR['Ozaytirma daraja']), R.sample(DAR['Qiyosiy daraja'] + DAR['Orttirma daraja'], 3))
B.topic(F2, 'sifat', 'Sifat va sifat darajalari', [6], sf_g1, sf_g2, sf_g3, 'morfologiya sifat daraja')

# ---- son ----
SON = {'Sanoq son': ['uch', 'yigirma', 'besh', 'yuz', 'ming', 'oʻn ikki'], 'Tartib son': ['uchinchi', 'yigirmanchi', 'beshinchi', 'birinchi', 'oʻninchi', 'yuzinchi'],
       'Dona son': ['uchta', 'beshta', 'oʻnta', 'ikkita', 'yettita', 'yuzta'], 'Chama son': ['uchtacha', 'oʻnlab', 'yuzlab', 'beshtacha', 'minglab', 'yigirmatacha'],
       'Jamlovchi son': ['uchala', 'ikkovi', 'beshovlon', 'toʻrtala', 'uchovi', 'ikkala'], 'Taqsim son': ['uchtadan', 'ikkitadan', 'beshtadan', 'oʻntadan', 'bittadan', 'yuztadan']}
SNL = list(SON)
def sn_g1():
    lab = ch(['Sanoq son', 'Tartib son', 'Dona son']); w = ch(SON[lab])
    return mc(f'«{w}» qanday son?', lab, R.sample([x for x in SNL if x != lab], 3))
sn_g2 = cls('«{w}» qanday son?', SON, SNL)
def sn_g3():
    t = R.randrange(3)
    if t == 0: return mc('Tartib son qaysi qoʻshimcha bilan yasaladi?', '-(i)nchi', ['-ta', '-tadan', '-lab'])
    if t == 1: return mc('Taqsim son qaysi qoʻshimcha bilan yasaladi?', '-tadan', ['-inchi', '-ta', '-ala'])
    lab = ch(SNL); return mc(f'Qaysi soʻz — {lab.lower()}?', ch(SON[lab]), R.sample([x for k, v in SON.items() if k != lab for x in v], 3))
B.topic(F2, 'son', 'Son va uning turlari', [6], sn_g1, sn_g2, sn_g3, 'morfologiya son sanoq tartib')

# ---- olmosh ----
OLM = {'Kishilik olmoshi': ['men', 'sen', 'u', 'biz', 'siz', 'ular'], 'Koʻrsatish olmoshi': ['bu', 'shu', 'oʻsha', 'ana', 'mana', 'ushbu'],
       'Soʻroq olmoshi': ['kim', 'nima', 'qayer', 'qaysi', 'qanday', 'qancha'], 'Belgilash olmoshi': ['hamma', 'barcha', 'har', 'butun', 'jami', 'hamisha']}
OLM['Belgilash olmoshi'] = OLM['Belgilash olmoshi'][:5]
OLM['Oʻzlik olmoshi'] = ['oʻzim', 'oʻzing', 'oʻzi', 'oʻzimiz']; OLM['Gumon olmoshi'] = ['allakim', 'kimdir', 'nimadir', 'allanima', 'qayerdadir']
OLM['Boʻlishsizlik olmoshi'] = ['hech kim', 'hech narsa', 'hech qayer', 'hech qaysi']
OL = list(OLM)
def ol_g1():
    lab = ch(['Kishilik olmoshi', 'Koʻrsatish olmoshi', 'Soʻroq olmoshi']); w = ch(OLM[lab])
    return mc(f'«{w}» qanday olmosh?', lab, R.sample([x for x in OL if x != lab], 3))
ol_g2 = cls('«{w}» qanday olmosh?', OLM, OL)
ol3 = [mc('Olmosh nima oʻrnida qoʻllanadi?', 'Ot, sifat, son oʻrnida', ['Faqat feʼl oʻrnida', 'Koʻmakchi oʻrnida', 'Undov oʻrnida']),
       mc('Kishilik olmoshlari nechta?', '6', ['3', '5', '8']), mc('«Biz» qaysi shaxsni bildiradi?', 'I shaxs koʻplik', ['II shaxs koʻplik', 'III shaxs koʻplik', 'I shaxs birlik']),
       mc('«Ular» qaysi shaxsni bildiradi?', 'III shaxs koʻplik', ['I shaxs koʻplik', 'II shaxs koʻplik', 'III shaxs birlik']),
       mc('«Sen» qaysi shaxsni bildiradi?', 'II shaxs birlik', ['I shaxs birlik', 'III shaxs birlik', 'II shaxs koʻplik']),
       mc('«Siz» olmoshi qachon birlik maʼnosida ishlatiladi?', 'Hurmat bilan murojaatda', ['Hech qachon', 'Koʻplikda', 'Faqat savolda']),
       mc('«U kecha keldi» gapida «u» qanday olmosh?', 'Kishilik olmoshi', ['Koʻrsatish olmoshi', 'Soʻroq olmoshi', 'Belgilash olmoshi']),
       mc('«U kitobni ber» gapida «u» qanday olmosh?', 'Koʻrsatish olmoshi', ['Kishilik olmoshi', 'Soʻroq olmoshi', 'Gumon olmoshi']),
       mc('Qaysi soʻz gumon olmoshi?', 'kimdir', ['kim', 'hech kim', 'hamma']), mc('Qaysi soʻz boʻlishsizlik olmoshi?', 'hech kim', ['kimdir', 'hamma', 'kim']),
       mc('Qaysi soʻz soʻroq olmoshi?', 'qayer', ['shu', 'hamma', 'oʻzim'])]
B.topic(F2, 'olmosh', 'Olmosh va uning turlari', [6], ol_g1, ol_g2, ol3, 'morfologiya olmosh')

# ---- feʼl: zamon ----
ZAM = {'Oʻtgan zamon': ['keldi', 'oʻqidi', 'yozdi', 'bordi', 'kuldi', 'ishladi', 'koʻrdi', 'uxladi'],
       'Hozirgi zamon': ['kelyapti', 'oʻqiyapti', 'yozyapti', 'boryapti', 'kulyapti', 'ishlamoqda', 'oʻqimoqda', 'yozmoqda'],
       'Kelasi zamon': ['bormoqchi', 'kelmoqchi', 'oʻqimoqchi', 'yozmoqchi', 'kelar', 'borar', 'oʻqir', 'yozar']}
ZL = list(ZAM) + ['Zamonsiz']
def fz_g1():
    t = R.randrange(2)
    if t == 0: return mc('Qaysi soʻz feʼl?', ch(TURKUM['Feʼl']), R.sample(TURKUM['Ot'] + TURKUM['Sifat'], 3))
    return mc('Feʼl nimani bildiradi?', 'Harakat va holatni', ['Predmet nomini', 'Belgini', 'Miqdorni'])
def fz_g2():
    lab = ch(list(ZAM)); w = ch(ZAM[lab]); return mc(f'«{w}» feʼli qaysi zamonda?', lab, [x for x in ZL if x != lab])
fz3 = [mc('Oʻtgan zamon feʼli qaysi qoʻshimcha bilan yasaladi?', '-di', ['-yap', '-moqchi', '-ar']), mc('Hozirgi zamon davom feʼli qaysi qoʻshimcha bilan yasaladi?', '-yap', ['-di', '-moqchi', '-gan']),
       mc('«Men ertaga kinoga bormoqchiman» gapidagi feʼl qaysi zamonda?', 'Kelasi zamon', ['Oʻtgan zamon', 'Hozirgi zamon', 'Zamonsiz']),
       mc('«Ukam hozir dars tayyorlayapti» gapidagi feʼl qaysi zamonda?', 'Hozirgi zamon', ['Oʻtgan zamon', 'Kelasi zamon', 'Zamonsiz']),
       mc('«Biz kecha muzeyga bordik» gapidagi feʼl qaysi zamonda?', 'Oʻtgan zamon', ['Hozirgi zamon', 'Kelasi zamon', 'Zamonsiz']),
       mc('Buyruq-istak maylidagi feʼl qaysi?', 'oʻqi', ['oʻqidi', 'oʻqiyapti', 'oʻqigan']), mc('Boʻlishsiz feʼl qaysi?', 'kelmadi', ['keldi', 'kelyapti', 'kelsa']),
       mc('Feʼlning boʻlishsiz shakli qaysi qoʻshimcha bilan yasaladi?', '-ma', ['-di', '-ni', '-lar']), mc('Shart maylidagi feʼl qaysi?', 'kelsa', ['keldi', 'kelmadi', 'kelyapti']),
       mc('Feʼl qanday soʻroqlarga javob beradi?', 'nima qildi? nima qilyapti?', ['kim? nima?', 'qanday?', 'nechta?'])]
B.topic(F2, 'fel', 'Feʼl va uning zamonlari', [6], fz_g1, fz_g2, fz3, 'morfologiya feʼl zamon')

# ---- ravish ----
RAV = {'Payt ravishi': ['ertalab', 'kechqurun', 'hozir', 'doim', 'hamisha', 'endi'], 'Holat ravishi': ['sekin', 'yayov', 'tez-tez', 'asta-sekin', 'zoʻrgʻa', 'birdan'],
       'Oʻrin ravishi': ['ichkari', 'tashqari', 'olgʻa', 'nari', 'beri'], 'Miqdor-daraja ravishi': ['koʻp', 'oz', 'sal', 'biroz', 'juda', 'gʻoyat']}
RL = list(RAV)
def rv_g1():
    t = R.randrange(2)
    if t == 0: return mc('Qaysi soʻz ravish?', ch(TURKUM['Ravish']), R.sample(TURKUM['Ot'] + TURKUM['Sifat'][:8], 3))
    return mc('Ravish nimani bildiradi?', 'Harakatning belgisini', ['Predmetning nomini', 'Predmetning belgisini', 'Predmet sonini'])
rv_g2 = cls('«{w}» qanday ravish?', RAV, RL)
rv3 = [mc('Ravish qanday soʻroqlarga javob beradi?', 'qachon? qanday? qayerga? qancha?', ['kim? nima?', 'nima qildi?', 'nechanchi?']),
       mc('«U ertalab yugurdi» gapida «ertalab» qanday ravish?', 'Payt ravishi', ['Holat ravishi', 'Oʻrin ravishi', 'Miqdor-daraja ravishi']),
       mc('«Bobom yayov keldi» gapida «yayov» qanday ravish?', 'Holat ravishi', ['Payt ravishi', 'Oʻrin ravishi', 'Miqdor-daraja ravishi']),
       mc('«Bolalar ichkari kirdi» gapida «ichkari» qanday ravish?', 'Oʻrin ravishi', ['Payt ravishi', 'Holat ravishi', 'Miqdor-daraja ravishi']),
       mc('«Men biroz charchadim» gapida «biroz» qanday ravish?', 'Miqdor-daraja ravishi', ['Payt ravishi', 'Holat ravishi', 'Oʻrin ravishi']),
       mc('Ravish gapda koʻpincha qaysi soʻz turkumiga bogʻlanadi?', 'Feʼlga', ['Otga', 'Olmoshga', 'Songa']),
       mc('«Ali tez-tez kutubxonaga boradi» gapidagi ravish qaysi?', 'tez-tez', ['Ali', 'kutubxonaga', 'boradi']),
       mc('«Biz hamisha tinchlik tarafdorimiz» gapidagi ravish qaysi?', 'hamisha', ['biz', 'tinchlik', 'tarafdorimiz']),
       mc('Qaysi soʻz payt ravishi?', 'kechqurun', ['sekin', 'ichkari', 'biroz']), mc('Qaysi soʻz holat ravishi?', 'asta-sekin', ['ertalab', 'tashqari', 'juda']),
       mc('Qaysi soʻz oʻrin ravishi?', 'olgʻa', ['hozir', 'yayov', 'oz'])]
B.topic(F2, 'ravish', 'Ravish va uning turlari', [6], rv_g1, rv_g2, rv3, 'morfologiya ravish')

# ---- feʼl nisbatlari ----
NIS = {'Aniq nisbat': ['yozdi', 'oʻqidi', 'yuvdi', 'kiydi', 'kuldi', 'qurdi'], 'Oʻzlik nisbati': ['yuvindi', 'kiyindi', 'tarandi', 'bezandi', 'yasandi'],
       'Birgalik nisbati': ['yozishdi', 'kulishdi', 'oʻynashdi', 'gaplashdi', 'koʻrishdi', 'quchoqlashdi'],
       'Orttirma nisbat': ['yozdirdi', 'oʻqitdi', 'kuldirdi', 'yugurtirdi', 'ichirdi', 'yuvdirdi'], 'Majhul nisbat': ['yozildi', 'oʻqildi', 'qurildi', 'ekildi', 'yuvildi', 'tikildi']}
NL = list(NIS)
def ns_g1():
    lab = ch(['Aniq nisbat', 'Birgalik nisbati', 'Majhul nisbat']); w = ch(NIS[lab])
    return mc(f'«{w}» feʼli qaysi nisbatda?', lab, R.sample([x for x in NL if x != lab], 3))
ns_g2 = cls('«{w}» feʼli qaysi nisbatda?', NIS, NL)
ns3 = [mc('Majhul nisbat qaysi qoʻshimchalar bilan yasaladi?', '-il, -in', ['-ish, -sh', '-dir, -tir', '-lar, -ni']),
       mc('Birgalik nisbati qaysi qoʻshimcha bilan yasaladi?', '-ish, -sh', ['-il, -in', '-dir, -t', '-gan']),
       mc('Orttirma nisbat qaysi qoʻshimchalar bilan yasaladi?', '-dir, -tir, -t, -giz', ['-il, -in', '-ish, -sh', '-lar']),
       mc('«Uy quruvchilar tomonidan qurildi» gapidagi feʼl qaysi nisbatda?', 'Majhul nisbat', ['Aniq nisbat', 'Orttirma nisbat', 'Oʻzlik nisbati']),
       mc('«Ona qiziga xat yozdirdi» gapidagi feʼl qaysi nisbatda?', 'Orttirma nisbat', ['Aniq nisbat', 'Majhul nisbat', 'Birgalik nisbati']),
       mc('«Doʻstlar uzoq gaplashdi» gapidagi feʼl qaysi nisbatda?', 'Birgalik nisbati', ['Aniq nisbat', 'Oʻzlik nisbati', 'Majhul nisbat']),
       mc('«Bola tez kiyindi» gapidagi feʼl qaysi nisbatda?', 'Oʻzlik nisbati', ['Aniq nisbat', 'Majhul nisbat', 'Birgalik nisbati']),
       mc('«oʻqi» feʼlining orttirma nisbati qaysi?', 'oʻqit', ['oʻqil', 'oʻqish', 'oʻqin']), mc('«yoz» feʼlining majhul nisbati qaysi?', 'yozil', ['yozdir', 'yozish', 'yozin']),
       mc('«kul» feʼlining birgalik nisbati qaysi?', 'kulish', ['kuldir', 'kulin', 'kulil']), mc('Oʻzbek tilida feʼlning nechta nisbati bor?', '5', ['3', '4', '6'])]
B.topic(F2, 'nisbat', 'Feʼl nisbatlari', [7], ns_g1, ns_g2, ns3, 'morfologiya feʼl nisbat')

# ---- vazifa shakllari ----
VS = {'Sifatdosh': ['oʻqigan', 'oʻqiyotgan', 'oʻqiydigan', 'yozgan', 'kelgan', 'kulayotgan', 'oqar', 'yonar'],
      'Ravishdosh': ['oʻqib', 'yozib', 'kelgach', 'kulib', 'oʻqiguncha', 'yugurib', 'koʻrgach', 'kula-kula'],
      'Harakat nomi': ['oʻqish', 'yozish', 'kelish', 'yugurish', 'suzish', 'ishlash', 'oʻqimoq', 'yozuv']}
VL = list(VS) + ['Shart mayli']
vs_g1 = cls('«{w}» feʼlning qaysi shakli?', VS, VL)
def vs_g2():
    lab = ch(list(VS)); s = {'Sifatdosh': [('Kitob oʻqigan bola', 'oʻqigan'), ('Oqar suv', 'oqar'), ('Kulayotgan qiz', 'kulayotgan'), ('Yonar chiroq', 'yonar')],
                            'Ravishdosh': [('U kulib gapirdi', 'kulib'), ('Darsni tugatgach, uyga ketdik', 'tugatgach'), ('Yugurib keldi', 'yugurib'), ('Kitobni oʻqib chiqdim', 'oʻqib')],
                            'Harakat nomi': [('Kitob oʻqish foydali', 'oʻqish'), ('Suzish sogʻliq uchun foydali', 'suzish'), ('Daraxt ekish savob ish', 'ekish'), ('Yugurish menga yoqadi', 'yugurish')]}[lab]
    g, w = ch(s); return mc(f'«{g}» birikmasida «{w}» feʼlning qaysi shakli?', lab, [x for x in VL if x != lab])
vs3 = [mc('Sifatdosh qanday soʻroqlarga javob beradi?', 'qanday? qanaqa?', ['qanday qilib? qachon?', 'nima qilish?', 'kim? nima?']),
       mc('Ravishdosh nimani bildiradi?', 'Harakatning belgisini (qanday qilib, qachon)', ['Predmetning belgisini', 'Harakat nomini', 'Predmet nomini']),
       mc('Harakat nomi qanday soʻroqqa javob beradi?', 'nima qilish?', ['qanday?', 'qanday qilib?', 'kim?']),
       mc('Qaysi qoʻshimcha sifatdosh yasaydi?', '-gan', ['-ib', '-ish', '-gach']), mc('Qaysi qoʻshimcha ravishdosh yasaydi?', '-ib', ['-gan', '-ish', '-moq']),
       mc('Qaysi qoʻshimcha harakat nomi yasaydi?', '-ish', ['-gan', '-ib', '-gach']), mc('Qaysi soʻz sifatdosh?', 'yozilgan', ['yozib', 'yozish', 'yozdi']),
       mc('Qaysi soʻz ravishdosh?', 'kelgach', ['kelgan', 'kelish', 'keldi']), mc('Qaysi soʻz harakat nomi?', 'ishlash', ['ishlagan', 'ishlab', 'ishladi']),
       mc('Sifatdosh gapda koʻpincha qaysi vazifada keladi?', 'Aniqlovchi', ['Ega', 'Kesim', 'Undalma'])]
B.topic(F2, 'vazifa', 'Sifatdosh, ravishdosh va harakat nomi', [7], vs_g1, vs_g2, vs3, 'morfologiya feʼl sifatdosh ravishdosh harakat nomi')

# ---- yordamchi soʻzlar ----
YRD = {'Koʻmakchi': ['bilan', 'uchun', 'kabi', 'singari', 'sari', 'tomon', 'haqida', 'orqali'], 'Bogʻlovchi': ['va', 'lekin', 'ammo', 'biroq', 'yoki', 'chunki', 'agar', 'hamda'],
       'Yuklama': ['faqat', 'hatto', 'axir', '-mi', '-ku', '-chi', '-oq', 'xuddi'], 'Undov': ['oh', 'voy', 'ura', 'eh', 'ofarin', 'barakalla', 'obbo', 'uh']}
YL = list(YRD)
def yr_g1():
    lab = ch(['Koʻmakchi', 'Bogʻlovchi']); w = ch(YRD[lab]); return mc(f'«{w}» qanday soʻz?', lab, [x for x in YL if x != lab])
yr_g2 = cls('«{w}» qanday soʻz?', YRD, YL)
yr3 = [mc('«Men akam bilan keldim» gapidagi koʻmakchi qaysi?', 'bilan', ['men', 'akam', 'keldim']), mc('«Kitob va daftar oldim» gapidagi bogʻlovchi qaysi?', 'va', ['kitob', 'daftar', 'oldim']),
       mc('«Hatto bobom ham keldi» gapidagi yuklama qaysi?', 'hatto', ['bobom', 'ham', 'keldi']) if False else mc('«Faqat sen yordam berding» gapidagi yuklama qaysi?', 'faqat', ['sen', 'yordam', 'berding']),
       mc('«Ura, biz yutdik!» gapidagi undov qaysi?', 'ura', ['biz', 'yutdik', 'gapda undov yoʻq']),
       mc('«Men bordim, lekin u kelmadi» gapidagi bogʻlovchi qaysi?', 'lekin', ['men', 'bordim', 'kelmadi']), mc('«Vatan uchun xizmat qilamiz» gapidagi koʻmakchi qaysi?', 'uchun', ['Vatan', 'xizmat', 'qilamiz']),
       mc('Yordamchi soʻzlar gap boʻlagi boʻla oladimi?', 'Yoʻq', ['Ha, doim', 'Faqat ega boʻladi', 'Faqat kesim boʻladi']),
       mc('Qaysi turkum his-hayajonni bildiradi?', 'Undov', ['Koʻmakchi', 'Bogʻlovchi', 'Yuklama']),
       mc('Qaysi turkum gap boʻlaklarini va gaplarni bogʻlaydi?', 'Bogʻlovchi', ['Koʻmakchi', 'Yuklama', 'Undov']),
       mc('«Kelasanmi?» soʻzidagi «-mi» qanday soʻz?', 'Soʻroq yuklamasi', ['Bogʻlovchi', 'Koʻmakchi', 'Egalik qoʻshimchasi'])]
B.topic(F2, 'yordamchi', 'Yordamchi soʻzlar va undov', [7], yr_g1, yr_g2, yr3, 'morfologiya koʻmakchi bogʻlovchi yuklama undov')

# ======================= SINTAKSIS =======================
GT = {'Darak gap': ['Men maktabga boraman.', 'Bugun havo issiq.', 'Ukam kitob oʻqiyapti.', 'Toshkent — Oʻzbekiston poytaxti.', 'Bahorda daraxtlar gullaydi.', 'Biz sport bilan shugʻullanamiz.'],
      'Soʻroq gap': ['Sen qachon kelasan?', 'Bu kitob kimniki?', 'Darsga tayyorlandingmi?', 'Qayerda yashaysiz?', 'Nega kechikding?', 'Ertaga havo qanday boʻladi?'],
      'Buyruq gap': ['Darsni yaxshi tayyorla.', 'Eshikni yoping.', 'Kitobni menga ber.', 'Ota-onangizni hurmat qiling.', 'Kech qolmang.', 'Daraxtlarni asrang.'],
      'Undov gap': ['Qanday goʻzal kun!', 'Voy, qanday chiroyli!', 'Ura, biz yutdik!', 'Ofarin, barakalla!', 'Naqadar keng dala!', 'Eh, qanday ajoyib!']}
GTL = list(GT)
def gt_g1():
    lab = ch(['Darak gap', 'Soʻroq gap']); s = ch(GT[lab]); return mc(f'«{s}» — qanday gap?', lab, [x for x in GTL if x != lab])
gt_g2 = cls('«{w}» — qanday gap?', GT, GTL)
gt3 = [mc('Darak gap oxirida qanday tinish belgisi qoʻyiladi?', 'Nuqta', ['Soʻroq belgisi', 'Undov belgisi', 'Vergul']),
       mc('Soʻroq gap oxirida qanday tinish belgisi qoʻyiladi?', 'Soʻroq belgisi', ['Nuqta', 'Undov belgisi', 'Ikki nuqta']),
       mc('Kuchli hayajon bilan aytilgan gap oxirida qanday belgi qoʻyiladi?', 'Undov belgisi', ['Nuqta', 'Soʻroq belgisi', 'Vergul']),
       mc('Buyruq gap nimani bildiradi?', 'Buyruq, iltimos, maslahatni', ['Xabarni', 'Soʻroqni', 'Hayratni']),
       mc('Darak gap nimani bildiradi?', 'Biror voqea haqida xabarni', ['Soʻroqni', 'Buyruqni', 'Kuchli hayajonni']),
       mc('Qaysi gap soʻroq gap?', 'Kim keldi?', ['Kim kelsa, kelsin.', 'Kel!', 'Ali keldi.']),
       mc('Qaysi gap buyruq gap?', 'Oynani och.', ['Oyna ochiq.', 'Oyna ochiqmi?', 'Qanday katta oyna!']),
       mc('Qaysi gap darak gap?', 'Qor yogʻdi.', ['Qor yogʻdimi?', 'Qanday qor!', 'Qorni kurang.']), mc('Qaysi gap undov gap?', 'Qanday chiroyli bogʻ!', ['Bogʻ chiroyli.', 'Bogʻ chiroylimi?', 'Bogʻni toza tuting.']),
       mc('Soʻroq gapda koʻpincha nima ishtirok etadi?', 'Soʻroq olmoshi yoki -mi yuklamasi', ['Undov soʻz', 'Buyruq shakli', 'Kirish soʻz'])]
B.topic(F3, 'gapturi', 'Gap turlari: darak, soʻroq, buyruq, undov', [5, 8], gt_g1, gt_g2, gt3, 'sintaksis gap darak soʻroq buyruq undov')

BOL = [('Qushlar osmonda uchmoqda.', 'qushlar', 'Ega'), ('Qushlar osmonda uchmoqda.', 'uchmoqda', 'Kesim'), ('Onam mazali osh pishirdi.', 'mazali', 'Aniqlovchi'),
       ('Onam mazali osh pishirdi.', 'onam', 'Ega'), ('Onam mazali osh pishirdi.', 'pishirdi', 'Kesim'), ('Ukam kitobni diqqat bilan oʻqidi.', 'kitobni', 'Toʻldiruvchi'),
       ('Biz ertalab sport bilan shugʻullanamiz.', 'ertalab', 'Hol'), ('Oq bulutlar sekin suzardi.', 'oq', 'Aniqlovchi'), ('Oq bulutlar sekin suzardi.', 'sekin', 'Hol'),
       ('Oq bulutlar sekin suzardi.', 'bulutlar', 'Ega'), ('Talabalar imtihonni muvaffaqiyatli topshirdi.', 'imtihonni', 'Toʻldiruvchi'),
       ('Kichkina qiz qoʻshiq kuyladi.', 'kichkina', 'Aniqlovchi'), ('Kichkina qiz qoʻshiq kuyladi.', 'qiz', 'Ega'), ('Kichkina qiz qoʻshiq kuyladi.', 'kuyladi', 'Kesim'),
       ('Dadam bugun ishdan erta qaytdi.', 'erta', 'Hol'), ('Dadam bugun ishdan erta qaytdi.', 'dadam', 'Ega'), ('Oʻqituvchi yangi mavzuni tushuntirdi.', 'yangi', 'Aniqlovchi'),
       ('Oʻqituvchi yangi mavzuni tushuntirdi.', 'mavzuni', 'Toʻldiruvchi'), ('Oʻqituvchi yangi mavzuni tushuntirdi.', 'oʻqituvchi', 'Ega'), ('Shamol qattiq esdi.', 'qattiq', 'Hol'),
       ('Shamol qattiq esdi.', 'shamol', 'Ega'), ('Bahorda daraxtlar gullaydi.', 'bahorda', 'Hol'), ('Bahorda daraxtlar gullaydi.', 'daraxtlar', 'Ega'),
       ('Ali doʻstining kitobini oldi.', 'kitobini', 'Toʻldiruvchi'), ('Bu kitob juda qiziqarli.', 'qiziqarli', 'Kesim'), ('Mening akam shifokor.', 'shifokor', 'Kesim'),
       ('Mening akam shifokor.', 'mening', 'Aniqlovchi'), ('Ular kechqurun uyga qaytishdi.', 'kechqurun', 'Hol')]
BL = ['Ega', 'Kesim', 'Toʻldiruvchi', 'Aniqlovchi', 'Hol']
def bl_g1():
    s, w, lab = ch([x for x in BOL if x[2] in ('Ega', 'Kesim')]); return mc(f'«{s}» gapida «{w}» qaysi gap boʻlagi?', lab, [x for x in BL if x != lab][:3] if lab == 'Ega' else R.sample([x for x in BL if x != lab], 3))
def bl_g2():
    s, w, lab = ch(BOL); return mc(f'«{s}» gapida «{w}» qaysi gap boʻlagi?', lab, R.sample([x for x in BL if x != lab], 3))
bl3 = [mc('Gapning bosh boʻlaklari qaysilar?', 'Ega va kesim', ['Toʻldiruvchi va hol', 'Aniqlovchi va hol', 'Ega va toʻldiruvchi']),
       mc('Ega qanday soʻroqlarga javob beradi?', 'kim? nima?', ['nima qildi?', 'qanday?', 'qachon?']), mc('Kesim nimani bildiradi?', 'Eganing harakati yoki belgisini', ['Predmet belgisini', 'Harakat oʻrnini', 'Harakat obyektini']),
       mc('Aniqlovchi qanday soʻroqlarga javob beradi?', 'qanday? qaysi? kimning?', ['kimni? nimani?', 'qachon? qayerda?', 'nima qildi?']),
       mc('Toʻldiruvchi qanday soʻroqlarga javob beradi?', 'kimni? nimani? kimga? nimaga?', ['qanday?', 'qachon?', 'kim? nima?']),
       mc('Hol qanday soʻroqlarga javob beradi?', 'qachon? qayerda? qanday qilib?', ['kim? nima?', 'kimni? nimani?', 'qaysi?']),
       mc('Ikkinchi darajali boʻlaklar nechta?', '3 (toʻldiruvchi, aniqlovchi, hol)', ['2', '4', '5']),
       mc('Qaysi gap boʻlagi koʻpincha ot bilan ifodalangan predmetga bogʻlanadi?', 'Aniqlovchi', ['Hol', 'Kesim', 'Toʻldiruvchi']),
       mc('Gapda harakat bajaruvchini bildiruvchi boʻlak qaysi?', 'Ega', ['Kesim', 'Hol', 'Aniqlovchi']), mc('Gapning markaziy (hokim) boʻlagi qaysi?', 'Kesim', ['Ega', 'Aniqlovchi', 'Hol'])]
def bl_g3():
    if R.random() < .5: return ch(bl3)
    s, w, lab = ch([x for x in BOL if x[2] in ('Toʻldiruvchi', 'Aniqlovchi', 'Hol') or x[0].startswith(('Bu kitob', 'Mening'))])
    return mc(f'«{s}» gapida «{w}» qaysi gap boʻlagi?', lab, R.sample([x for x in BL if x != lab], 3))
B.topic(F3, 'bolak', 'Gap boʻlaklari', [8], bl_g1, bl_g2, bl_g3, 'sintaksis ega kesim toʻldiruvchi aniqlovchi hol')

BIR = [('chiroyli', 'gul'), ('kitob', 'oʻqimoq'), ('maktab', 'hovlisi'), ('tez', 'yugurmoq'), ('oltin', 'uzuk'), ('daryo', 'boʻyi'), ('xat', 'yozmoq'),
       ('katta', 'uy'), ('sekin', 'yurmoq'), ('olma', 'daraxti'), ('qizil', 'olma'), ('baland', 'togʻ'), ('suv', 'ichmoq'), ('shirin', 'qovun')]
BHL = ['Hokim soʻz', 'Tobe soʻz', 'Ikkalasi teng', 'Bogʻlovchi']
def br_g1():
    a, b = ch(BIR); return mc(f'«{a} {b}» birikmasida hokim (asosiy) soʻz qaysi?', b, [a, 'ikkalasi ham', 'birikmada hokim soʻz yoʻq'])
def br_g2():
    a, b = ch(BIR); return mc(f'«{a} {b}» birikmasida tobe (ergash) soʻz qaysi?', a, [b, 'ikkalasi ham', 'birikmada tobe soʻz yoʻq'])
br3 = [mc('Soʻz birikmasi kamida nechta mustaqil soʻzdan tuziladi?', '2', ['1', '3', '4']), mc('Soʻz birikmasida savol qaysi soʻzdan beriladi?', 'Hokim soʻzdan tobe soʻzga', ['Tobe soʻzdan hokim soʻzga', 'Ixtiyoriy', 'Savol berilmaydi']),
       mc('Qaysi biri soʻz birikmasi?', 'yashil maysa', ['va', 'kitob va daftar', 'bordi-keldi']), mc('«Ona va bola» soʻz birikmasimi?', 'Yoʻq, teng bogʻlangan soʻzlar', ['Ha, otli birikma', 'Ha, feʼlli birikma', 'Ha, gap']),
       mc('«Kitob oʻqimoq» qanday birikma (hokim soʻzga koʻra)?', 'Feʼlli birikma', ['Otli birikma', 'Sifatli birikma', 'Gap']),
       mc('«Chiroyli gul» qanday birikma (hokim soʻzga koʻra)?', 'Otli birikma', ['Feʼlli birikma', 'Ravishli birikma', 'Gap']),
       mc('Qaysi biri gap, birikma emas?', 'Quyosh chiqdi.', ['issiq quyosh', 'quyosh nuri', 'quyoshga qaramoq']),
       mc('«maktab hovlisi» birikmasida hokim soʻz qaysi?', 'hovlisi', ['maktab', 'ikkalasi ham', 'hokim soʻz yoʻq']),
       mc('«tez yugurmoq» birikmasida tobe soʻz qanday soʻroqqa javob beradi?', 'qanday?', ['kim?', 'nimani?', 'qayerda?']),
       mc('«kitob oʻqimoq» birikmasida tobe soʻz qanday soʻroqqa javob beradi?', 'nimani? (nima?)', ['qanday?', 'qachon?', 'kimning?'])]
B.topic(F3, 'birikma', 'Soʻz birikmasi', [8], br_g1, br_g2, br3, 'sintaksis birikma hokim tobe')

UND = [('Doʻstim, bu yoqqa kel.', 'doʻstim'), ('Aziz oʻquvchilar, darsni boshlaymiz.', 'aziz oʻquvchilar'), ('Ona, men keldim!', 'ona'), ('Ali, kitobingni olib kel.', 'Ali'),
       ('Bolalar, tinch oʻtiring.', 'bolalar'), ('Sen, Vatan, bizning faxrimizsan.', 'Vatan'), ('Hurmatli mehmonlar, xush kelibsiz!', 'hurmatli mehmonlar'), ('Dilnoza, daftaringni ochgin.', 'Dilnoza'), ('Ukajon, ehtiyot boʻl!', 'ukajon'),
       ('Bobojon, sizga choy keltiraymi?', 'bobojon'), ('Qadrdon doʻstlarim, sizlarni tabriklayman!', 'qadrdon doʻstlarim'), ('Shamol, sekinroq es!', 'shamol')]
KIR = [('Albatta, u keladi.', 'albatta'), ('Afsuski, poyezd ketib qoldi.', 'afsuski'), ('Shubhasiz, sen gʻolib boʻlasan.', 'shubhasiz'), ('Menimcha, bu toʻgʻri.', 'menimcha'),
       ('Ehtimol, ertaga yomgʻir yogʻar.', 'ehtimol'), ('Baxtimizga, havo ochildi.', 'baxtimizga'), ('Xullas, ish tugadi.', 'xullas'), ('Darhaqiqat, bu ajoyib kitob.', 'darhaqiqat'), ('Aytishlaricha, u yaxshi rassom.', 'aytishlaricha'),
       ('Birinchidan, darsni tayyorlash kerak.', 'birinchidan'), ('Balki, u kech qolar.', 'balki'), ('Avvalo, salomlashish kerak.', 'avvalo')]
def uk_g1():
    s, w = ch(UND); words = [x.strip('.,!?') for x in s.split() if x.strip('.,!?').lower() not in w.lower().split()]
    return mc(f'«{s}» gapidagi undalma qaysi?', w, R.sample(words, min(3, len(words))) if len(words) >= 3 else words + ['undalma yoʻq'])
def uk_g2():
    s, w = ch(KIR); words = [x.strip('.,!?') for x in s.split() if x.strip('.,!?').lower() != w]
    return mc(f'«{s}» gapidagi kirish soʻz qaysi?', w, (R.sample(words, 3) if len(words) >= 3 else words + ['kirish soʻz yoʻq']))
uk3 = [mc('Undalma gap boʻlagi boʻladimi?', 'Yoʻq', ['Ha, ega boʻladi', 'Ha, toʻldiruvchi boʻladi', 'Ha, hol boʻladi']),
       mc('Kirish soʻz gap boʻlagi boʻladimi?', 'Yoʻq', ['Ha, hol boʻladi', 'Ha, kesim boʻladi', 'Ha, aniqlovchi boʻladi']),
       mc('Undalma gapda qanday tinish belgisi bilan ajratiladi?', 'Vergul (yoki undov belgisi)', ['Nuqta', 'Qavs', 'Qoʻshtirnoq']),
       mc('Undalma nimani bildiradi?', 'Nutq qaratilgan shaxs yoki narsani', ['Soʻzlovchining munosabatini', 'Harakatni', 'Belgini']),
       mc('Kirish soʻz nimani bildiradi?', 'Soʻzlovchining fikrga munosabatini', ['Nutq qaratilgan shaxsni', 'Harakat vaqtini', 'Harakat obyektini']),
       mc('Qaysi gapda undalma bor?', 'Opa, choy ichasizmi?', ['Opam choy ichdi.', 'Albatta, choy ichamiz.', 'Choy issiq.']),
       mc('Qaysi gapda kirish soʻz bor?', 'Shubhasiz, u rost aytdi.', ['U rost aytdi.', 'Ali, rost ayt.', 'Rost gap yaxshi.']),
       mc('«Menimcha» soʻzi qanday soʻz?', 'Kirish soʻz', ['Undalma', 'Ega', 'Kesim']),
       mc('Qaysi soʻz kirish soʻz boʻlib kela oladi?', 'afsuski', ['kitob', 'yugurdi', 'chiroyli'])]
B.topic(F3, 'undalma', 'Undalma va kirish soʻzlar', [8], uk_g1, uk_g2, uk3, 'sintaksis undalma kirish soʻz tinish belgisi')

QG = {'Bogʻlangan qoʻshma gap': ['Quyosh chiqdi va havo isidi.', 'Men chaqirdim, lekin u kelmadi.', 'Yomgʻir yogʻdi, ammo havo sovimadi.', 'Bahor keldi va daraxtlar gulladi.', 'Men kitob oʻqidim, ukam esa rasm chizdi.', 'Qoʻngʻiroq chalindi va darslar boshlandi.'],
      'Ergash gapli qoʻshma gap': ['Agar yomgʻir yogʻsa, biz uyda qolamiz.', 'U kelmadi, chunki kasal edi.', 'Kim mehnat qilsa, u murodiga yetadi.', 'Agar vaqting boʻlsa, menga qoʻngʻiroq qil.', 'Biz sayrga chiqmadik, chunki havo sovuq edi.', 'Qayerda mehnat boʻlsa, oʻsha yerda baraka boʻladi.'],
      'Bogʻlovchisiz qoʻshma gap': ['Qoʻngʻiroq chalindi, dars boshlandi.', 'Kun isidi, qorlar eriy boshladi.', 'Shamol esdi, daraxtlar tebrandi.', 'Quyosh botdi, havo salqinlashdi.', 'Eshik ochildi, mehmonlar kirdi.', 'Bahor keldi, qushlar qaytdi.'],
      'Sodda gap': ['Men kitob oʻqidim.', 'Bolalar hovlida oʻynashdi.', 'Bugun havo juda issiq.', 'Ali va Vali maktabga ketdi.', 'Kuzda barglar sargʻayadi.', 'Ukam rasm chizishni yaxshi koʻradi.']}
QL = list(QG)
def qg_g1():
    lab = ch(['Sodda gap', 'Bogʻlangan qoʻshma gap']); s = ch(QG[lab]); return mc(f'«{s}» — qanday gap?', lab, [x for x in QL if x != lab])
qg_g2 = cls('«{w}» — qanday gap?', QG, QL)
qg3 = [mc('Qoʻshma gap nechta sodda gapdan tuziladi?', 'Kamida ikkita', ['Faqat bitta', 'Faqat uchta', 'Kamida toʻrtta']),
       mc('Bogʻlangan qoʻshma gapda qanday bogʻlovchilar ishlatiladi?', 'va, lekin, ammo, biroq', ['chunki, agar', 'bilan, uchun', 'faqat, hatto']),
       mc('Ergash gapli qoʻshma gapda qanday bogʻlovchilar ishlatiladi?', 'chunki, agar, -ki', ['va, lekin, ammo', 'bilan, kabi', 'oh, voy']),
       mc('Bogʻlovchisiz qoʻshma gap qismlari qanday bogʻlanadi?', 'Ohang yordamida', ['Bogʻlovchi bilan', 'Koʻmakchi bilan', 'Yuklama bilan']),
       mc('Ergash gapli qoʻshma gapda qaysi qism mazmunan asosiy?', 'Bosh gap', ['Ergash gap', 'Ikkalasi teng', 'Kirish soʻz']),
       mc('Bogʻlangan qoʻshma gap qismlari qanday munosabatda?', 'Teng huquqli', ['Biri ikkinchisiga tobe', 'Biri undalma', 'Biri kirish soʻz']),
       mc('«Agar» bogʻlovchisi qanday maʼnoni bildiradi?', 'Shart', ['Sabab', 'Zidlik', 'Payt']), mc('«Chunki» bogʻlovchisi qanday maʼnoni bildiradi?', 'Sabab', ['Shart', 'Zidlik', 'Maqsad']),
       mc('«Lekin», «ammo» bogʻlovchilari qanday maʼnoni bildiradi?', 'Zidlik', ['Sabab', 'Shart', 'Payt']),
       mc('Qoʻshma gap qismlari orasiga koʻpincha qanday tinish belgisi qoʻyiladi?', 'Vergul', ['Nuqta', 'Soʻroq belgisi', 'Qoʻshtirnoq'])]
B.topic(F3, 'qoshma', 'Qoʻshma gap turlari', [9], qg_g1, qg_g2, qg3, 'sintaksis qoʻshma gap bogʻlangan ergash bogʻlovchisiz')

# ======================= ADABIYOT =======================
OGZ = {'Maqol': ['Bilagi zoʻr birni yiqar, bilimi zoʻr mingni yiqar.', 'Ona yurting — oltin beshiging.', 'Yaxshidan ot qoladi, yomondan dod qoladi.', 'Til — dilning kaliti.', 'Sabr tagi — sariq oltin.', 'Mehnatning tagi — rohat.'],
       'Topishmoq': ['Bir qoshiq suvda oʻynaydi. (Til)', 'Kechasi chiqadi, kunduzi yoʻqoladi. (Yulduz)', 'Oyogʻi yoʻq yuradi, qoʻli yoʻq chizadi. (Qalam)', 'Ichi toʻla oltin, tashi qizil chiroq. (Anor)'],
       'Ertak': ['«Zumrad va Qimmat»', '«Ur toʻqmoq»', '«Bolta va oʻgʻri»? '], 'Doston': ['«Alpomish»', '«Goʻroʻgʻli»', '«Rustamxon»'], 'Latifa': ['Nasriddin Afandi haqidagi qisqa kulgili hikoya']}
OGZ['Ertak'] = ['«Zumrad va Qimmat»', '«Ur toʻqmoq»', '«Tohir va Zuhra»? ']
OGZ['Ertak'] = ['«Zumrad va Qimmat»', '«Ur toʻqmoq»', '«Uch ogʻayni botirlar»']
MAQ = [('Bilagi zoʻr birni yiqar, bilimi zoʻr …', 'mingni yiqar'), ('Ona yurting — …', 'oltin beshiging'), ('Yaxshidan ot qoladi, yomondan …', 'dod qoladi'),
       ('Til — dilning …', 'kaliti'), ('Sabr tagi — …', 'sariq oltin'), ('Mehnatning tagi — …', 'rohat'), ('Bir yigitga yetmish hunar …', 'oz'),
       ('Olim boʻlsang, …', 'olam seniki'), ('Doʻst achitib gapirar, dushman …', 'kuldirib'), ('Ilm olish — ignada …', 'quduq qazish')]
og1 = [mc('Maqol nima?', 'Xalqning qisqa, hikmatli soʻzi', ['Uzun sheʼriy asar', 'Kulgili hikoya', 'Qahramonlik qoʻshigʻi']),
       mc('Topishmoqda nima boʻladi?', 'Narsa yashirin tasvirlanadi, uni topish kerak', ['Qahramonlik voqeasi', 'Kulgili voqea', 'Hikmatli xulosa']),
       mc('Nasriddin Afandi qaysi janr qahramoni?', 'Latifa', ['Doston', 'Maqol', 'Topishmoq']), mc('«Alpomish» qanday asar?', 'Xalq dostoni', ['Roman', 'Ertak', 'Gʻazal']),
       mc('Xalq ogʻzaki ijodi asarlarining muallifi kim?', 'Xalq (muallifi nomaʼlum)', ['Alisher Navoiy', 'Abdulla Qodiriy', 'Bobur']),
       mc('Qaysi biri xalq ogʻzaki ijodi janri?', 'Ertak', ['Roman', 'Gʻazal', 'Ruboiy']), mc('Dostonlarni xalq orasida kimlar kuylagan?', 'Baxshilar', ['Shoirlar', 'Rassomlar', 'Olimlar']),
       mc('«Zumrad va Qimmat» qanday asar?', 'Xalq ertagi', ['Doston', 'Roman', 'Maqol']), mc('«Goʻroʻgʻli» qanday asar?', 'Xalq dostoni', ['Roman', 'Hikoya', 'Gʻazal']),
       mc('Latifa qanday asar?', 'Qisqa kulgili hikoya', ['Uzun sheʼriy asar', 'Hikmatli soʻz', 'Qahramonlik qoʻshigʻi']), mc('Qaysi biri maqol?', 'Til — dilning kaliti.', ['Kecha yomgʻir yogʻdi.', 'Bugun dars bor.', 'Men kitob oʻqidim.'])]
def og_g2():
    a, b = ch(MAQ); return mc(f'Maqolni davom ettiring: «{a}»', b, R.sample([x[1] for x in MAQ if x[1] != b], 3))
OGT = [(m[0] + ' ' + m[1], 'Maqol') for m in MAQ[:6]] + [('«Alpomish»', 'Doston'), ('«Goʻroʻgʻli»', 'Doston'), ('«Zumrad va Qimmat»', 'Ertak'), ('«Ur toʻqmoq»', 'Ertak'),
       ('Nasriddin Afandi haqidagi qisqa kulgili hikoya', 'Latifa')]
def og_g3():
    t = R.randrange(3)
    if t == 0:
        s, lab = ch(OGT); s = s.replace(' … ', ' ').replace('…', '').strip('«»')
        return mc(f'«{s}» — qaysi janrga mansub?', lab, [x for x in ['Maqol', 'Doston', 'Ertak', 'Latifa', 'Topishmoq'] if x != lab])
    if t == 1: return mc('«Alpomish» dostonining asosiy gʻoyasi?', 'Vatanparvarlik va qahramonlik', ['Kulgi', 'Sayohat', 'Tabiat tasviri'])
    return og_g2()
B.topic(F4, 'ogzaki', 'Xalq ogʻzaki ijodi: maqol, topishmoq, doston', [5], og1, og_g2, og_g3, 'adabiyot folklor maqol topishmoq ertak doston latifa')

AS = [('«Oʻtkan kunlar»', 'Abdulla Qodiriy'), ('«Mehrobdan chayon»', 'Abdulla Qodiriy'), ('«Kecha va kunduz»', 'Choʻlpon'), ('«Boburnoma»', 'Zahiriddin Muhammad Bobur'),
      ('«Xamsa»', 'Alisher Navoiy'), ('«Mahbub ul-qulub»', 'Alisher Navoiy'), ('«Lison ut-tayr»', 'Alisher Navoiy'), ('«Shum bola»', 'Gʻafur Gʻulom'),
      ('«Sariq devni minib»', 'Xudoyberdi Toʻxtaboyev'), ('«Bolalik»', 'Oybek'), ('«Navoiy» romani', 'Oybek'), ('«Sarob»', 'Abdulla Qahhor'),
      ('«Oʻgʻri» hikoyasi', 'Abdulla Qahhor'), ('«Ikki eshik orasi»', 'Oʻtkir Hoshimov'), ('«Dunyoning ishlari»', 'Oʻtkir Hoshimov'), ('«Yulduzli tunlar»', 'Pirimqul Qodirov'),
      ('«Qutadgʻu bilig»', 'Yusuf Xos Hojib'), ('«Devonu lugʻotit turk»', 'Mahmud Koshgʻariy'), ('«Ufq»', 'Said Ahmad'), ('«Ulugʻbek xazinasi»', 'Odil Yoqubov')]
AUT = sorted({x[1] for x in AS})
def as_g():
    a, b = ch(AS)
    if R.random() < .6: return mc(f'{a} asarining muallifi kim?', b, R.sample([x for x in AUT if x != b], 3))
    return mc(f'{b} qalamiga mansub asar qaysi?', a, R.sample([x[0] for x in AS if x[1] != b], 3))
as1 = [mc('«Oʻtkan kunlar» romanining muallifi kim?', 'Abdulla Qodiriy', ['Choʻlpon', 'Oybek', 'Abdulla Qahhor']), mc('«Boburnoma» asarining muallifi kim?', 'Zahiriddin Muhammad Bobur', ['Alisher Navoiy', 'Abdulla Qodiriy', 'Mahmud Koshgʻariy']),
       mc('«Xamsa» asarining muallifi kim?', 'Alisher Navoiy', ['Bobur', 'Choʻlpon', 'Gʻafur Gʻulom']), mc('«Shum bola» qissasining muallifi kim?', 'Gʻafur Gʻulom', ['Oybek', 'Abdulla Qahhor', 'Oʻtkir Hoshimov']),
       mc('«Sariq devni minib» asarining muallifi kim?', 'Xudoyberdi Toʻxtaboyev', ['Gʻafur Gʻulom', 'Said Ahmad', 'Oybek']), mc('«Kecha va kunduz» romanining muallifi kim?', 'Choʻlpon', ['Abdulla Qodiriy', 'Oybek', 'Odil Yoqubov']),
       mc('«Bolalik» qissasining muallifi kim?', 'Oybek', ['Gʻafur Gʻulom', 'Abdulla Qahhor', 'Choʻlpon']), mc('«Ikki eshik orasi» romanining muallifi kim?', 'Oʻtkir Hoshimov', ['Said Ahmad', 'Pirimqul Qodirov', 'Oybek']),
       mc('«Mehrobdan chayon» romanining muallifi kim?', 'Abdulla Qodiriy', ['Choʻlpon', 'Oybek', 'Gʻafur Gʻulom']), mc('«Sarob» romanining muallifi kim?', 'Abdulla Qahhor', ['Abdulla Qodiriy', 'Oybek', 'Said Ahmad'])]
B.topic(F4, 'asar', 'Asar va uning muallifi', [6, 7, 8, 9], as1, as_g, as_g, 'adabiyot asar muallif yozuvchi shoir roman')

TUR = {'Epik tur': ['Roman', 'Qissa', 'Hikoya', 'Ertak', 'Masal'], 'Lirik tur': ['Gʻazal', 'Ruboiy', 'Tuyuq', 'Muxammas', 'Qasida'], 'Dramatik tur': ['Drama', 'Tragediya', 'Komediya']}
TRL = list(TUR) + ['Xalq ogʻzaki ijodi emas']
tr_g1 = lambda: (lambda lab: mc(f'«{ch(TUR[lab])}» qaysi adabiy turga kiradi?', lab, ['Epik tur', 'Lirik tur', 'Dramatik tur', 'Publitsistik tur']))(ch(list(TUR)))
tr2 = [mc('Adabiyot necha turga boʻlinadi?', '3 (epik, lirik, dramatik)', ['2', '4', '5']), mc('Qaysi biri adabiy tur emas, janr?', 'Roman', ['Epik', 'Lirik', 'Dramatik']),
       mc('Voqeani hikoya qilib beruvchi tur qaysi?', 'Epik tur', ['Lirik tur', 'Dramatik tur', 'Hech qaysi']), mc('His-tuygʻularni ifodalovchi tur qaysi?', 'Lirik tur', ['Epik tur', 'Dramatik tur', 'Hech qaysi']),
       mc('Sahnada koʻrsatish uchun yoziladigan tur qaysi?', 'Dramatik tur', ['Epik tur', 'Lirik tur', 'Hech qaysi']), mc('Eng katta hajmli epik janr qaysi?', 'Roman', ['Hikoya', 'Qissa', 'Masal']),
       mc('Hikoya, qissa va romandan eng kichik hajmlisi qaysi?', 'Hikoya', ['Qissa', 'Roman', 'Hammasi teng']), mc('Kulgili, hajviy dramatik asar qanday ataladi?', 'Komediya', ['Tragediya', 'Drama', 'Doston']),
       mc('Masalda nima boʻladi?', 'Hayvonlar orqali ibratli xulosa', ['Faqat tabiat tasviri', 'Sevgi kechinmalari', 'Tarixiy voqealar'])]
tr3 = [mc('Ruboiy necha misradan iborat?', '4', ['2', '6', '5']), mc('Bayt necha misradan iborat?', '2', ['1', '3', '4']),
       mc('Gʻazalning birinchi bayti nima deyiladi?', 'Matlaʼ', ['Maqtaʼ', 'Radif', 'Qofiya']), mc('Gʻazalning oxirgi bayti nima deyiladi?', 'Maqtaʼ', ['Matlaʼ', 'Radif', 'Tuyuq']),
       mc('Misralar oxiridagi ohangdosh soʻzlar nima deyiladi?', 'Qofiya', ['Radif', 'Bayt', 'Misra']), mc('Qofiyadan keyin takrorlanadigan soʻz nima deyiladi?', 'Radif', ['Qofiya', 'Matlaʼ', 'Vazn']),
       mc('Sheʼrning bir qatori nima deyiladi?', 'Misra', ['Bayt', 'Band', 'Qofiya']), mc('Tuyuq necha misradan iborat?', '4', ['2', '5', '6']),
       mc('Muxammas har bandi necha misradan iborat?', '5', ['4', '3', '6']), mc('Mumtoz adabiyotda shoir taxallusi koʻpincha qayerda keladi?', 'Maqtaʼda', ['Matlaʼda', 'Sarlavhada', 'Radifda'])]
B.topic(F4, 'turjanr', 'Adabiy turlar va janrlar, sheʼr tuzilishi', [7, 8], tr_g1, tr2, tr3, 'adabiyot tur janr epik lirik dramatik gʻazal ruboiy')

MUM = [mc('Alisher Navoiy qaysi shaharda tugʻilgan?', 'Hirot', ['Samarqand', 'Buxoro', 'Andijon']), mc('Alisher Navoiy qaysi yili tugʻilgan?', '1441', ['1483', '1370', '1501']),
       mc('«Xamsa» nechta dostondan iborat?', '5', ['3', '4', '7']), mc('Zahiriddin Muhammad Bobur qaysi shaharda tugʻilgan?', 'Andijon', ['Hirot', 'Samarqand', 'Toshkent']),
       mc('Bobur qaysi yili tugʻilgan?', '1483', ['1441', '1526', '1370']), mc('Bobur qaysi davlatga asos solgan?', 'Hindistondagi Boburiylar davlati', ['Temuriylar davlati', 'Xiva xonligi', 'Qoʻqon xonligi']),
       mc('«Farhod va Shirin» qaysi asar tarkibiga kiradi?', '«Xamsa»', ['«Boburnoma»', '«Qutadgʻu bilig»', '«Mahbub ul-qulub»']),
       mc('«Layli va Majnun» dostonini oʻzbek tilida kim yozgan?', 'Alisher Navoiy', ['Bobur', 'Lutfiy', 'Ogahiy']),
       mc('Alisher Navoiyning taxallusi turkiy sheʼrlarida qanday?', 'Navoiy', ['Foniy', 'Bobur', 'Lutfiy']), mc('Navoiy forsiy sheʼrlarida qanday taxallus ishlatgan?', 'Foniy', ['Navoiy', 'Mashrab', 'Ogahiy']),
       mc('«Boburnoma» qanday asar?', 'Memuar (esdalik) asar', ['Doston', 'Gʻazallar toʻplami', 'Ertak']), mc('«Qutadgʻu bilig» muallifi kim?', 'Yusuf Xos Hojib', ['Mahmud Koshgʻariy', 'Ahmad Yugnakiy', 'Alisher Navoiy']),
       mc('«Devonu lugʻotit turk» qanday asar?', 'Turkiy soʻzlar lugʻati', ['Doston', 'Roman', 'Tarixiy solnoma']),
       mc('«Mahbub ul-qulub» asari qaysi janrga yaqin?', 'Pand-nasihat (axloqiy-taʼlimiy) asar', ['Roman', 'Komediya', 'Doston']),
       mc('Alisher Navoiy qaysi hukmdorning yaqin doʻsti boʻlgan?', 'Husayn Boyqaro', ['Amir Temur', 'Bobur', 'Ulugʻbek'])]
YAN = [mc('Birinchi oʻzbek romani qaysi?', '«Oʻtkan kunlar»', ['«Kecha va kunduz»', '«Navoiy»', '«Sarob»']), mc('«Oʻtkan kunlar» romanining bosh qahramoni kim?', 'Otabek', ['Anvar', 'Zebi', 'Saidiy']),
       mc('«Mehrobdan chayon» romanining bosh qahramoni kim?', 'Anvar', ['Otabek', 'Shum bola', 'Hoshimjon']), mc('«Shum bola» asarining qahramoni kim?', 'Qoravoy', ['Otabek', 'Anvar', 'Hoshimjon']),
       mc('Choʻlponning asl ismi nima?', 'Abdulhamid Sulaymon oʻgʻli', ['Abdulla Qodiriy', 'Musa Toshmuhammad oʻgʻli', 'Gʻafur Gʻulom']),
       mc('Oybekning asl ismi nima?', 'Muso Toshmuhammad oʻgʻli', ['Abdulhamid Sulaymon oʻgʻli', 'Gʻafur Gʻulom', 'Abdulla Qahhor']),
       mc('Oʻzbekiston Respublikasi Davlat madhiyasi soʻzlari muallifi kim?', 'Abdulla Oripov', ['Erkin Vohidov', 'Gʻafur Gʻulom', 'Choʻlpon']),
       mc('«Oʻtkan kunlar» qanday asar?', 'Tarixiy roman', ['Doston', 'Komediya', 'Gʻazal']), mc('«Ulugʻbek xazinasi» romanining muallifi kim?', 'Odil Yoqubov', ['Oybek', 'Said Ahmad', 'Pirimqul Qodirov']),
       mc('«Yulduzli tunlar» romani kim haqida?', 'Bobur', ['Navoiy', 'Ulugʻbek', 'Amir Temur'])]
YAN = [x for x in YAN if 'Oybekning asl ismi' not in x['q']]
B.topic(F4, 'mumtoz', 'Mumtoz va yangi oʻzbek adabiyoti', [8, 9], MUM[:10], MUM[5:] + YAN[:5], YAN + MUM[10:], 'adabiyot Navoiy Bobur Qodiriy Choʻlpon mumtoz')


# ---- imlo: qoʻshib, ajratib, chiziqcha bilan ----
CHIZ = ['ota-ona', 'aka-uka', 'asta-sekin', 'kecha-kunduz', 'oq-qora', 'yaxshi-yomon', 'bordi-keldi', 'katta-kichik', 'opa-singil', 'tez-tez', 'qozon-tovoq', 'sekin-sekin']
QOSH = ['toshbaqa', 'kungaboqar', 'belbogʻ', 'bilaguzuk', 'qoʻlyozma', 'beshbarmoq', 'otquloq', 'gultojixoʻroz', 'oshqozon']
AJR = ['temir yoʻl', 'ish haqi', 'olib keldi', 'oʻqib chiqdi', 'yozib oldi', 'kelib ketdi', 'har kim', 'hech narsa', 'har doim']
def im_variants(w):
    base = w.replace('-', ' ').replace('ʻ', '\x00')
    parts = base.split(' ')
    v = {w, '-'.join(parts), ''.join(parts), ' '.join(parts)} if len(parts) > 1 else {w}
    return {x.replace('\x00', 'ʻ') for x in v}
def im_q(w):
    parts = w.replace('-', ' ').split(' ')
    if len(parts) == 1: return None
    vs = ['-'.join(parts), ''.join(parts), ' '.join(parts), ', '.join(parts)]
    return mc(f'«{" ".join(parts)}» qanday yoziladi?', w, [x for x in vs if x != w])
def im_g1():
    w = ch(CHIZ); return im_q(w)
def im_g2():
    w = ch(AJR + CHIZ[:6]); return im_q(w)
def im_g3():
    t = R.randrange(4)
    if t == 0: return mc('Qaysi soʻz qoʻshib yoziladi?', ch(QOSH), [ch(CHIZ), ch(AJR), ch([x for x in CHIZ + AJR])]) if True else None
    if t == 1: return mc('Qaysi soʻz chiziqcha bilan yoziladi?', ch(CHIZ), R.sample(QOSH, 2) + [ch(AJR)])
    if t == 2: return mc('Qaysi birikma ajratib yoziladi?', ch(AJR), R.sample(QOSH, 2) + [ch(CHIZ)])
    return ch([mc('Juft soʻzlar qanday yoziladi?', 'Chiziqcha bilan', ['Qoʻshib', 'Ajratib', 'Qoʻshtirnoqda']), mc('Takroriy soʻzlar (sekin-sekin) qanday yoziladi?', 'Chiziqcha bilan', ['Qoʻshib', 'Ajratib', 'Vergul bilan']),
               mc('Qoʻshma otlar (toshbaqa, kungaboqar) qanday yoziladi?', 'Qoʻshib', ['Chiziqcha bilan', 'Ajratib', 'Qoʻshtirnoqda']), mc('Koʻmakchi feʼllar (oʻqib chiqdi) qanday yoziladi?', 'Ajratib', ['Qoʻshib', 'Chiziqcha bilan', 'Qoʻshtirnoqda'])])
B.topic(F1, 'imlo', 'Qoʻshib, ajratib va chiziqcha bilan yozish', [7], im_g1, im_g2, im_g3, 'imlo yozilish juft soʻz qoʻshma soʻz chiziqcha')

# ---- uyushiq boʻlaklar ----
UY = [('Ali, Vali va Sardor maktabga keldi.', 'Ali, Vali, Sardor', 'Uyushiq ega'), ('Bozordan olma, nok va uzum oldik.', 'olma, nok, uzum', 'Uyushiq toʻldiruvchi'),
      ('Bolalar kuldi, sakradi, qoʻshiq aytdi.', 'kuldi, sakradi, qoʻshiq aytdi', 'Uyushiq kesim'), ('Qizil, sariq, yashil gullar ochildi.', 'qizil, sariq, yashil', 'Uyushiq aniqlovchi'),
      ('U tez va chiroyli yozadi.', 'tez, chiroyli', 'Uyushiq hol'), ('Daftar, qalam va kitob stolda yotibdi.', 'daftar, qalam, kitob', 'Uyushiq ega'),
      ('Ukam rasm chizdi va uni menga koʻrsatdi.', 'chizdi, koʻrsatdi', 'Uyushiq kesim'), ('Biz Samarqand, Buxoro va Xivani koʻrdik.', 'Samarqand, Buxoro, Xivani', 'Uyushiq toʻldiruvchi')]
UYL = ['Uyushiq ega', 'Uyushiq kesim', 'Uyushiq toʻldiruvchi', 'Uyushiq aniqlovchi', 'Uyushiq hol']
def uy_g1():
    s, w, lab = ch(UY); others = [x[1] for x in UY if x[1] != w]
    return mc(f'«{s}» gapidagi uyushiq boʻlaklar qaysi?', w, R.sample(others, 3))
def uy_g2():
    s, w, lab = ch(UY); return mc(f'«{s}» gapida qanday uyushiq boʻlak bor?', lab, R.sample([x for x in UYL if x != lab], 3))
uy3 = [mc('Uyushiq boʻlaklar nima?', 'Bir xil soʻroqqa javob berib, bir boʻlakka bogʻlanuvchi boʻlaklar', ['Gapning bosh boʻlaklari', 'Undalmalar', 'Kirish soʻzlar']),
       mc('Bogʻlovchisiz uyushiq boʻlaklar orasiga qanday belgi qoʻyiladi?', 'Vergul', ['Nuqta', 'Tire', 'Ikki nuqta']),
       mc('Umumlashtiruvchi soʻzdan keyin kelgan uyushiq boʻlaklar oldidan qanday belgi qoʻyiladi?', 'Ikki nuqta', ['Vergul', 'Tire', 'Nuqta']),
       mc('Uyushiq boʻlaklardan oldin kelgan umumlashtiruvchi soʻz qaysi?', 'hamma, barcha', ['va, lekin', 'albatta', 'kecha']),
       mc('«Bogʻda turli mevalar bor: olma, nok, shaftoli» gapidagi umumlashtiruvchi soʻz qaysi?', 'mevalar', ['bogʻda', 'olma', 'shaftoli']),
       mc('«va» bogʻlovchisidan oldin vergul qoʻyiladimi (uyushiq boʻlaklarda)?', 'Yoʻq', ['Ha, doim', 'Faqat gap boshida', 'Faqat kesimda']),
       mc('Qaysi gapda uyushiq boʻlak bor?', 'Olma va nok pishdi.', ['Olma pishdi.', 'Nok shirin.', 'Bogʻda olma bor.']),
       mc('Uyushiq boʻlaklar bir-biri bilan qanday bogʻlanadi?', 'Teng bogʻlovchilar yoki ohang bilan', ['Ergashtiruvchi bogʻlovchi bilan', 'Koʻmakchi bilan', 'Faqat «chunki» bilan']),
       mc('«Lekin», «ammo» bilan bogʻlangan uyushiq boʻlaklar orasiga nima qoʻyiladi?', 'Vergul', ['Hech narsa', 'Nuqta', 'Ikki nuqta']), mc('Gapning qaysi boʻlaklari uyushib kela oladi?', 'Barcha boʻlaklari', ['Faqat ega', 'Faqat kesim', 'Faqat hol'])]
B.topic(F3, 'uyushiq', 'Uyushiq boʻlakli gaplar', [8], uy_g1, uy_g2, uy3, 'sintaksis uyushiq boʻlak tinish belgisi')

# ---- koʻchirma va oʻzlashtirma gap ----
KO = [('«Men ertaga kelaman», — dedi Ali.', 'Koʻchirma gap'), ('Ali ertaga kelishini aytdi.', 'Oʻzlashtirma gap'), ('Ustoz: «Darsga tayyorlaning», — dedi.', 'Koʻchirma gap'),
      ('Ustoz darsga tayyorlanishimizni aytdi.', 'Oʻzlashtirma gap'), ('«Kitobni qayerdan olding?» — soʻradi opam.', 'Koʻchirma gap'), ('Opam kitobni qayerdan olganimni soʻradi.', 'Oʻzlashtirma gap'),
      ('Dadam: «Sport bilan shugʻullan», — dedi.', 'Koʻchirma gap'), ('Dadam sport bilan shugʻullanishimni maslahat berdi.', 'Oʻzlashtirma gap')]
ko_g1 = lambda: (lambda s, lab: mc(f'{s} — bu qanday gap?', lab, ['Koʻchirma gap', 'Oʻzlashtirma gap', 'Undalma', 'Kirish gap']))(*ch(KO))
ko2 = [mc('Koʻchirma gap qanday belgi ichiga olinadi?', 'Qoʻshtirnoq', ['Qavs', 'Tire', 'Vergul']), mc('Koʻchirma gap nima?', 'Birovning gapi oʻzgarishsiz berilishi', ['Birovning gapi mazmunan berilishi', 'Kirish soʻz', 'Undalma']),
       mc('Oʻzlashtirma gap nima?', 'Birovning gapi soʻzlovchi nomidan mazmunan berilishi', ['Birovning gapi aynan berilishi', 'Undalma', 'Kirish gap']),
       mc('Koʻchirma gapdan keyin kelgan muallif gapi oldidan qanday belgi qoʻyiladi?', 'Vergul va tire', ['Nuqta', 'Ikki nuqta', 'Soʻroq belgisi']),
       mc('Muallif gapi koʻchirma gapdan oldin kelsa, undan keyin qanday belgi qoʻyiladi?', 'Ikki nuqta', ['Tire', 'Nuqta', 'Vergul']),
       mc('Koʻchirma gapli qoʻshma tuzilmada muallif gapi nimani bildiradi?', 'Gap kimga tegishli ekanini', ['Gap mazmunini', 'Tinish belgisini', 'Kirish soʻzni'])]
ko3 = [mc('«Men charchadim», — dedi Vali. Oʻzlashtirma shakli qaysi?', 'Vali charchaganini aytdi.', ['Vali: «Men charchadim», — dedi.', 'Vali charchadi.', '«Vali charchadi», — dedim.']),
       mc('«Sen kelasanmi?» — soʻradi Lola. Oʻzlashtirma shakli qaysi?', 'Lola kelish-kelmasligimni soʻradi.', ['Lola keldi.', 'Lola: «Kelasanmi?» — dedi.', 'Lola kelmadi.']),
       mc('Qaysi gap koʻchirma gapli?', 'Onam: «Ehtiyot boʻl», — dedi.', ['Onam ehtiyot boʻlishimni aytdi.', 'Onam ehtiyotkor.', 'Ehtiyot boʻl.']),
       mc('Qaysi gap oʻzlashtirma gap?', 'Ukam kech qolishini aytdi.', ['«Kech qolaman», — dedi ukam.', 'Ukam: «Kech qolaman», — dedi.', 'Kech qolma!']),
       mc('Koʻchirma gap oʻzlashtirmaga aylantirilganda qaysi belgi tushib qoladi?', 'Qoʻshtirnoq', ['Nuqta', 'Vergul', 'Hech qaysi']), ] + ko2[:5]
B.topic(F3, 'kochirma', 'Koʻchirma va oʻzlashtirma gap', [9], ko_g1, ko2 + [ko_g1() for _ in range(6)], ko3, 'sintaksis koʻchirma oʻzlashtirma tinish belgisi qoʻshtirnoq')

# ---- nutq uslublari ----
USL = {'Soʻzlashuv uslubi': ['Doʻstlar orasidagi suhbat', 'Oila davrasidagi gap-soʻz', 'Telefondagi oddiy suhbat'],
       'Rasmiy uslub': ['Ariza', 'Buyruq (hujjat)', 'Ishonchnoma', 'Tilxat'], 'Ilmiy uslub': ['Darslik matni', 'Ilmiy maqola', 'Ensiklopediya maqolasi'],
       'Publitsistik uslub': ['Gazeta maqolasi', 'Teleko‘rsatuvdagi chiqish', 'Yigʻilishdagi nutq'], 'Badiiy uslub': ['Hikoya', 'Sheʼr', 'Roman']}
USL['Publitsistik uslub'] = ['Gazeta maqolasi', 'Televideniyedagi chiqish', 'Mitingdagi nutq']
UL = list(USL)
us_g1 = cls('«{w}» qaysi nutq uslubiga mansub?', USL, UL)
us2 = [mc('Nutq uslublari nechta?', '5', ['3', '4', '6']), mc('Qaysi uslubda obrazli ifodalar, tasviriy vositalar koʻp?', 'Badiiy uslub', ['Rasmiy uslub', 'Ilmiy uslub', 'Soʻzlashuv uslubi']),
       mc('Qaysi uslubda atamalar (terminlar) koʻp ishlatiladi?', 'Ilmiy uslub', ['Badiiy uslub', 'Soʻzlashuv uslubi', 'Publitsistik uslub']),
       mc('Qaysi uslub qatʼiy shakl va qoliplarga ega?', 'Rasmiy uslub', ['Badiiy uslub', 'Soʻzlashuv uslubi', 'Publitsistik uslub']),
       mc('Ommaviy axborot vositalari qaysi uslubdan foydalanadi?', 'Publitsistik uslub', ['Ilmiy uslub', 'Rasmiy uslub', 'Badiiy uslub']),
       mc('Kundalik hayotdagi erkin suhbat qaysi uslubga xos?', 'Soʻzlashuv uslubi', ['Rasmiy uslub', 'Ilmiy uslub', 'Badiiy uslub'])] + [us_g1() for _ in range(5)]
us3 = [mc('«Fotosintez — yashil oʻsimliklarda yorugʻlik taʼsirida organik modda hosil boʻlishi» — qaysi uslub?', 'Ilmiy uslub', ['Badiiy uslub', 'Soʻzlashuv uslubi', 'Rasmiy uslub']),
       mc('«Maktab direktoriga 7-«A» sinf oʻquvchisidan ariza» — qaysi uslub?', 'Rasmiy uslub', ['Ilmiy uslub', 'Badiiy uslub', 'Publitsistik uslub']),
       mc('«Oy kumush nurlarini sochib, tun pardasini yoritdi» — qaysi uslub?', 'Badiiy uslub', ['Ilmiy uslub', 'Rasmiy uslub', 'Soʻzlashuv uslubi']),
       mc('«Qalaysan, oshna? Ishlar joyidami?» — qaysi uslub?', 'Soʻzlashuv uslubi', ['Rasmiy uslub', 'Ilmiy uslub', 'Badiiy uslub']),
       mc('«Aziz yurtdoshlar! Barchangizni bayram bilan qutlayman!» — qaysi uslubga yaqin?', 'Publitsistik uslub', ['Ilmiy uslub', 'Rasmiy uslub', 'Soʻzlashuv uslubi']),
       mc('«Suv 100 °C da qaynaydi» — qaysi uslub?', 'Ilmiy uslub', ['Badiiy uslub', 'Soʻzlashuv uslubi', 'Publitsistik uslub']),
       mc('«Men, Karimov Aziz, kutubxonadan 3 ta kitob olganimni tasdiqlayman» — qaysi uslub?', 'Rasmiy uslub', ['Badiiy uslub', 'Soʻzlashuv uslubi', 'Ilmiy uslub'])] + [us_g1() for _ in range(5)]
B.topic(F1, 'uslub', 'Nutq uslublari', [9], us_g1, us2, us3, 'uslub nutq rasmiy ilmiy badiiy publitsistik soʻzlashuv')

# ---- rasmiy hujjatlar ----
HUJ = [('Ariza', 'Biror iltimos bilan rasmiy murojaat'), ('Tilxat', 'Biror narsani olganlikni tasdiqlovchi hujjat'), ('Ishonchnoma', 'Boshqa shaxsga vakolat beruvchi hujjat'),
       ('Tarjimai hol', 'Shaxsning oʻz hayoti haqidagi maʼlumoti'), ('Tavsifnoma', 'Shaxsning ish va xulqiga berilgan baho'), ('Eʼlon', 'Koʻpchilikka maʼlumot beruvchi qisqa matn'),
       ('Bildirishnoma', 'Rahbarga biror holat haqida maʼlum qilish'), ('Taklifnoma', 'Tadbirga chaqiruv')]
HN = [h[0] for h in HUJ]; HD = [h[1] for h in HUJ]
def hj_g1():
    a, b = ch(HUJ); return mc(f'{b} — bu qanday hujjat?', a, R.sample([x for x in HN if x != a], 3))
def hj_g2():
    a, b = ch(HUJ); return mc(f'«{a}» nima?', b, R.sample([x for x in HD if x != b], 3))
hj3 = [mc('Arizada birinchi navbatda nima yoziladi?', 'Kimga yozilayotgani', ['Imzo', 'Sana', 'Xulosa']), mc('Tilxat qachon yoziladi?', 'Biror narsani olganda', ['Ishga kirganda', 'Bayramga taklif qilganda', 'Kitob oʻqiganda']),
       mc('Ishonchnoma nima uchun kerak?', 'Ishni boshqa kishi bajarishi uchun vakolat berish', ['Iltimos qilish', 'Hayot haqida maʼlumot berish', 'Tadbirga chaqirish']),
       mc('Tarjimai hol kimning nomidan yoziladi?', 'Shaxsning oʻz nomidan (I shaxsda)', ['Rahbar nomidan', 'Ota-ona nomidan', 'Sinf nomidan']),
       mc('Tavsifnomani kim yozadi?', 'Rahbar yoki ustoz', ['Shaxsning oʻzi', 'Doʻstlari', 'Qoʻshnilari']), mc('Rasmiy hujjatlar qaysi uslubda yoziladi?', 'Rasmiy uslubda', ['Badiiy uslubda', 'Soʻzlashuv uslubida', 'Publitsistik uslubda']),
       mc('Hujjat oxirida odatda nima qoʻyiladi?', 'Sana va imzo', ['Rasm', 'Sheʼr', 'Maqol']), mc('Qaysi hujjatda «Iltimos qilaman» iborasi koʻp uchraydi?', 'Ariza', ['Tilxat', 'Tarjimai hol', 'Eʼlon'])] + [hj_g1() for _ in range(3)]
B.topic(F1, 'hujjat', 'Rasmiy hujjatlar: ariza, tilxat, ishonchnoma', [8, 9], hj_g1, hj_g2, hj3, 'ish yuritish hujjat ariza tilxat ishonchnoma tarjimai hol')

B.save()
