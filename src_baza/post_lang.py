"""Ingliz va Rus tili banklariga qoʻshimcha savol turlari va qiyin mavzularni olib tashlash.
Ishlatish: generatorlardan (python3 src_baza/rus_tili.py va ingliz) keyin: python3 src_baza/post_lang.py
Idempotent: qayta ishga tushirsa ham takrorlanmaydi."""
import json,re,random,os
HERE=os.path.dirname(os.path.abspath(__file__));BAZA=os.path.join(HERE,'..','games','baza')
REMOVE={
 'ingliz':{'shart','relative','yasalish'},
 'rus-tili':{'r_arhaizm','r_razdel','r_paronim','r_slovoobr','r_neskl','r_odnosost','r_spp','r_slozhn','r_pryamaya','r_prich','r_prichob','r_deeprich','r_deepob','r_naklon','r_sufgl','r_perehod','r_nnn','r_razmest'}}
# faqat xato aniq boʻladigan (bir nechta toʻgʻri javob boʻlmaydigan) grammatika mavzulari
ERR_OK={'ingliz':{'tobe','artikl','koplik','present','pastreg','continuous','daraja','perfect','passive','pastcont','irregular','there'},
 'rus-tili':{'r_rod','r_sklon','r_padej','r_chislo','r_prilag','r_sklpr','r_lichn','r_prit','r_proshed','r_son3','r_predlog','r_predlog2','r_stepen','r_kratk'}}
ORD='Gapni toʻgʻri tartibga soling'
def clean(i,lang):
    q=i['q']
    if lang=='rus-tili' and ':' in q: q=q.split(':',1)[1].strip()
    elif lang=='ingliz' and ':' in q:
        pre,rest=q.split(':',1)
        if len(pre.split())<=4: q=rest.strip()
        else: return None
    q=re.sub(r'\s*\([^)]*\)','',q)
    if q.count('___')!=1 or re.search(r'\w___|___\w',q) or '(' in q: return None
    if '/' in ''.join(i['o']): return None
    return re.sub(r'\s+',' ',q).strip()
def fill(q,w): return re.sub(r'\s+',' ',q.replace('___',w)).strip()
def ok_sent(s,lang):
    w=s.split(' ')
    if not s[0].isupper() or s[-1] not in '.!?': return False
    if lang=='rus-tili' and re.search(r'[A-Za-z]|…|\.\.\.',s): return False
    return True
def main():
    random.seed(11);rep={}
    for lang in ('ingliz','rus-tili'):
        p=os.path.join(BAZA,lang+'.json');j=json.load(open(p,encoding='utf-8'))
        bk=os.path.join(HERE,'removed_'+lang+'.json')
        rem=[t for t in j['topics'] if t['id'] in REMOVE[lang]]
        if rem:
            old=json.load(open(bk,encoding='utf-8')) if os.path.exists(bk) else []
            ids={t['id'] for t in old};json.dump(old+[t for t in rem if t['id'] not in ids],open(bk,'w',encoding='utf-8'),ensure_ascii=False)
        j['topics']=[t for t in j['topics'] if t['id'] not in REMOVE[lang]]
        n_ord=n_err=n_find=0
        for t in j['topics']:
            t['items']=[i for i in t['items'] if 's' not in i and not i.get('q','').startswith(('✏️','🔍'))]
            base=[i for i in t['items'] if 'o' in i]
            order=[];fix=[];find=[];seen=set()
            for i in base:
                q=clean(i,lang)
                if not q: continue
                good=i['o'][i['c']];full=fill(q,good)
                if not ok_sent(full,lang) or full in seen: continue
                words=full.split(' ');seen.add(full)
                if 4<=len(words)<=8 and len({x.lower().strip('.,!?;') for x in words})==len(words): order.append({'q':ORD,'s':words})
                if t['id'] not in ERR_OK[lang]: continue
                wr=[w for k,w in enumerate(i['o']) if k!=i['c']]
                if len(words)>=4 and not re.search(r'[.!?] ',full):
                    wr=[w for w in wr if w.lower() not in ('already','yet','ever','never','just','since','for','still','always','often')]
                    if not wr: continue
                    bad=random.choice(wr);wrong=fill(q,bad)
                    if lang=='rus-tili' and re.search(r'\w___|___\w',q): continue
                    # 1) xatoni toʻgʻrilang: 4 ta tayyor gap
                    opts=[fill(q,w) for w in i['o']];opts=list(dict.fromkeys(opts))
                    if len(opts)==4 and wrong in opts and len(full)<=70:
                        random.shuffle(opts);fix.append({'q':f'✏️ Xatoni toʻgʻrilang: «{wrong}»','o':opts,'c':opts.index(full)})
                    # 2) xato qaysi soʻzda
                    wl=wrong.split(' ');norm=lambda x:x.strip('.,!?;:')
                    bi=[k for k,x in enumerate(wl) if norm(x)==bad]
                    if len(bi)==1 and len({norm(x).lower() for x in wl})==len(wl):
                        others=[norm(x) for k,x in enumerate(wl) if k!=bi[0]];
                        if len(others)>=3:
                            o=random.sample(others,3)+[bad];random.shuffle(o)
                            find.append({'q':f'🔍 Gapda xato qaysi soʻzda? «{wrong}»','o':o,'c':o.index(bad)})
            random.shuffle(order);random.shuffle(fix);random.shuffle(find)
            # tartib: uzunlikka qarab daraja
            o=sorted(order[:12],key=lambda i:(len(i['s']),sum(map(len,i['s']))))
            if len(o)>=4:
                for k,i in enumerate(o): i['d']=1+min(2,k*3//len(o))
                t['items']+=o;n_ord+=len(o)
            if len(fix)+len(find)>=4:
                ex=[]
                for k,i in enumerate(fix[:5]): i['d']=2 if k%2==0 else 3;ex.append(i)
                for k,i in enumerate(find[:5]): i['d']=3 if k%2==0 else 2;ex.append(i)
                t['items']+=ex;n_err+=len(fix[:5]);n_find+=len(find[:5])
        json.dump(j,open(p,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
        rep[lang]=(len(j['topics']),n_ord,n_err,n_find)
    print(rep)
main()
