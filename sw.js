/* Bilim Kaliti — service worker (ilova rejimi uchun).
   Sahifalar va oʻyinlar: avval internetdan (har doim yangi versiya), internet boʻlmasa — saqlangan nusxa.
   Rasmlar va shriftlar: saqlangan nusxa darhol, orqada yangilanadi.
   Saytni yangilaganda shu yerdagi VERSION raqamini oshirish shart emas — sahifalar baribir internetdan olinadi. */
const VERSION = 'bk-v60';
const CORE = [
  '/',
  '/index.html',
  '/fx.css',
  '/fx.js',
  '/manifest.webmanifest',
  '/ikonka.png',
  '/icon-192.png',
  '/icon-512.png',
  '/games/grades.json',
  '/games/sets.json',
  '/games/baza/matematika.json',
  '/games/baza/ona-tili.json',
  '/games/baza/ingliz.json',
  '/games/baza/rus-tili.json',
  '/games/bilim.html',
  '/games/eshik-kodi.html',
  '/games/kosmik-baza.html',
  '/games/sirli-xonalar.html',
  '/games/toplam.html',
  '/games/diplom.js'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(VERSION)
      .then(c => Promise.all(CORE.map(u => c.add(new Request(u, { cache: 'reload' })).catch(() => {}))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Shriftlar, Telegram skripti va kutubxonalar ham saqlanadi — internet uzilsa ham ishlaydi
const FONT_HOSTS = ['fonts.googleapis.com', 'fonts.gstatic.com', 'telegram.org', 'cdn.jsdelivr.net', 'cdnjs.cloudflare.com'];

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;               // API (POST) soʻrovlariga tegmaymiz
  const url = new URL(req.url);
  const same = url.origin === self.location.origin;
  if (!same && !FONT_HOSTS.includes(url.hostname)) return; // boshqa saytlar — oddiy yoʻl bilan

  const isPage = req.mode === 'navigate' || /\.(html|json|webmanifest)$/.test(url.pathname) || url.pathname.endsWith('/');
  if (same && isPage) {
    e.respondWith(networkFirst(req));
  } else {
    e.respondWith(staleWhileRevalidate(req));
  }
});

async function networkFirst(req) {
  const cache = await caches.open(VERSION);
  try {
    // no-cache: brauzer keshidagi eski nusxa emas, har doim yangisi (ETag bilan tez tekshiriladi)
    const res = await fetch(new Request(req.url, { cache: 'no-cache', credentials: 'same-origin' }));
    if (res && res.ok) cache.put(stripQuery(req), res.clone());
    return res;
  } catch (err) {
    const hit = await cache.match(stripQuery(req), { ignoreSearch: true });
    if (hit) return hit;
    if (req.mode === 'navigate') {
      const home = await cache.match('/', { ignoreSearch: true });
      if (home) return home;
    }
    return new Response('Internet yoʻq', { status: 503, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
  }
}

async function staleWhileRevalidate(req) {
  const cache = await caches.open(VERSION);
  const hit = await cache.match(req);
  const net = fetch(req).then(res => {
    if (res && (res.ok || res.type === 'opaque')) cache.put(req, res.clone());
    return res;
  }).catch(() => null);
  return hit || (await net) || new Response('', { status: 504 });
}

function stripQuery(req) {
  const u = new URL(req.url);
  if (!u.search) return req;
  return new Request(u.origin + u.pathname);
}
