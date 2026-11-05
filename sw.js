/* OVERSOUND – app installabile: il sito si apre anche con connessione debole.
   Pagine: prima dalla rete (sempre aggiornate), se manca la rete dalla copia salvata.
   Librerie e icone: dalla copia salvata. Prezzi, ordini e account (gestionale): sempre dalla rete. */
const V = 'oversound-v3', BASE = ['/', '/index.html', '/manifest.webmanifest', '/icone/logo.webp', '/icone/app-192.png', '/icone/app-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(V).then(c => c.addAll(BASE)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== V).map(x => caches.delete(x)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.pathname.startsWith('/api/') || u.hostname.endsWith('pythonanywhere.com')) return;   // dati veri: mai dalla copia
  if (r.mode === 'navigate' || (u.origin === location.origin && u.pathname.endsWith('.html'))) {
    e.respondWith(fetch(r).then(res => { const c = res.clone(); caches.open(V).then(x => x.put('/index.html', c)); return res; })
      .catch(() => caches.match('/index.html').then(x => x || caches.match('/')))); return;
  }
  if (/cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net|fonts\.(googleapis|gstatic)\.com/.test(u.hostname) || (u.origin === location.origin && u.pathname.startsWith('/icone/'))) {
    e.respondWith(caches.match(r).then(x => x || fetch(r).then(res => { if (res.ok || res.type === 'opaque') { const c = res.clone(); caches.open(V).then(z => z.put(r, c)); } return res; })));
  }
});
