// Pokopia 材料单 Service Worker —— 离线缓存 app shell
const CACHE = 'pokopia-v1';
const SHELL = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './icon-maskable-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  // cache-first：离线版所有资源已内联，命中缓存即秒开
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request)
        .then(resp => {
          // 仅缓存同源成功响应
          if (resp && resp.ok && new URL(event.request.url).origin === self.location.origin) {
            const copy = resp.clone();
            caches.open(CACHE).then(c => c.put(event.request, copy));
          }
          return resp;
        })
        .catch(() => caches.match('./index.html'));
    })
  );
});
