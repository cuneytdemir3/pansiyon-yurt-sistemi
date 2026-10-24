const CACHE_NAME = 'sbl-pansiyon-v1';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Basit pass-through fetch: PWA yüklenebilirliği için SW şarttır.
  // Çevrimdışı önbellekleme karmaşıklığını önlemek için daima network'ten çeker.
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});