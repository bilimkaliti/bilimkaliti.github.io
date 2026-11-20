# -*- coding: utf-8 -*-
from ru_base import *

# ================= LUGʻAT: mavzular =================
vocab('r_oila', 'Семья — Oila', [5, 6, 7, 8], [('мама', 'ona'), ('папа', 'ota'), ('бабушка', 'buvi'), ('дедушка', 'bobo'), ('сын', 'oʻgʻil (farzand)'), ('дочь', 'qiz (farzand)'),
    ('внук', 'nevara (oʻgʻil)'), ('родители', 'ota-ona'), ('семья', 'oila'), ('брат', 'aka yoki uka'), ('сестра', 'opa yoki singil'), ('дядя', 'amaki yoki togʻa'), ('тётя', 'xola yoki amma'),
    ('муж', 'er'), ('жена', 'xotin'), ('ребёнок', 'bola (chaqaloq)'), ('двоюродный брат', 'amakivachcha (aka-uka)'), ('племянник', 'jiyan (oʻgʻil)')], 'семья family oila')

vocab('r_tana', 'Части тела — Tana aʼzolari', [5, 6, 7, 8], [('голова', 'bosh'), ('рука', 'qoʻl'), ('нога', 'oyoq'), ('глаз', 'koʻz'), ('ухо', 'quloq'), ('нос', 'burun'), ('рот', 'ogʻiz'),
    ('зуб', 'tish'), ('палец', 'barmoq'), ('спина', 'orqa (bel)'), ('живот', 'qorin'), ('шея', 'boʻyin'), ('плечо', 'yelka'), ('колено', 'tizza'), ('волосы', 'soch'), ('лицо', 'yuz'),
    ('сердце', 'yurak'), ('язык', 'til (ogʻizdagi)'), ('лоб', 'peshona'), ('щека', 'yonoq')], 'тело tana aʼzo')

vocab('r_zdorov', 'Здоровье — Salomatlik', [5, 6, 7, 8], [('врач', 'shifokor'), ('больница', 'kasalxona'), ('лекарство', 'dori'), ('температура', 'harorat (isitma)'), ('кашель', 'yoʻtal'), ('насморк', 'tumov'),
    ('боль', 'ogʻriq'), ('здоровье', 'salomatlik'), ('больной', 'kasal'), ('здоровый', 'sogʻlom'), ('аптека', 'dorixona'), ('болеть', 'ogʻrimoq / kasal boʻlmoq'), ('таблетка', 'tabletka'), ('горло', 'tomoq'),
    ('простуда', 'shamollash'), ('градусник', 'termometr (isitma oʻlchagich)'), ('рецепт', 'retsept'), ('поправляться', 'tuzalmoq')], 'здоровье salomatlik врач')

vocab('r_kasb', 'Профессии — Kasblar', [5, 6, 7, 8], [('врач', 'shifokor'), ('учитель', 'oʻqituvchi'), ('повар', 'oshpaz'), ('водитель', 'haydovchi'), ('строитель', 'quruvchi'), ('инженер', 'muhandis'),
    ('продавец', 'sotuvchi'), ('художник', 'rassom'), ('лётчик', 'uchuvchi'), ('полицейский', 'politsiyachi'), ('портной', 'tikuvchi (erkak)'), ('программист', 'dasturchi'), ('журналист', 'jurnalist'),
    ('парикмахер', 'sartarosh'), ('юрист', 'huquqshunos'), ('фермер', 'fermer'), ('пожарный', 'oʻt oʻchiruvchi'), ('музыкант', 'musiqachi'), ('актёр', 'aktyor'), ('бухгалтер', 'buxgalter')], 'профессия kasb')

vocab('r_kiyim', 'Одежда — Kiyim', [5, 6, 7, 8], [('рубашка', 'koʻylak (erkaklar)'), ('платье', 'koʻylak (ayollar)'), ('брюки', 'shim'), ('юбка', 'yubka'), ('куртка', 'kurtka'), ('пальто', 'palto'),
    ('шапка', 'bosh kiyim (shapka)'), ('шарф', 'sharf'), ('перчатки', 'qoʻlqop'), ('ботинки', 'botinka'), ('носки', 'paypoq'), ('футболка', 'futbolka'), ('свитер', 'sviter'),
    ('кроссовки', 'krossovka'), ('сапоги', 'etik'), ('костюм', 'kostyum'), ('пояс', 'belbogʻ'), ('халат', 'xalat'), ('тапочки', 'shippak')], 'одежда kiyim')

vocab('r_oziq', 'Фрукты, овощи и продукты — Meva, sabzavot, mahsulot', [5, 6, 7, 8], [('яблоко', 'olma'), ('груша', 'nok'), ('виноград', 'uzum'), ('арбуз', 'tarvuz'), ('дыня', 'qovun'), ('персик', 'shaftoli'),
    ('абрикос', 'oʻrik'), ('вишня', 'olcha'), ('апельсин', 'apelsin'), ('лимон', 'limon'), ('картофель', 'kartoshka'), ('морковь', 'sabzi'), ('лук', 'piyoz'), ('помидор', 'pomidor'),
    ('огурец', 'bodring'), ('капуста', 'karam'), ('чеснок', 'sarimsoq'), ('молоко', 'sut'), ('сыр', 'pishloq'), ('масло', 'yogʻ (sariyogʻ)'), ('яйцо', 'tuxum'), ('хлеб', 'non'),
    ('мясо', 'goʻsht'), ('сахар', 'shakar'), ('соль', 'tuz'), ('вода', 'suv'), ('чай', 'choy'), ('рис', 'guruch')], 'фрукты овощи продукты meva sabzavot')

vocab('r_rang', 'Цвета — Ranglar', [5, 6, 7, 8], [('красный', 'qizil'), ('синий', 'toʻq koʻk'), ('голубой', 'ochiq koʻk'), ('зелёный', 'yashil'), ('жёлтый', 'sariq'), ('чёрный', 'qora'), ('белый', 'oq'),
    ('оранжевый', 'toʻq sariq (zarg‘aldoq)'), ('коричневый', 'jigarrang'), ('розовый', 'pushti'), ('серый', 'kulrang'), ('фиолетовый', 'binafsha')], 'цвета ranglar')

vocab('r_uy', 'Дом и комната — Uy va xona', [5, 6, 7, 8], [('комната', 'xona'), ('кухня', 'oshxona'), ('ванная', 'hammom'), ('коридор', 'yoʻlak'), ('балкон', 'balkon'), ('кровать', 'karavot'),
    ('стол', 'stol'), ('стул', 'stul'), ('шкаф', 'shkaf'), ('диван', 'divan'), ('окно', 'deraza'), ('дверь', 'eshik'), ('ковёр', 'gilam'), ('лампа', 'chiroq (lampa)'), ('зеркало', 'oyna'),
    ('потолок', 'shift'), ('пол', 'pol'), ('стена', 'devor'), ('холодильник', 'muzlatgich'), ('лестница', 'zina'), ('крыша', 'tom'), ('подушка', 'yostiq')], 'дом комната uy xona мебель')

vocab('r_maktab', 'Школа — Maktab', [5, 6, 7, 8], [('класс', 'sinf'), ('урок', 'dars'), ('ученик', 'oʻquvchi'), ('парта', 'parta'), ('доска', 'doska'), ('мел', 'bur'), ('тетрадь', 'daftar'),
    ('ручка', 'ruchka'), ('карандаш', 'qalam'), ('линейка', 'chizgʻich'), ('портфель', 'portfel'), ('учебник', 'darslik'), ('перемена', 'tanaffus'), ('расписание', 'dars jadvali'), ('оценка', 'baho'),
    ('директор', 'direktor'), ('библиотека', 'kutubxona'), ('столовая', 'oshxona (maktabdagi)'), ('экзамен', 'imtihon'), ('домашнее задание', 'uy vazifasi'), ('ластик', 'oʻchirgʻich')], 'школа maktab урок')

vocab('r_fasl', 'Времена года, месяцы, погода — Fasllar, oylar, ob-havo', [5, 6, 7, 8], [('зима', 'qish'), ('весна', 'bahor'), ('лето', 'yoz'), ('осень', 'kuz'), ('январь', 'yanvar'), ('март', 'mart'),
    ('июнь', 'iyun'), ('сентябрь', 'sentabr'), ('ноябрь', 'noyabr'), ('снег', 'qor'), ('дождь', 'yomgʻir'), ('ветер', 'shamol'), ('солнце', 'quyosh'), ('облако', 'bulut'), ('туман', 'tuman'),
    ('мороз', 'qirov (qattiq sovuq)'), ('жара', 'jazirama issiq'), ('гроза', 'momaqaldiroq'), ('тепло', 'iliq'), ('холодно', 'sovuq'), ('лужа', 'kapchiq (suv toʻplanishi)')], 'времена года месяцы погода fasl oy')

vocab('r_transport', 'Транспорт — Transport', [5, 6, 7, 8], [('автобус', 'avtobus'), ('трамвай', 'tramvay'), ('троллейбус', 'trolleybus'), ('метро', 'metro'), ('поезд', 'poyezd'), ('самолёт', 'samolyot'),
    ('велосипед', 'velosiped'), ('машина', 'mashina'), ('такси', 'taksi'), ('пароход', 'paroxod'), ('вокзал', 'vokzal'), ('остановка', 'bekat'), ('билет', 'chipta'), ('аэропорт', 'aeroport'),
    ('пассажир', 'yoʻlovchi'), ('водитель', 'haydovchi'), ('мотоцикл', 'mototsikl'), ('вертолёт', 'vertolyot')], 'транспорт transport')

vocab('r_mamlakat', 'Страны и города — Mamlakatlar', [5, 6, 7, 8], [('Россия', 'Rossiya'), ('Узбекистан', 'Oʻzbekiston'), ('Казахстан', 'Qozogʻiston'), ('Китай', 'Xitoy'), ('Германия', 'Germaniya'),
    ('Франция', 'Fransiya'), ('Англия', 'Angliya'), ('Турция', 'Turkiya'), ('Япония', 'Yaponiya'), ('Индия', 'Hindiston'), ('Италия', 'Italiya'), ('Египет', 'Misr'), ('Ташкент', 'Toshkent'),
    ('Самарканд', 'Samarqand'), ('Москва', 'Moskva'), ('Европа', 'Yevropa'), ('Азия', 'Osiyo'), ('Африка', 'Afrika'), ('страна', 'mamlakat'), ('столица', 'poytaxt'), ('граница', 'chegara')], 'страны mamlakat')

vocab('r_hobbi', 'Хобби и спорт — Qiziqish va sport', [5, 6, 7, 8], [('футбол', 'futbol'), ('плавание', 'suzish'), ('шахматы', 'shaxmat'), ('рисование', 'rasm chizish'), ('чтение', 'oʻqish (kitob)'),
    ('музыка', 'musiqa'), ('танцы', 'raqs'), ('путешествие', 'sayohat'), ('игра', 'oʻyin'), ('бегать', 'yugurmoq'), ('прыгать', 'sakramoq'), ('петь', 'kuylamoq (qoʻshiq aytmoq)'), ('танцевать', 'raqsga tushmoq'),
    ('рисовать', 'rasm chizmoq'), ('плавать', 'suzmoq'), ('собирать', 'yigʻmoq (kolleksiya)'), ('тренировка', 'mashgʻulot'), ('команда', 'jamoa'), ('победа', 'gʻalaba'), ('чемпион', 'chempion')], 'хобби увлечения спорт')

vocab('r_kun', 'Мой день — Kun tartibi', [5, 6, 7, 8], [('вставать', 'turmoq (uyqudan)'), ('умываться', 'yuvinmoq'), ('завтракать', 'nonushta qilmoq'), ('обедать', 'tushlik qilmoq'), ('ужинать', 'kechki ovqat qilmoq'),
    ('делать уроки', 'uy vazifasini qilmoq'), ('ложиться спать', 'yotib uxlamoq'), ('утро', 'ertalab (tong)'), ('день', 'kun (kunduz)'), ('вечер', 'kechqurun'), ('ночь', 'tun'), ('будильник', 'budilnik'),
    ('чистить зубы', 'tish yuvmoq'), ('одеваться', 'kiyinmoq'), ('отдыхать', 'dam olmoq'), ('гулять', 'sayr qilmoq'), ('убирать', 'tozalamoq (yigʻishtirmoq)'), ('просыпаться', 'uygʻonmoq')], 'распорядок дня kun tartibi')

vocab('r_internet', 'Компьютер и интернет — Kompyuter va internet', [5, 6, 7, 8], [('компьютер', 'kompyuter'), ('ноутбук', 'noutbuk'), ('телефон', 'telefon'), ('клавиатура', 'klaviatura'), ('мышь', 'sichqoncha (kompyuter)'),
    ('экран', 'ekran'), ('интернет', 'internet'), ('сайт', 'sayt'), ('сообщение', 'xabar'), ('пароль', 'parol'), ('программа', 'dastur'), ('игра', 'oʻyin'), ('видео', 'video'), ('фото', 'surat (foto)'),
    ('скачать', 'yuklab olmoq'), ('искать', 'qidirmoq'), ('наушники', 'quloqchin'), ('зарядка', 'zaryadka (quvvatlagich)')], 'интернет компьютер internet')

vocab('r_hayvon', 'Животные и питомцы — Hayvonlar', [5, 6, 7, 8], [('собака', 'it'), ('кошка', 'mushuk'), ('попугай', 'toʻti'), ('хомяк', 'xomyak'), ('кролик', 'quyon'), ('рыбка', 'baliqcha'), ('корова', 'sigir'),
    ('лошадь', 'ot'), ('овца', 'qoʻy'), ('коза', 'echki'), ('курица', 'tovuq'), ('утка', 'oʻrdak'), ('гусь', 'gʻoz'), ('волк', 'boʻri'), ('лиса', 'tulki'), ('медведь', 'ayiq'), ('заяц', 'toʻshqon'),
    ('слон', 'fil'), ('лев', 'sher'), ('тигр', 'yoʻlbars'), ('обезьяна', 'maymun'), ('верблюд', 'tuya'), ('птица', 'qush'), ('питомец', 'uy hayvoni (asrab oluvchi)')], 'животные питомцы hayvon')

vocab('r_odob', 'Вежливые слова — Odob va muomala', [5, 6, 7, 8], [('здравствуйте', 'assalomu alaykum (salom)'), ('до свидания', 'xayr (koʻrishguncha)'), ('спасибо', 'rahmat'), ('пожалуйста', 'iltimos / marhamat'),
    ('извините', 'kechiring'), ('простите', 'uzr (kechirasiz)'), ('доброе утро', 'xayrli tong'), ('добрый день', 'xayrli kun'), ('добрый вечер', 'xayrli kech'), ('спокойной ночи', 'xayrli tun'),
    ('приятного аппетита', 'ishtaha ochilsin (yoqimli ishtaha)'), ('с днём рождения', 'tugʻilgan kuningiz bilan'), ('удачи', 'omad'), ('будьте добры', 'marhamat qiling (iltimos)'), ('очень приятно', 'tanishganimdan xursandman')], 'вежливые слова odob')

vocab('r_xarakter', 'Характер и чувства — Xarakter va his-tuygʻular', [6, 7, 8], [('добрый', 'mehribon'), ('злой', 'jahldor (yomon)'), ('весёлый', 'quvnoq'), ('грустный', 'xafa (qaygʻuli)'), ('смелый', 'jasur'),
    ('трусливый', 'qoʻrqoq'), ('ленивый', 'dangasa'), ('трудолюбивый', 'mehnatsevar'), ('умный', 'aqlli'), ('честный', 'halol (rostgoʻy)'), ('вежливый', 'odobli'), ('друг', 'doʻst'), ('дружба', 'doʻstlik'),
    ('радость', 'quvonch'), ('страх', 'qoʻrquv'), ('удивление', 'hayrat'), ('гордый', 'gʻururli'), ('скромный', 'kamtar')], 'характер дружба xarakter doʻstlik')
