// TransferWire Service Worker (19.11.2026, PWA): macht die App installierbar und zeigt ohne Netz eine Hinweisseite.
// Es wird NICHTS zwischengespeichert - keine Daten, keine App-Seite, keine Anmeldung. Alte Zwischenspeicher werden geloescht.
// Nur Seitenaufrufe (Navigation) laufen hier durch; schlaegt der Abruf fehl, kommt die Hinweisseite unten. Alles andere geht unveraendert ans Netz.
var OFFLINE = '<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="theme-color" content="#101012"><title>TransferWire</title>'
  + '<style>html,body{height:100%;margin:0}body{display:flex;align-items:center;justify-content:center;background:#101012;color:#EDEDED;font:400 16px/1.5 Inter,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;padding:24px;box-sizing:border-box;text-align:center}'
  + 'main{max-width:420px}h1{font:700 22px/1.25 Inter,system-ui,sans-serif;margin:0 0 10px}p{margin:0 0 22px;color:#B9BDC4}button{min-height:44px;padding:11px 22px;border:0;border-radius:10px;background:#C8A355;color:#1A1306;font:700 14px Inter,system-ui,sans-serif;cursor:pointer}button:focus-visible{outline:2px solid #fff;outline-offset:2px}</style></head>'
  + '<body><main><h1 id="t">Keine Verbindung</h1><p id="s">Bitte Internet prüfen. TransferWire braucht eine Verbindung.</p><button id="b" type="button">Erneut versuchen</button></main>'
  + '<script>(function(){var T={en:["No connection","Please check your internet. TransferWire needs a connection.","Try again"],es:["Sin conexión","Comprueba tu conexión a internet. TransferWire necesita conexión.","Reintentar"],fr:["Pas de connexion","Vérifiez votre connexion Internet. TransferWire a besoin d’une connexion.","Réessayer"],it:["Nessuna connessione","Controlla la connessione a Internet. TransferWire ha bisogno di una connessione.","Riprova"],pt:["Sem conexão","Verifique sua internet. O TransferWire precisa de conexão.","Tentar novamente"],tr:["Bağlantı yok","Lütfen internet bağlantınızı kontrol edin. TransferWire için bağlantı gerekir.","Tekrar dene"]};'
  + 'var l="";try{l=localStorage.getItem("tw_spr")||localStorage.getItem("tw_lang")||""}catch(e){}if(!l)l=String(navigator.language||"de").slice(0,2).toLowerCase();var x=T[l];if(x){document.documentElement.lang=l;document.getElementById("t").textContent=x[0];document.getElementById("s").textContent=x[1];document.getElementById("b").textContent=x[2]}'
  + 'document.getElementById("b").addEventListener("click",function(){location.reload()});window.addEventListener("online",function(){location.reload()})})();<\/script></body></html>';
self.addEventListener('install', function (e) { self.skipWaiting(); });
self.addEventListener('activate', function (e) {
  e.waitUntil((async function () {
    try { var ks = await caches.keys(); await Promise.all(ks.map(function (k) { return caches.delete(k); })); } catch (err) {}
    await self.clients.claim();
  })());
});
self.addEventListener('fetch', function (e) {
  if (e.request.mode !== 'navigate') return;
  e.respondWith(fetch(e.request).catch(function () {
    return new Response(OFFLINE, { status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' } });
  }));
});
