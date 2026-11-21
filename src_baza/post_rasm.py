# Rasmli (emoji) soʻz savollari: ingliz, rus, ona tili bazalariga "Rasmli soʻzlar" mavzulari qoʻshadi. Takror ishga tushirish xavfsiz.
import json,os,random
H=os.path.dirname(os.path.abspath(__file__));B=os.path.join(H,'..','games','baza')
# (emoji, en, ru, uz)
C={
'hayvon':('Hayvonlar','🐾',[('🐶','dog','собака','it'),('🐱','cat','кошка','mushuk'),('🐭','mouse','мышь','sichqon'),('🐰','rabbit','кролик','quyon'),('🦊','fox','лиса','tulki'),('🐻','bear','медведь','ayiq'),('🐼','panda','панда','panda'),('🐯','tiger','тигр','yoʻlbars'),('🦁','lion','лев','sher'),('🐮','cow','корова','sigir'),('🐷','pig','свинья','choʻchqa'),('🐸','frog','лягушка','baqa'),('🐵','monkey','обезьяна','maymun'),('🐔','chicken','курица','tovuq'),('🐧','penguin','пингвин','pingvin'),('🐦','bird','птица','qush'),('🦆','duck','утка','oʻrdak'),('🦉','owl','сова','boyqush'),('🐺','wolf','волк','boʻri'),('🐴','horse','лошадь','ot'),('🐝','bee','пчела','asalari'),('🦋','butterfly','бабочка','kapalak'),('🐢','turtle','черепаха','toshbaqa'),('🐍','snake','змея','ilon'),('🐙','octopus','осьминог','sakkizoyoq'),('🐟','fish','рыба','baliq'),('🐬','dolphin','дельфин','delfin'),('🐘','elephant','слон','fil'),('🐪','camel','верблюд','tuya'),('🦒','giraffe','жираф','jirafa'),('🐑','sheep','овца','qoʻy'),('🐐','goat','коза','echki'),('🦅','eagle','орёл','burgut')]),
'meva':('Meva va sabzavotlar','🍎',[('🍎','apple','яблоко','olma'),('🍌','banana','банан','banan'),('🍇','grapes','виноград','uzum'),('🍉','watermelon','арбуз','tarvuz'),('🍊','orange','апельсин','apelsin'),('🍋','lemon','лимон','limon'),('🍓','strawberry','клубника','qulupnay'),('🍒','cherry','вишня','olcha'),('🍑','peach','персик','shaftoli'),('🍐','pear','груша','nok'),('🍍','pineapple','ананас','ananas'),('🥕','carrot','морковь','sabzi'),('🍅','tomato','помидор','pomidor'),('🥔','potato','картофель','kartoshka'),('🌽','corn','кукуруза','makkajoʻxori'),('🥒','cucumber','огурец','bodring'),('🍆','eggplant','баклажан','baqlajon'),('🧅','onion','лук','piyoz'),('🧄','garlic','чеснок','sarimsoq')]),
'ovqat':('Ovqat va ichimliklar','🍞',[('🍞','bread','хлеб','non'),('🧀','cheese','сыр','pishloq'),('🥚','egg','яйцо','tuxum'),('🍕','pizza','пицца','pitsa'),('🍰','cake','торт','tort'),('🍪','cookie','печенье','pechenye'),('🍫','chocolate','шоколад','shokolad'),('🍬','candy','конфета','konfet'),('🥛','milk','молоко','sut'),('☕','coffee','кофе','qahva'),('🍯','honey','мёд','asal'),('🥄','spoon','ложка','qoshiq')]),
'transport':('Transport','🚗',[('🚗','car','машина','mashina'),('🚌','bus','автобус','avtobus'),('🚲','bicycle','велосипед','velosiped'),('✈️','plane','самолёт','samolyot'),('🚂','train','поезд','poyezd'),('🚢','ship','корабль','kema'),('🚁','helicopter','вертолёт','vertolyot'),('🚀','rocket','ракета','raketa'),('🚕','taxi','такси','taksi'),('🚜','tractor','трактор','traktor'),('🏍️','motorcycle','мотоцикл','mototsikl')]),
'kiyim':('Kiyim va buyumlar','👕',[('👕','shirt','футболка','futbolka'),('👖','jeans','джинсы','jinsi'),('👗','dress','платье','koʻylak'),('🧦','socks','носки','paypoq'),('🧢','cap','кепка','kepka'),('🧣','scarf','шарф','sharf'),('🧤','gloves','перчатки','qoʻlqop'),('👓','glasses','очки','koʻzoynak'),('👜','bag','сумка','sumka'),('🎩','hat','шляпа','shlyapa'),('👑','crown','корона','toj'),('☂️','umbrella','зонт','soyabon')]),
'tabiat':('Tabiat','🌳',[('☀️','sun','солнце','quyosh'),('🌙','moon','луна','oy'),('⭐','star','звезда','yulduz'),('☁️','cloud','облако','bulut'),('🌧️','rain','дождь','yomgʻir'),('❄️','snow','снег','qor'),('🌈','rainbow','радуга','kamalak'),('🔥','fire','огонь','olov'),('🌊','wave','волна','toʻlqin'),('🌳','tree','дерево','daraxt'),('🌸','flower','цветок','gul'),('🍄','mushroom','гриб','qoʻziqorin'),('⛰️','mountain','гора','togʻ')]),
'buyum':('Maktab va uy buyumlari','📚',[('📚','books','книги','kitoblar'),('✏️','pencil','карандаш','qalam'),('🖊️','pen','ручка','ruchka'),('✂️','scissors','ножницы','qaychi'),('🎒','backpack','рюкзак','ryukzak'),('⏰','clock','часы','soat'),('🔑','key','ключ','kalit'),('💡','lamp','лампа','lampochka'),('📱','phone','телефон','telefon'),('💻','computer','компьютер','kompyuter'),('📷','camera','фотоаппарат','fotoapparat'),('⚽','ball','мяч','toʻp'),('🎸','guitar','гитара','gitara'),('🎹','piano','пианино','pianino'),('🪑','chair','стул','stul'),('🛏️','bed','кровать','yotoq'),('🚪','door','дверь','eshik'),('🪟','window','окно','deraza'),('🎁','gift','подарок','sovgʻa'),('🏠','house','дом','uy'),('🏫','school','школа','maktab'),('🔨','hammer','молоток','bolgʻa')]),
'tana':('Tana aʼzolari','👁️',[('👁️','eye','глаз','koʻz'),('👂','ear','ухо','quloq'),('👃','nose','нос','burun'),('👄','mouth','рот','ogʻiz'),('✋','hand','рука','qoʻl'),('🦷','tooth','зуб','tish'),('🧠','brain','мозг','miya'),('❤️','heart','сердце','yurak')]),
}
L={'ingliz':(1,'What is it?','Bu rasm qaysi soʻz?',[2,3,4]),'rus-tili':(2,'Что на картинке?','Rasmda nima bor?',[2,3,4]),'ona-tili':(3,'Rasmga mos soʻzni toping','Rasmga mos soʻzni toping',[1,2,3])}
BOB='Rasmli soʻzlar'
random.seed(7)
for slug,(ix,_,prompt,sinf) in L.items():
    P=os.path.join(B,slug+'.json');j=json.load(open(P,encoding='utf-8'))
    j['topics']=[t for t in j['topics'] if not t['id'].startswith('rasm-')]
    if BOB not in j['bolimlar']:j['bolimlar'].append(BOB)
    for cid,(cname,ic,words) in C.items():
        W=[(w[0],w[ix]) for w in words]
        items=[]
        for e,w in W:
            others=[x[1] for x in W if x[1]!=w];random.shuffle(others)
            o=others[:3]+[w];random.shuffle(o)
            n=len(w.replace(' ',''));d=1 if n<=4 else 2 if n<=7 else 3
            items.append({'q':f'{e}  {prompt}','o':o,'c':o.index(w),'d':d})
        j['topics'].append({'id':'rasm-'+cid,'bob':BOB,'name':f'{ic} Rasmli soʻzlar: {cname.lower()}','sinf':sinf,'k':'rasm emoji soʻz lugʻat '+cname.lower(),'items':items})
    json.dump(j,open(P,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    print(slug,len([t for t in j['topics'] if t['id'].startswith('rasm-')]))
