# Yangi fan bazasini qoʻshish

1. `games/baza/<slug>.json` yarating (masalan `tarix.json`). Tuzilishi `ingliz.json` kabi:
   `{"fan":"Tarix","slug":"tarix","v":1,"bolimlar":[...],"topics":[{"id","bob","name","sinf":[..],"k","items":[...]}]}`
2. Savol turlari (hammasi ixtiyoriy, bor turdagi oʻyinlar avtomatik ochiladi):
   - test: `{"q","o":[..4 ta..],"c":indeks,"d":1|2|3}` — hamma test oʻyinlari, Bomba (variant raqami sim boʻladi), Anagram (javob bir soʻz boʻlsa), Juftlash
   - tartib: `{"q","s":[soʻzlar toʻgʻri tartibda],"d"}` — «Tartibga sol»
   - guruh: `{"q","g":[{"n":"nomi","w":[soʻzlar]},..],"d"}` — «Guruhlarga ajrat»
3. `python3 -c "import sys;sys.path.insert(0,'src_baza');import common;common.update_version()"` — `games/kinds.json` va versiya yangilanadi.
4. `sw.js` dagi VERSION raqamini oshiring. Boshqa hech narsa oʻzgartirilmaydi: fan roʻyxatlari, mavzular va oʻyinlar roʻyxati kinds.json asosida oʻzi paydo boʻladi.
