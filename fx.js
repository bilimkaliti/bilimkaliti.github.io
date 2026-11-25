/* Orqaga: oʻyindan kelgan sahifaga qaytish (boʻlmasa — Oʻyinlar) */
window.BKLEAVE=function(){var home=location.pathname.replace(/games\/[^\/]*$/,'')+'#/oyinlar',d=(history.state&&history.state.bkd)||0,ok=false;
 try{var u=new URL(document.referrer);ok=u.origin===location.origin&&!/\/games\//.test(u.pathname)}catch(e){}
 if(ok&&history.length>d+1)history.go(-(d+1));else location.href=home};
/* Bilim Kaliti — umumiy effektlar: silkinish, sakrash, ball "pop", postament, Robo-doʻst, tilt, oʻchirgich */
(function(){
 var ST=function(){try{return localStorage.getItem('bk_fx')}catch(e){return null}};
 var RMq=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
 var on=ST()==='1'?true:ST()==='0'?false:!RMq;
 var H=document.documentElement,isGame=/\/games\//.test(location.pathname);
 function apply(){H.classList.toggle('nofx',!on);var b=document.getElementById('fxBtn');if(b)b.textContent=on?'✨ Effekt: yoqiq':'💤 Effekt: oʻchiq';
  document.querySelectorAll('.fxlink').forEach(function(x){x.textContent=on?'✨ Animatsiya: yoqiq':'💤 Animatsiya: oʻchiq'})}
 function set(v){on=v;try{localStorage.setItem('bk_fx',v?'1':'0')}catch(e){}apply()}
 apply();
 function re(el,c,ms){if(!on||!el)return;el.classList.remove(c);void el.offsetWidth;el.classList.add(c);setTimeout(function(){el.classList.remove(c)},ms||700)}
 var EM=['✨','⭐','🎉','💫'],SAD=['💭'];
 function spark(el,n,list){if(!on||!el||!el.animate)return;requestAnimationFrame(function(){sp2(el,n,list)})}
 function sp2(el,n,list){var r=el.getBoundingClientRect();if(!r.width)return;
  for(var i=0;i<n;i++){var e=document.createElement('span');e.className='fxp';e.textContent=list[i%list.length];
   var x=r.left+r.width/2,y=r.top+r.height/2,a=Math.random()*Math.PI*2,d=40+Math.random()*60;
   document.body.appendChild(e);
   var an=e.animate([{transform:'translate('+x+'px,'+y+'px) scale(.4)',opacity:1},{transform:'translate('+(x+Math.cos(a)*d)+'px,'+(y+Math.sin(a)*d-30)+'px) scale(1.1)',opacity:1,offset:.6},{transform:'translate('+(x+Math.cos(a)*d*1.2)+'px,'+(y+Math.sin(a)*d+20)+'px) scale(.6)',opacity:0}],{duration:800+Math.random()*400,easing:'ease-out'});
   an.onfinish=(function(n){return function(){n.remove()}})(e)}}
 /* Robo-doʻst (faqat oʻyinlarda) */
 var bot=null,botT=0;
 function mkBot(){if(bot||!isGame)return;bot=document.createElement('div');bot.id='fxBot';bot.innerHTML='🤖<b></b>';bot.setAttribute('aria-hidden','true');
  bot.onclick=function(){botSay('Omad! 💪','happy')};document.body.appendChild(bot)}
 function botSay(t,k){if(!bot||!on)return;var b=bot.querySelector('b');b.textContent=t;bot.classList.remove('happy','sad');void bot.offsetWidth;bot.classList.add(k);bot.classList.add('say');
  clearTimeout(botT);botT=setTimeout(function(){bot.classList.remove('say','happy','sad')},1500)}
 var GOOD=['Barakalla! 👏','Ofarin! 🌟','Zoʻr! 🔥','Ajoyib! 🎉'],BAD=['Hechqisi yoʻq 🙂','Yana urinib koʻring','Eʻtibor bering 🤔'];
 var pick=function(a){return a[Math.floor(Math.random()*a.length)]};
 function panelOf(el){return el.closest('.pn,.tp,.team,.panel')||el.parentElement}
 function onMsg(el){var c=el.classList;
  if(c.contains('good')){var p=panelOf(el);re(p,'fx-pulse',500);re(p,'fx-glowg',700);spark(el,8,EM);botSay(pick(GOOD),'happy')}
  else if(c.contains('bad')){var p2=panelOf(el);re(p2,'fx-shake',500);re(p2,'fx-glowr',600);botSay(pick(BAD),'sad')}}
 /* podium */
 function podium(box){if(!box||box.querySelector('.fx-pod'))return;var rows=[];
  if(box.id==='res'){box.querySelectorAll(':scope>div').forEach(function(d){var s=d.querySelector('span'),b=d.querySelector('b');if(s&&b)rows.push({n:s.textContent.replace(/^[^\p{L}\p{N}]+/u,'').trim(),s:+b.textContent,c:d.style.getPropertyValue('--tc')})})}
  else{box.querySelectorAll(':scope>div').forEach(function(d){var n=d.querySelector('b'),p=d.querySelector('.pts');if(n&&p)rows.push({n:n.textContent.trim(),s:+p.textContent,c:d.style.getPropertyValue('--tc')})})}
  if(rows.length<2||rows[0].s<=0)return;rows.sort(function(a,b){return b.s-a.s});
  var med=['🥇','🥈','🥉'],rk=[],pl=0,prev=null;rows.forEach(function(r,i){if(r.s!==prev){pl=i+1;prev=r.s}r.p=pl});
  var top=rows.filter(function(r){return r.p<=3}).slice(0,3),h='';
  top.forEach(function(r){var esc=function(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})};
   h+='<div class="fpc p'+r.p+'"><span class="fpm">'+med[r.p-1]+'</span><span class="fpn" style="color:'+(r.c||'inherit')+'">'+esc(r.n)+'</span><div class="fpb">'+r.s+'</div></div>'});
  box.insertAdjacentHTML('beforebegin','<div class="fx-pod" aria-hidden="true">'+h+'</div>');
  var cup=box.closest('.endc,.modal');if(cup){var c=cup.querySelector('.cup')||cup.querySelector('div[style*="font-size:3rem"]');if(c){c.classList.add('fx-cup');c.style.fontSize=''}}
  setTimeout(function(){var e=document.querySelector('.fx-pod .p1');if(e)spark(e,14,['🎉','⭐','✨','🏆'])},1300)}
 function clean(){document.querySelectorAll('.fx-pod').forEach(function(x){x.remove()})}
 /* kuzatuvchi */
 function watch(){
  var mo=new MutationObserver(function(ms){ms.forEach(function(m){var t=m.target;
   if(m.type==='attributes'){
    if(t.classList.contains('msg')&&(t.classList.contains('good')||t.classList.contains('bad')))onMsg(t);
    else if((t.id==='end'||t.id==='final')){if(t.classList.contains('hidden'))clean();else setTimeout(function(){podium(document.getElementById(t.id==='end'?'res':'rank'))},60)}}
   else if(m.type==='childList'||m.type==='characterData'){var e=t.nodeType===3?t.parentElement:t;
    if(e&&e.id==='scores'){var bs=e.querySelectorAll('b'),cur=[].map.call(bs,function(b){return b.textContent});(window.__fxSc||[]).forEach(function(v,i){if(cur[i]!==undefined&&cur[i]!==v)re(bs[i],'fx-pop',550)});window.__fxSc=cur;return}
    if(!e||!e.closest)return;var s=e.closest('#scores b,.th .sc,.hsc');if(s&&s===e&&m.addedNodes.length+(m.type==='characterData'?1:0)>0)re(s,'fx-pop',550)}})});
  mo.observe(document.body,{subtree:true,attributes:true,attributeFilter:['class'],childList:true,characterData:true})}
 /* hero tilt (bosh sahifa) */
 var raf=0;
 document.addEventListener('mousemove',function(e){if(!on||isGame||raf)return;raf=requestAnimationFrame(function(){raf=0;var b=document.querySelector('.hero .board');if(!b)return;
  var r=b.getBoundingClientRect();if(r.bottom<0||r.top>innerHeight)return;var x=(e.clientX-(r.left+r.width/2))/innerWidth,y=(e.clientY-(r.top+r.height/2))/innerHeight;
  b.style.setProperty('--ry',(x*14).toFixed(2)+'deg');b.style.setProperty('--rx',(-y*10).toFixed(2)+'deg')})},{passive:true});
 document.addEventListener('mouseleave',function(){var b=document.querySelector('.hero .board');if(b){b.style.setProperty('--rx','0deg');b.style.setProperty('--ry','0deg')}});
 document.addEventListener('click',function(e){var l=e.target.closest&&e.target.closest('.fxlink');if(l)set(!on)});
 function init(){if(isGame){mkBot();var b=document.createElement('button');b.id='fxBtn';b.type='button';b.onclick=function(){set(!on)};document.body.appendChild(b)}apply();watch()}
 /* yangi savol paydo boʻlganda — 3D aylanib kirish (matn oʻzgargandagina, qayta chizishda emas) */
 var QSEL='.stmt,.ttq,.qc,.qtxt,.card .q,.mo,.mq,.mn';var LAST=new WeakMap();
 function qin(el){if(!on||!el.animate||RMQ())return;var txt=(el.textContent||'').trim().slice(0,160),par=el.parentNode;if(!par)return;
   var key=par.__bkq||(par.__bkq={});var cls=el.className&&String(el.className).split(' ')[0];if(key[cls]===txt)return;key[cls]=txt;
   el.animate([{opacity:0,transform:'perspective(700px) rotateX(-55deg) translateY(-10px) scale(.96)'},{opacity:1,transform:'perspective(700px) rotateX(6deg)',offset:.7},{opacity:1,transform:'none'}],{duration:520,easing:'cubic-bezier(.25,1.1,.4,1)'})}
 function RMQ(){try{return matchMedia('(prefers-reduced-motion: reduce)').matches}catch(e){return false}}
 function qwatch(){if(!isGame||!window.MutationObserver)return;new MutationObserver(function(ms){ms.forEach(function(m){m.addedNodes&&m.addedNodes.forEach(function(n){if(n.nodeType!==1)return;
   if(n.matches&&n.matches(QSEL))qin(n);n.querySelectorAll&&Array.prototype.forEach.call(n.querySelectorAll(QSEL),qin)})})}).observe(document.body,{childList:true,subtree:true})}
 if(document.body)qwatch();else document.addEventListener('DOMContentLoaded',qwatch);
 window.BKFX={spark:spark,shake:function(e){re(e,'fx-shake',500)},pop:function(e){re(e,'fx-pop',550)},get on(){return on},set:set};
 if(document.body)init();else document.addEventListener('DOMContentLoaded',init);
})();
