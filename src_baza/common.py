# -*- coding: utf-8 -*-
"""Barcha fanlar uchun umumiy yordamchilar: savol turlari, toʻplash, yozish va versiya."""
import json, random, os, hashlib, re, glob

N = 10
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


class Baza:
    def __init__(self, fan, slug, seed):
        self.fan, self.slug = fan, slug
        self.R = random.Random(seed)
        self.topics, self.bobs = [], []

    # --- savol turlari ---
    def mc(self, q, right, wrongs):
        right = str(right); ws = []
        for w in wrongs:
            w = str(w)
            if w != right and w not in ws: ws.append(w)
        if len(ws) < 3: return None
        o = self.R.sample(ws, 3); c = self.R.randrange(4); o.insert(c, right)
        return {'q': q, 'o': o, 'c': c}

    def num(self, q, a):
        assert isinstance(a, int) and 0 <= a <= 9999, (q, a)
        return {'q': q, 'a': a}

    def pick(self, pool, k, exclude=()):
        pool = [x for x in pool if x not in exclude]
        return self.R.sample(pool, min(k, len(pool)))

    # --- toʻplash ---
    def collect(self, src, n=N, tries=600):
        """src: generator funksiya yoki tayyor roʻyxat"""
        if isinstance(src, list):
            l = [dict(x) for x in src if x]; self.R.shuffle(l)
            out, seen = [], set()
            for it in l:
                k = it['q'] + '|' + (it['o'][it['c']] if 'o' in it else str(it.get('a')))
                if k in seen: continue
                seen.add(k); out.append(it)
            return out[:n]
        out, seen = [], set()
        for _ in range(tries):
            it = src()
            if not it: continue
            it = dict(it)
            k = it['q'] + '|' + (it['o'][it['c']] if 'o' in it else str(it.get('a')))
            if k in seen: continue
            seen.add(k); out.append(it)
            if len(out) >= n: break
        return out

    def topic(self, bob, tid, name, sinf, g1, g2, g3, k=''):
        items = []
        for d, g in ((1, g1), (2, g2), (3, g3)):
            lst = self.collect(g)
            assert len(lst) >= 6, (tid, d, len(lst))
            for it in lst: it['d'] = d; items.append(it)
        if bob not in self.bobs: self.bobs.append(bob)
        self.topics.append({'id': tid, 'bob': bob, 'name': name, 'sinf': sinf, 'k': k, 'items': items})

    # --- yozish ---
    def save(self):
        ids = [t['id'] for t in self.topics]; assert len(ids) == len(set(ids))
        for t in self.topics:
            for it in t['items']:
                if 'o' in it: assert len(it['o']) == 4 and len(set(it['o'])) == 4 and 0 <= it['c'] < 4, (t['id'], it)
        p = os.path.join(ROOT, 'games', 'baza', self.slug + '.json')
        os.makedirs(os.path.dirname(p), exist_ok=True)
        json.dump({'fan': self.fan, 'v': 1, 'bolimlar': self.bobs, 'topics': self.topics}, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        print(self.fan, ':', len(self.topics), 'mavzu,', sum(len(t['items']) for t in self.topics), 'savol,', os.path.getsize(p) // 1024, 'KB')
        from collections import Counter
        print('  sinflar:', sorted(Counter(x for t in self.topics for x in t['sinf']).items()))
        for t in self.topics:
            c = [sum(1 for i in t['items'] if i['d'] == d) for d in (1, 2, 3)]
            if min(c) < N: print('  kam:', t['id'], c)
        update_version()


def update_version():
    h = hashlib.md5()
    for f in sorted(glob.glob(os.path.join(ROOT, 'games', 'baza', '*.json'))):
        h.update(open(f, 'rb').read())
    v = h.hexdigest()[:8]
    for f in ('index.html', 'games/toplam.html', 'games/bilim.html'):
        fp = os.path.join(ROOT, f); s = open(fp, encoding='utf-8').read()
        s2 = re.sub(r"const BZ_V='[0-9a-f]*';", f"const BZ_V='{v}';", s, count=1)
        if s2 != s: open(fp, 'w', encoding='utf-8').write(s2)
    # games/kinds.json: qaysi fanda qanday turdagi savollar bor (oʻyinlar fan roʻyxatini shu bilan filtrlaydi)
    import json as _j
    K = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'games', 'baza', '*.json'))):
        j = _j.load(open(f, encoding='utf-8')); ks = set()
        for t in j['topics']:
            for i in t['items']:
                ks.add('mc' if ('o' in i or 'a' in i) else 'order' if 's' in i else 'group' if 'g' in i else 'x')
        K[j['fan']] = sorted(ks - {'x'})
    _j.dump(K, open(os.path.join(ROOT, 'games', 'kinds.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('versiya', v)
