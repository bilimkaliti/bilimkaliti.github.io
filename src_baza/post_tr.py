# Ingliz tili "tartibga sol" gaplariga oʻzbekcha tarjima qoʻshadi (post_lang.py dan keyin ishga tushiring)
import json,os
H=os.path.dirname(os.path.abspath(__file__));P=os.path.join(H,'..','games','baza','ingliz.json')
tr=dict(l.rstrip('\n').split('=',1) for l in open(os.path.join(H,'tr_ingliz.txt'),encoding='utf-8') if '=' in l)
norm=lambda x:x.replace("'","’")
tr={norm(k):v for k,v in tr.items()}
j=json.load(open(P,encoding='utf-8'));n=miss=0
for t in j['topics']:
    for i in t['items']:
        if 's' in i:
            en=norm(' '.join(i['s']));u=tr.get(en)
            if u:i['q']='«'+u+'» — inglizcha gapni tuzing';n+=1
            else:miss+=1;print('yoʻq:',en)
json.dump(j,open(P,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print('tarjima qoʻshildi',n,'yoʻq',miss)

# --- Rus tili ---
BAD={'У его нет книги.','У её нет книги.','Я дам мне книгу.'}  # xato gaplar (grammatik notoʻgʻri) — olib tashlanadi
P2=os.path.join(H,'..','games','baza','rus-tili.json')
tr2=dict(l.rstrip('\n').split('=',1) for l in open(os.path.join(H,'tr_rus.txt'),encoding='utf-8') if '=' in l)
j=json.load(open(P2,encoding='utf-8'));n=miss=rm=0
for t in j['topics']:
    keep=[]
    for i in t['items']:
        if 's' in i:
            ru=' '.join(i['s'])
            if ru in BAD:rm+=1;continue
            u=tr2.get(ru)
            if u:i['q']='«'+u+'» — ruscha gapni tuzing';n+=1
            else:miss+=1;print('yoʻq:',ru)
        keep.append(i)
    t['items']=keep
json.dump(j,open(P2,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print('rus: tarjima',n,'yoʻq',miss,'olib tashlandi',rm)
