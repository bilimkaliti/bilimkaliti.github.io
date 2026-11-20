# -*- coding: utf-8 -*-
"""Rus tili (5–8-sinf) savollar bazasi: games/baza/rus-tili.json
Manba: 5–6 va 7–8-sinf yillik rejalari (3 ta fayl). Ishga tushirish: python3 src_baza/rus_tili.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ru_base import B
import ru_lex, ru_fon, ru_sos, ru_mor1, ru_mor2, ru_mor3, ru_mor4, ru_mor5, ru_mor6, ru_mor7, ru_syn, ru_lit
# darajalar orasidagi takrorlarni olib tashlash (daraja soni 8 dan kam boʻlmasa)
for t in B.topics:
    seen = {}
    for lvl in (1, 2, 3):
        cnt = sum(1 for i in t['items'] if i['d'] == lvl)
        for it in list(t['items']):
            if it['d'] != lvl: continue
            k = (it['q'], it['o'][it['c']] if 'o' in it else it.get('a'))
            if k in seen and seen[k] != lvl and cnt > 8:
                t['items'].remove(it); cnt -= 1
            else: seen.setdefault(k, lvl)
B.save()
