import json, time
from playwright.sync_api import sync_playwright
out = {}; fehler = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1600, "height": 950})
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de");')
    p = ctx.new_page()
    p.on("pageerror", lambda e: fehler.append("PE: " + str(e)[:200]))
    p.on("console", lambda m: fehler.append("CE: " + m.text[:200]) if m.type == "error" and "Failed to load resource" not in m.text else None)
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000)
    p.wait_for_timeout(6000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    out["live"] = p.evaluate("() => { const t = document.querySelector('header').innerText; return { text: (t.match(/● LIVE[^\\n|]*/)||[''])[0], doppelt: (t.match(/LIVE/g)||[]).length }; }")
    out["sidebar"] = p.evaluate("() => { const a = document.querySelector('.tw-main aside') || document.querySelector('.tw-main'); const t = a.innerText; const m = t.match(/Meistdiskutierte Vereine[\\s\\S]{0,400}?Gespeicherte Filter/); return { block: m ? m[0].replace(/\\n+/g,' | ').slice(0,300) : 'nicht gefunden', leer: t.includes('Noch keine gespeicherten Filter') }; }")
    out["karten"] = p.evaluate("""() => { const cards = [...document.querySelectorAll('.tw-feedlist .tw-card')].slice(0, 6); const hs = cards.map(c => c.getBoundingClientRect().height); const rows = {}; cards.forEach(c => { const y = Math.round(c.getBoundingClientRect().top); (rows[y] = rows[y] || []).push(Math.round(c.getBoundingClientRect().height)); }); return { heights: Object.values(rows).slice(0,3), unbestaetigt: document.querySelector('.tw-feedlist').innerText.includes('UNBESTÄTIGT'), jPlatzhalter: /·\\s*J\\.?\\s*·/.test(document.querySelector('.tw-feedlist').innerText), pfeilAlt: (document.querySelector('.tw-feedlist').innerText.match(/↗/g)||[]).length, watchPill: document.querySelector('.tw-feedlist').innerText.includes('Beobachten'), logos: document.querySelectorAll('.tw-feedlist .tw-route-club').length, vertragslos: document.querySelector('.tw-feedlist').innerText.includes('Vertragslos'), bookmark: document.querySelectorAll('.tw-feedlist button[title]').length }; }""")
    out["fehler"] = fehler[:4]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
