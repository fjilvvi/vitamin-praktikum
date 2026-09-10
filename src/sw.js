/* Витаминный практикум — офлайн-слой */
const VERSION = "__VERSION__";
const SHELL = "shell-" + VERSION;
const FONTS = "fonts-v1";
const ASSETS = [
  "./", "./index.html", "./manifest.webmanifest",
  "./icons/icon-192.png", "./icons/icon-512.png",
  "./icons/icon-maskable-512.png", "./icons/apple-touch-icon.png"
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(ASSETS)).catch(() => {}));
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map(k => (k.startsWith("shell-") && k !== SHELL) ? caches.delete(k) : null));
    await self.clients.claim();
  })());
});

self.addEventListener("message", e => {
  if (e.data && e.data.type === "SKIP_WAITING") self.skipWaiting();
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  // страница: сеть вперёд, кэш как запасной вариант — так обновления приходят сразу
  if (req.mode === "navigate"){
    e.respondWith((async () => {
      try{
        const fresh = await fetch(req);
        const c = await caches.open(SHELL);
        c.put("./index.html", fresh.clone());
        return fresh;
      }catch(err){
        const c = await caches.open(SHELL);
        return (await c.match("./index.html")) || (await c.match("./")) || Response.error();
      }
    })());
    return;
  }

  // шрифты Google: сначала кэш, обновляем в фоне
  if (url.hostname.endsWith("googleapis.com") || url.hostname.endsWith("gstatic.com")){
    e.respondWith((async () => {
      const c = await caches.open(FONTS);
      const hit = await c.match(req);
      const net = fetch(req).then(res => { c.put(req, res.clone()).catch(() => {}); return res; }).catch(() => hit);
      return hit || net;
    })());
    return;
  }

  // свои файлы: сначала кэш
  if (url.origin === location.origin){
    e.respondWith((async () => {
      const c = await caches.open(SHELL);
      const hit = await c.match(req, { ignoreSearch:true });
      if (hit) return hit;
      try{
        const res = await fetch(req);
        if (res.ok) c.put(req, res.clone()).catch(() => {});
        return res;
      }catch(err){ return Response.error(); }
    })());
  }
});
