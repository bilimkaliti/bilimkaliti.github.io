# "Guruhlarga ajrat" va "Tartibga sol" mavzularini 4 ta bazaga qoʻshadi (matematika, ona-tili, ingliz, rus-tili). Takror ishga tushirish xavfsiz.
import json,os,random,sys
H=os.path.dirname(os.path.abspath(__file__));B=os.path.join(H,'..','games','baza')
sys.path.insert(0,H)
import importlib.util
spec=importlib.util.spec_from_file_location('rasm',os.path.join(H,'post_rasm.py'))
random.seed(11)
K=lambda s:s.split()
def round_(q,groups,d):  # groups: [(name,[words])]
    return {'q':q,'g':[{'n':n,'w':w} for n,w in groups],'d':d}
def pick(lst,n):return random.sample(lst,min(n,len(lst)))
def topic(id,bob,name,sinf,k,items):return {'id':id,'bob':bob,'name':name,'sinf':sinf,'k':k,'items':items}
BG='Guruhlarga ajrat';BO='Tartibga sol'
# ---------- MATEMATIKA ----------
def mat_topics():
    T=[]
    # juft/toq
    it=[]
    for d,hi in ((1,20),(2,100),(3,1000)):
        for _ in range(5):
            ev=pick([x for x in range(1,hi) if x%2==0],4);od=pick([x for x in range(1,hi) if x%2],4)
            it.append(round_('Sonlarni guruhlarga ajrating',[('Juft',[str(x) for x in ev]),('Toq',[str(x) for x in od])],d))
    T.append(topic('g-juft','Guruhlarga ajrat','🗂️ Juft va toq sonlar',[2,3,4],'juft toq son guruh',it))
    # xona
    it=[]
    for d,nb in ((1,2),(2,3),(3,4)):
        rng=[(1,9),(10,99),(100,999),(1000,9999)][:nb];names=['Bir xonali','Ikki xonali','Uch xonali','Toʻrt xonali'][:nb]
        for _ in range(5):
            it.append(round_('Sonlarni xonasiga qarab ajrating',[(n,[str(random.randint(*r)) for _ in range(3 if nb<4 else 2)]) for n,r in zip(names,rng)],d))
    T.append(topic('g-xona','Guruhlarga ajrat','🗂️ Bir, ikki, uch xonali sonlar',[2,3,4],'xonali son guruh',it))
    # boʻlinish
    it=[]
    def only(x,ds):return sum(x%k==0 for k in (2,3,5))==1 and any(x%k==0 for k in ds)
    for d,ds,hi in ((1,(2,5),60),(2,(2,3,5),120),(3,(2,3,5),400)):
        for _ in range(5):
            gs=[]
            for k in ds:
                pool=[x for x in range(6,hi) if only(x,(k,))]
                gs.append((f'{k} ga boʻlinadi',[str(x) for x in pick(pool,3)]))
            it.append(round_('Sonlarni qaysi songa boʻlinishiga qarab ajrating',gs,d))
    T.append(topic('g-bolinish','Guruhlarga ajrat','🗂️ 2, 3 va 5 ga boʻlinish',[5,6],'boʻlinish belgisi guruh',it))
    # tub/murakkab
    pr=[x for x in range(2,100) if all(x%k for k in range(2,int(x**.5)+1))];co=[x for x in range(4,100) if x not in pr]
    it=[]
    for d,hi in ((1,30),(2,60),(3,100)):
        p=[x for x in pr if x<hi];c=[x for x in co if x<hi]
        for _ in range(5):it.append(round_('Sonlarni guruhlarga ajrating',[('Tub son',[str(x) for x in pick(p,4)]),('Murakkab son',[str(x) for x in pick(c,4)])],d))
    T.append(topic('g-tub','Guruhlarga ajrat','🗂️ Tub va murakkab sonlar',[6],'tub murakkab son guruh',it))
    # musbat/manfiy
    it=[]
    for d,hi in ((1,9),(2,99),(3,99)):
        for _ in range(5):
            f=(lambda x:str(x).replace('.',',')) if d==3 else str
            mk=(lambda: round(random.uniform(0.5,hi/10+9),1)) if d==3 else (lambda: random.randint(1,hi))
            pos=sorted({mk() for _ in range(4)});neg=sorted({mk() for _ in range(4)})
            it.append(round_('Sonlarni guruhlarga ajrating',[('Musbat son',[f(x) for x in pos]),('Manfiy son',['−'+f(x) for x in neg])],d))
    T.append(topic('g-musbat','Guruhlarga ajrat','🗂️ Musbat va manfiy sonlar',[6],'musbat manfiy son guruh',it))
    # burchaklar
    it=[]
    for d,names in ((1,['Oʻtkir burchak','Oʻtmas burchak']),(2,['Oʻtkir burchak','Toʻgʻri burchak','Oʻtmas burchak']),(3,['Oʻtkir burchak','Toʻgʻri burchak','Oʻtmas burchak','Yoyiq burchak'])):
        for _ in range(5):
            R={'Oʻtkir burchak':(5,85),'Oʻtmas burchak':(95,175)}
            gs=[]
            for n in names:
                if n=='Toʻgʻri burchak':w=['90°']
                elif n=='Yoyiq burchak':w=['180°']
                else:
                    lo,hi=R[n];w=[f'{x}°' for x in sorted(random.sample(range(lo,hi+1,5),3))]
                gs.append((n,w))
            it.append(round_('Burchaklarni turiga qarab ajrating',gs,d))
    T.append(topic('g-burchak','Guruhlarga ajrat','🗂️ Burchak turlari',[5,6,7],'burchak oʻtkir oʻtmas guruh',it))
    # kasr turi
    it=[]
    for d,names in ((1,2),(2,2),(3,3)):
        for _ in range(5):
            mx=9 if d==1 else 15
            tg=set()
            while len(tg)<3:
                b=random.randint(2,mx);a=random.randint(1,b-1);tg.add(f'{a}/{b}')
            ng=set()
            while len(ng)<3:
                a=random.randint(2,mx);b=random.randint(1,a);ng.add(f'{a}/{b}')
            gs=[('Toʻgʻri kasr',sorted(tg)),('Notoʻgʻri kasr',sorted(ng))]
            if d==3:
                ar=set()
                while len(ar)<3:
                    b=random.randint(2,9);ar.add(f'{random.randint(1,5)} {random.randint(1,b-1)}/{b}')
                gs.append(('Aralash son',sorted(ar)))
            it.append(round_('Kasrlarni turiga qarab ajrating',gs,d))
    T.append(topic('g-kasr','Guruhlarga ajrat','🗂️ Kasr turlari',[5,6],'toʻgʻri notoʻgʻri aralash kasr guruh',it))
    # shakl / jism
    SH=['uchburchak','kvadrat','toʻgʻri toʻrtburchak','doira','beshburchak','oltiburchak','romb','trapetsiya','aylana'];JI=['kub','shar','silindr','konus','piramida','parallelepiped','prizma']
    it=[]
    for d,(a,b) in ((1,(SH[:4],JI[:4])),(2,(SH[:7],JI[:6])),(3,(SH,JI))):
        for _ in range(5):it.append(round_('Shakl va jismlarni ajrating',[('Tekis shakl',pick(a,4)),('Fazoviy jism',pick(b,4))],d))
    T.append(topic('g-shakl','Guruhlarga ajrat','🗂️ Tekis shakllar va fazoviy jismlar',[3,4,5],'shakl jism geometriya guruh',it))
    # oʻlchov birliklari
    U={'Uzunlik':['mm','sm','dm','m','km'],'Massa':['g','kg','sentner','tonna'],'Vaqt':['soniya','minut','soat','sutka','hafta','yil']}
    it=[]
    for d,n in ((1,2),(2,3),(3,3)):
        for _ in range(5):
            ks=pick(list(U),n);it.append(round_('Oʻlchov birliklarini ajrating',[(k,pick(U[k],3)) for k in ks],d))
    T.append(topic('g-birlik','Guruhlarga ajrat','🗂️ Oʻlchov birliklari',[3,4,5],'uzunlik massa vaqt birlik guruh',it))
    # --- tartibga sol ---
    it=[]
    for d,(lo,hi,n,dec) in ((1,(1,20,4,0)),(2,(10,999,5,0)),(3,(1,99,5,1))):
        for asc in (True,False):
            for _ in range(5):
                v=set()
                while len(v)<n:v.add(round(random.uniform(lo,hi),1) if dec else random.randint(lo,hi))
                v=sorted(v);v=v if asc else v[::-1];f=(lambda x:str(x).replace('.',',')) if dec else str
                it.append({'q':'Sonlarni '+('kichikdan kattaga' if asc else 'kattadan kichikka')+' tartiblang','s':[f(x) for x in v],'d':d})
    T.append(topic('o-sonlar','Tartibga sol','📅 Sonlarni tartiblash',[1,2,3,4,5,6],'sonlarni tartiblash oʻsish kamayish',it))
    OU=[('Uzunlik birliklarini kichikdan kattaga tartiblang',['mm','sm','dm','m','km'],1),('Massa birliklarini kichikdan kattaga tartiblang',['g','kg','sentner','tonna'],1),('Vaqt birliklarini kichikdan kattaga tartiblang',['soniya','minut','soat','sutka','hafta','yil'],2),('Uzunlik birliklarini kattadan kichikka tartiblang',['km','m','dm','sm','mm'],2),('Vaqt birliklarini kattadan kichikka tartiblang',['yil','hafta','sutka','soat','minut','soniya'],3),('Massa birliklarini kattadan kichikka tartiblang',['tonna','sentner','kg','g'],2)]
    T.append(topic('o-birlik','Tartibga sol','📅 Oʻlchov birliklarini tartiblash',[3,4,5],'birlik tartib uzunlik massa vaqt',[{'q':q,'s':s,'d':d} for q,s,d in OU]))
    return T
# ---------- umumiy: kunlar/oylar/fasllar ----------
def calendar_topic(lang):
    D={'uz':(['Dushanba','Seshanba','Chorshanba','Payshanba','Juma','Shanba','Yakshanba'],['Yanvar','Fevral','Mart','Aprel','May','Iyun','Iyul','Avgust','Sentabr','Oktabr','Noyabr','Dekabr'],['Qish','Bahor','Yoz','Kuz']),
       'en':(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],['January','February','March','April','May','June','July','August','September','October','November','December'],['Winter','Spring','Summer','Autumn']),
       'ru':(['Понедельник','Вторник','Среда','Четверг','Пятница','Суббота','Воскресенье'],['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'],['Зима','Весна','Лето','Осень'])}[lang]
    q={'uz':('Hafta kunlarini tartib bilan joylang','Oylarni yil boʻyicha tartiblang','Fasllarni tartib bilan joylang'),
       'en':('Put the days of the week in order','Put the months in order','Put the seasons in order'),
       'ru':('Расставьте дни недели по порядку','Расставьте месяцы по порядку','Расставьте времена года по порядку')}[lang]
    days,months,seas=D;it=[]
    it.append({'q':q[0],'s':days[:5],'d':1});it.append({'q':q[0],'s':days[2:],'d':1});it.append({'q':q[0],'s':days,'d':2})
    it.append({'q':q[2],'s':seas,'d':1})
    for st in (0,2,4,6,1,3,5,7):it.append({'q':q[1],'s':months[st:st+(4 if st%2 else 5)],'d':2 if st<4 else 3})
    it.append({'q':q[1],'s':months[:8],'d':3})
    return topic('o-kalendar','Tartibga sol','📅 '+{'uz':'Hafta kunlari, oylar, fasllar','en':'Days, months, seasons','ru':'Дни, месяцы, времена года'}[lang],[2,3,4],'kun oy fasl tartib',it)
# ---------- til: soʻz turkumlari / mavzular ----------
def themes(ix,nm,lang_q):
    # post_rasm.py dagi lugʻatdan (emoji soʻzlar) mavzu guruhlari
    src=open(os.path.join(H,'post_rasm.py'),encoding='utf-8').read()
    ns={};exec(src[src.index('C={'):src.index('L={')],ns);C=ns['C']
    cats=[('hayvon','meva','transport','kiyim','tabiat','ovqat')]
    names={'uz':{'hayvon':'Hayvonlar','meva':'Meva va sabzavotlar','transport':'Transport','kiyim':'Kiyim','tabiat':'Tabiat','ovqat':'Ovqat'},
           'en':{'hayvon':'Animals','meva':'Fruit and vegetables','transport':'Transport','kiyim':'Clothes','tabiat':'Nature','ovqat':'Food'},
           'ru':{'hayvon':'Животные','meva':'Фрукты и овощи','transport':'Транспорт','kiyim':'Одежда','tabiat':'Природа','ovqat':'Еда'}}[nm]
    keys=list(names);it=[]
    for d,n in ((1,2),(2,3),(3,4)):
        for _ in range(5):
            ks=pick(keys,n);it.append(round_(lang_q,[(names[k],[w[ix] for w in pick(C[k][2],3)]) for k in ks],d))
    return it
def lists_topic(id,name,sinf,q,lists,k):
    it=[]
    for d,n in ((1,2),(2,3),(3,3)):
        for _ in range(5):
            ks=pick(list(lists),n);it.append(round_(q,[(x,pick(lists[x],3 if d<3 else 4)) for x in ks],d))
    return topic(id,'Guruhlarga ajrat',name,sinf,k,it)
UZ={'Ot':K('kitob daftar maktab oʻquvchi stol uy daraxt qalam sinf bogʻ shahar qishloq ona doʻst non suv'),
    'Sifat':K('katta kichik chiroyli baland past yaxshi yomon oq qora qizil tez sekin issiq sovuq yangi eski'),
    'Feʼl':K('oʻqimoq yozmoq yugurmoq kulmoq ishlamoq oʻynamoq aytmoq koʻrmoq bormoq kelmoq uxlamoq yeb ichmoq sakramoq')}
UZ['Feʼl']=K('oʻqimoq yozmoq yugurmoq kulmoq ishlamoq oʻynamoq aytmoq koʻrmoq bormoq kelmoq uxlamoq sakramoq chizmoq')
UJ={'Jonli':K('bola oʻquvchi mushuk it qush baliq ot sigir daraxt gul'),'Jonsiz':K('stol kitob qalam uy maktab tosh daftar mashina'),}
UJ['Jonli']=K('bola oʻquvchi mushuk it qush baliq ot sigir ona oʻqituvchi');UJ['Jonsiz']=K('stol kitob qalam uy maktab tosh daftar mashina eshik deraza')
UN={'Unli harf':['a','e','i','o','u','oʻ'],'Undosh harf':['b','d','g','h','j','k','l','m','n','p','q','r','s','t','v','x','y','z','sh','ch']}
EN={'Noun':K('book table school teacher dog city river friend garden window'),'Verb':K('run read write play eat sleep swim sing open jump'),'Adjective':K('big small happy red fast tall cold new beautiful easy')}
RU={'Существительное':K('книга стол школа город река друг сад окно дорога урок'),'Глагол':K('читать писать бежать играть спать петь рисовать думать идти плавать'),'Прилагательное':K('большой красивый новый быстрый холодный добрый светлый тёплый умный лёгкий')}
RUG={'Мужской род':K('стол дом лес город брат мальчик самолёт урок'),'Женский род':K('книга школа сестра мама река дорога девочка вода'),'Средний род':K('окно море солнце дерево письмо поле облако яблоко')}
def build():
    out={}
    out['matematika']=mat_topics()
    out['ona-tili']=[lists_topic('g-turkum','🗂️ Ot, sifat, feʼl',[3,4,5],'Soʻzlarni turkumiga qarab ajrating',UZ,'ot sifat feʼl soʻz turkumi guruh'),
        lists_topic('g-jonli','🗂️ Jonli va jonsiz otlar',[3,4],'Otlarni guruhlarga ajrating',UJ,'jonli jonsiz ot guruh'),
        topic('g-harf','Guruhlarga ajrat','🗂️ Unli va undosh harflar',[1,2,3],'unli undosh harf guruh',[round_('Harflarni guruhlarga ajrating',[('Unli harf',pick(UN['Unli harf'],3 if d<3 else 4)),('Undosh harf',pick(UN['Undosh harf'],3 if d<3 else 5))],d) for d in (1,1,1,1,1,2,2,2,2,2,3,3,3,3,3)]),
        topic('g-mavzu','Guruhlarga ajrat','🗂️ Mavzularga ajrat: hayvon, meva, kiyim…',[1,2,3],'mavzu hayvon meva kiyim transport guruh',themes(3,'uz','Soʻzlarni mavzusiga qarab ajrating')),
        calendar_topic('uz')]
    out['ingliz']=[lists_topic('g-pos','🗂️ Noun, verb, adjective',[4,5,6],'Sort the words',EN,'noun verb adjective part of speech guruh'),
        topic('g-theme','Guruhlarga ajrat','🗂️ Themes: animals, food, clothes…',[2,3,4],'theme animal food clothes transport guruh',themes(1,'en','Sort the words by topic')),calendar_topic('en')]
    out['rus-tili']=[lists_topic('g-pos','🗂️ Существительное, глагол, прилагательное',[4,5,6],'Распределите слова по частям речи',RU,'часть речи существительное глагол прилагательное guruh'),
        lists_topic('g-rod','🗂️ Род имён существительных',[4,5],'Распределите слова по роду',RUG,'род мужской женский средний guruh'),
        topic('g-theme','Guruhlarga ajrat','🗂️ Темы: животные, одежда, еда…',[2,3,4],'тема животные одежда еда guruh',themes(2,'ru','Распределите слова по темам')),calendar_topic('ru')]
    return out
for slug,T in build().items():
    P=os.path.join(B,slug+'.json');j=json.load(open(P,encoding='utf-8'))
    ids={t['id'] for t in T};j['topics']=[t for t in j['topics'] if t['id'] not in ids]
    for t in T:
        if t['bob'] not in j['bolimlar']:j['bolimlar'].append(t['bob'])
        # xavfsizlik: har bir guruhli savolda soʻzlar takrorlanmasin
        for i in t['items']:
            if 'g' in i:
                seen=set()
                for g in i['g']:
                    g['w']=[w for w in g['w'] if not(w in seen or seen.add(w))]
        j['topics'].append(t)
    json.dump(j,open(P,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    print(slug,len(T),'mavzu,',sum(len(t['items']) for t in T),'savol')
