/* Bilim Kaliti — oʻyin oxirida chop etiladigan diplom.
   Har bir oʻyin sahifasiga <script src="diplom.js" defer></script> qoʻshiladi.
   Natija oynasi (#final yoki #end) ochilganda unga «🏅 Diplom» tugmasi qoʻshiladi. */
(function () {
  if (window.__bkDiplom) return; window.__bkDiplom = 1;
  var LS = { get: function (k, d) { try { var v = localStorage.getItem(k); return v == null ? d : v } catch (e) { return d } },
             set: function (k, v) { try { localStorage.setItem(k, v) } catch (e) {} } };
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c] }) }

  var css = '' +
    '.bkd-btn{margin:10px auto 0;display:inline-flex;align-items:center;gap:8px;border:0;border-radius:14px;padding:12px 22px;font:inherit;font-weight:900;font-size:1.05rem;cursor:pointer;background:linear-gradient(135deg,#ffd54a,#f5a300);color:#2a1d00;box-shadow:0 6px 18px rgba(245,163,0,.35)}' +
    '.bkd-btn:hover{filter:brightness(1.05)}' +
    '#bkdOv{position:fixed;inset:0;z-index:99999;background:rgba(10,14,30,.72);display:flex;flex-direction:column;align-items:center;justify-content:flex-start;overflow:auto;padding:18px 10px 30px;font-family:Nunito,system-ui,sans-serif}' +
    '#bkdOv .bar{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-bottom:12px}' +
    '#bkdOv .bar button{border:0;border-radius:12px;padding:11px 20px;font:inherit;font-weight:900;cursor:pointer;background:#fff;color:#16213e}' +
    '#bkdOv .bar .p{background:#f5b301;color:#1b1400}' +
    '#bkdOv .hint{color:#dfe3f5;font-weight:700;font-size:.9rem;margin:-4px 0 12px;text-align:center}' +
    '.bkd{width:min(1000px,96vw);aspect-ratio:297/210;background:#fffdf6;color:#1d2340;position:relative;border-radius:6px;box-shadow:0 20px 60px rgba(0,0,0,.45);overflow:hidden;font-family:Nunito,system-ui,sans-serif;container-type:inline-size}' +
    '.bkd .fr{position:absolute;inset:2.2cqw;border:.5cqw solid #d9a400;border-radius:1cqw}' +
    '.bkd .fr2{position:absolute;inset:3.3cqw;border:.18cqw solid #d9a400;border-radius:.6cqw}' +
    '.bkd .cn{position:absolute;width:7cqw;height:7cqw;font-size:5cqw;display:grid;place-items:center}' +
    '.bkd .rib{position:absolute;left:0;right:0;top:0;height:1.6cqw;background:linear-gradient(90deg,#3b2a8c,#7048e8,#3b2a8c)}' +
    '.bkd .rib.b{top:auto;bottom:0}' +
    '.bkd .in{position:absolute;inset:4.6cqw 10cqw 4.8cqw;display:flex;flex-direction:column;align-items:center;text-align:center}' +
    '.bkd .cup{font-size:6.5cqw;line-height:1}' +
    '.bkd h1{margin:.6cqw 0 0;font-size:7.4cqw;letter-spacing:1.2cqw;color:#b07d00;font-weight:900;text-shadow:0 .25cqw 0 #ffe7a1}' +
    '.bkd .sub{font-size:2.3cqw;font-weight:900;color:#3b2a8c;letter-spacing:.35cqw;text-transform:uppercase;margin-top:.3cqw}' +
    '.bkd .to{font-size:1.9cqw;color:#5b6283;margin-top:2.2cqw;font-weight:700}' +
    '.bkd .nm{font-size:5cqw;font-weight:900;color:#1d2340;margin-top:.4cqw;min-width:40cqw;border-bottom:.2cqw dashed #c9c2ae;padding:0 2cqw .3cqw;outline:none}' +
    '.bkd .why{font-size:2.15cqw;color:#2d3456;margin-top:1.8cqw;max-width:72cqw;line-height:1.35;font-weight:700;outline:none}' +
    '.bkd .ft{margin-top:auto;width:100%;display:flex;justify-content:space-between;align-items:flex-end;font-size:1.6cqw;color:#5b6283;font-weight:700}' +
    '.bkd .ft>div:not(.seal){width:26cqw;text-align:center}' +
    '.bkd .ft .ln{border-top:.15cqw solid #1d2340;padding-top:.5cqw;margin-top:2.5cqw;outline:none}' +
    '.bkd .seal{flex:none;width:11cqw;height:11cqw;border-radius:50%;background:radial-gradient(circle at 35% 30%,#ffe58a,#f0b000 60%,#b77f00);display:grid;place-items:center;color:#5a3d00;font-weight:900;font-size:1.35cqw;line-height:1.15;box-shadow:0 .4cqw 1cqw rgba(0,0,0,.2);border:.35cqw dotted #fff4c4}' +
    '.bkd .brand{position:absolute;bottom:0;left:0;right:0;height:1.6cqw;line-height:1.6cqw;text-align:center;font-size:1.1cqw;color:#fff;font-weight:800;letter-spacing:.1cqw}' +
    '[contenteditable]:hover{background:rgba(245,179,1,.10)}' +
    '@media print{@page{size:A4 landscape;margin:0}html,body{background:#fff!important}body>*:not(#bkdOv){display:none!important}' +
    '#bkdOv{position:static;background:none;padding:0;display:block;overflow:visible}#bkdOv .bar,#bkdOv .hint{display:none!important}' +
    '.bkd{width:297mm;height:210mm;aspect-ratio:auto;box-shadow:none;border-radius:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}[contenteditable]:hover{background:none}}';

  function addCss() { if (document.getElementById('bkdCss')) return; var s = document.createElement('style'); s.id = 'bkdCss'; s.textContent = css; document.head.appendChild(s) }

  function gameName() {
    var t = document.getElementById('ttl'), n = t && t.textContent.trim();
    if (!n) n = (document.title || '').split('—')[0].trim();
    return n.replace(/^[^\wА-Яа-яЎўҚқҒғҲҳʻʼ'"«]+/, '').trim() || 'Bilim Kaliti';
  }
  function winnerFrom(text) {
    text = (text || '').trim();
    var m;
    if (/Robo yutdi/i.test(text)) return '';
    if ((m = text.match(/Gʻolib:\s*(.+?)(?:\s+—|$)/))) return m[1].trim();
    if ((m = text.match(/^🏆\s*(.+?)\s+gʻolib/))) return m[1].trim();
    if ((m = text.match(/^Durang:\s*(.+?)(?:\s+—|$)/))) return m[1].trim();
    return '';
  }
  function today() { var d = new Date(); function p(x) { return (x < 10 ? '0' : '') + x } return p(d.getDate()) + '.' + p(d.getMonth() + 1) + '.' + d.getFullYear() }

  function openDiplom(box) {
    addCss();
    var title = box.querySelector('#winTitle,#endT,h2');
    var who = winnerFrom(title && title.textContent);
    var game = gameName();
    var why = '«' + game + '» oʻyinida ' + (who ? 'birinchi oʻrinni egallagani' : 'faol ishtirok etib, yuqori natija koʻrsatgani') + ', bilimi, diqqati va jamoaviy ruhi uchun taqdirlanadi.';
    var teacher = LS.get('bk_teacher', '');
    var school = LS.get('bk_school', '');
    var ov = document.createElement('div'); ov.id = 'bkdOv';
    ov.innerHTML =
      '<div class="bar"><button class="p" data-a="print">🖨 Chop etish / PDF</button><button data-a="close">✕ Yopish</button></div>' +
      '<div class="hint">✏️ Matnni bosib oʻzgartirishingiz mumkin: ism, sabab, maktab va oʻqituvchi.</div>' +
      '<div class="bkd">' +
        '<div class="rib"></div><div class="rib b"></div><div class="fr"></div><div class="fr2"></div>' +
        '<div class="cn" style="left:3.3cqw;top:3.3cqw">⭐</div><div class="cn" style="right:3.3cqw;top:3.3cqw">⭐</div>' +
        '<div class="cn" style="left:3.3cqw;bottom:3.3cqw">🌟</div><div class="cn" style="right:3.3cqw;bottom:3.3cqw">🌟</div>' +
        '<div class="in">' +
          '<div class="cup">🏆</div><h1>DIPLOM</h1><div class="sub">Sinf chempioni</div>' +
          '<div class="to">Ushbu diplom</div>' +
          '<div class="nm" contenteditable="true" data-k="nm">' + esc(who || 'Ism Familiya') + '</div>' +
          '<div class="why" contenteditable="true">' + esc(why) + '</div>' +
          '<div class="ft">' +
            '<div><div contenteditable="true" data-k="school">' + esc(school || 'Maktab, sinf') + '</div><div class="ln">Sana: ' + today() + '</div></div>' +
            '<div class="seal">BILIM<br>KALITI<br>🔑</div>' +
            '<div><div contenteditable="true" data-k="teacher">' + esc(teacher || 'Oʻqituvchi F.I.Sh.') + '</div><div class="ln">Imzo</div></div>' +
          '</div>' +
        '</div>' +
        '<div class="brand">bilimkaliti.github.io</div>' +
      '</div>';
    document.body.appendChild(ov);
    var nm = ov.querySelector('[data-k="nm"]');
    if (!who) { setTimeout(function () { nm.focus(); try { document.execCommand('selectAll', false, null) } catch (e) {} }, 50) }
    ov.addEventListener('input', function (e) {
      var k = e.target.getAttribute && e.target.getAttribute('data-k');
      if (k === 'teacher') LS.set('bk_teacher', e.target.textContent.trim());
      if (k === 'school') LS.set('bk_school', e.target.textContent.trim());
    });
    ov.addEventListener('click', function (e) {
      var a = e.target.getAttribute && e.target.getAttribute('data-a');
      if (a === 'close' || e.target === ov) ov.remove();
      if (a === 'print') {
        if (document.activeElement) document.activeElement.blur();
        try { window.print() } catch (err) { alert('Chop etish uchun brauzer menyusidan «Chop etish» ni tanlang.') }
      }
    });
  }

  function attach(box) {
    if (!box || box.querySelector('.bkd-btn')) return;
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'bkd-btn'; b.textContent = '🏅 Diplom';
    b.addEventListener('click', function () { openDiplom(box) });
    var card = box.querySelector('.modal,.endc,.endcard') || box;
    var btns = card.querySelector('.mbtns,.ebtn');
    if (btns) { btns.insertBefore(b, btns.firstChild); b.style.margin = '0' }
    else { var again = card.querySelector('#againBtn,#again,button'); if (again && again.parentNode === card) card.insertBefore(b, again); else card.appendChild(b); var w = document.createElement('div'); b.parentNode.insertBefore(w, b.nextSibling) }
  }

  function init() {
    addCss();
    ['final', 'end'].forEach(function (id) {
      var el = document.getElementById(id); if (!el) return;
      attach(el);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
