# -*- coding: utf-8 -*-
"""Rus tili savollar bazasi: umumiy yordamchilar (ru_*.py fayllari shu yerdan foydalanadi)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Baza

B = Baza('Rus tili', 'rus-tili', 2029)
R = B.R; ch = R.choice; mc = B.mc
BL = 'Lugʻat (soʻzlar)'; BF = 'Fonetika va imlo'; BS = 'Soʻz tarkibi va leksika'; BM = 'Morfologiya (soʻz turkumlari)'; BX = 'Sintaksis va tinish belgilari'; BA = 'Adabiyot'

def wr(pool, right, k=3):
    return R.sample([x for x in pool if x != right], k)

VOC = {}        # mavzu -> rus soʻzlari (ortiqcha soʻzni topish uchun)
NEAR = {('tana', 'salomatlik'), ('oila', 'tanishuv'), ('oziq', 'hayvon'), ('maktab', 'internet'), ('uy', 'kiyim'), ('fasl', 'vaqt'), ('transport', 'mamlakat'), ('kasb', 'zdorov'), ('kasb', 'transport'), ('kasb', 'maktab'), ('hobbi', 'internet'), ('xarakter', 'oila'), ('kasb', 'hobbi'), ('kun', 'hobbi'), ('internet', 'transport'), ('uy', 'maktab'), ('kun', 'zdorov'), ('hayvon', 'hobbi')}

def vocab(tid, name, sinf, pairs, k='', sizes=None):
    ru = [a for a, b in pairs]; uz = [b for a, b in pairs]; VOC[tid] = ru
    def g1():
        a, b = ch(pairs); return mc(f'«{a}» soʻzining tarjimasi qaysi?', b, wr(uz, b))
    def g2():
        a, b = ch(pairs); return mc(f'«{b}» ruscha qanday?', a, wr(ru, a))
    def g3():
        if R.random() < .25:
            return ch([g1, g2])()
        others = [w for t, ws in VOC.items() if t != tid and (t[2:], tid[2:]) not in NEAR and (tid[2:], t[2:]) not in NEAR for w in ws]
        if not others: return ch([g1, g2])()
        three = R.sample(ru, 3); x = ch(others)
        if x in ru: return None
        o = three[:]; c = R.randrange(4); o.insert(c, x)
        return {'q': 'Qaysi soʻz mavzuga mos kelmaydi (ortiqcha)?', 'o': o, 'c': c}
    B.topic(BL, tid, name, sinf, g1, g2, g3, k)

def cls(bob, tid, name, sinf, cats, q1, q2, q3, k='', decoys=(), lv=None):
    """cats: {kategoriya: [soʻzlar]}; q1(item)->savol, q2(cat)->savol, q3(cat)->savol"""
    keys = list(cats)
    allc = keys + [d for d in decoys if d not in keys]
    items = [(it, c) for c in keys for it in cats[c]]
    def g1():
        it, c = ch(items); return mc(q1(it), c, wr(allc, c))
    def g2():
        c = ch(keys); it = ch(cats[c]); w = [x for k2 in keys if k2 != c for x in cats[k2] if x not in cats[c]]
        return mc(q2(c), it, R.sample(w, 3))
    def g3():
        c = ch([x for x in keys if len(cats[x]) >= 3]); three = R.sample(cats[c], 3)
        w = [x for k2 in keys if k2 != c for x in cats[k2] if x not in cats[c]]; x = ch(w)
        o = three[:]; p = R.randrange(4); o.insert(p, x)
        return {'q': q3(c), 'o': o, 'c': p}
    if len(allc) < 4: g1 = g2
    gs = {'1': g1, '2': g2, '3': g3}
    order = lv or '123'
    B.topic(bob, tid, name, sinf, gs[order[0]], gs[order[1]], gs[order[2]], k)
