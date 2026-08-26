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
    out["feed"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const t = m.innerText; const sel = [...m.querySelectorAll('select')]; return { kasten: t.includes('Verein gezielt suchen'), selects: sel.map(s => ({ n: s.options.length, erste: s.options[0] ? s.options[0].text : '', disabled: s.disabled })), reihenfolge: ['ALLE', 'Verein gezielt suchen', 'Alle Meldungen', 'MEISTDISKUTIERTE VEREINE'].map(x => t.indexOf(x)), karten_vorher: m.querySelectorAll('.tw-card').length }; }""")
    # Kaskade bedienen: Land -> Liga -> Verein
    sels = p.locator(".tw-main select")
    p.evaluate("() => { const s = document.querySelectorAll('.tw-main select')[0]; const o = [...s.options].find(x => /England/i.test(x.text)) || s.options[1]; s.value = o.value; s.dispatchEvent(new Event('change', { bubbles: true })); }"); p.wait_for_timeout(500)
    p.evaluate("() => { const s = document.querySelectorAll('.tw-main select')[1]; const o = [...s.options].find(x => /Premier League/i.test(x.text)) || s.options[1]; s.value = o.value; s.dispatchEvent(new Event('change', { bubbles: true })); }"); p.wait_for_timeout(500)
    p.evaluate("() => { const s = document.querySelectorAll('.tw-main select')[2]; const o = [...s.options].find(x => /Manchester United/i.test(x.text)) || s.options[1]; s.value = o.value; s.dispatchEvent(new Event('change', { bubbles: true })); }"); p.wait_for_timeout(800)
    out["gefiltert"] = p.evaluate("() => { const m = document.querySelector('.tw-main'); const t = m.innerText; return { land: document.querySelectorAll('.tw-main select')[0].value, liga: document.querySelectorAll('.tw-main select')[1].value, verein: document.querySelectorAll('.tw-main select')[2].value, hinweis: (t.match(/Gefiltert nach[^\\n]*/)||[''])[0], karten: m.querySelectorAll('.tw-card').length, chip_aktiv: !!m.querySelector('.tw-feedfilter button[style*=\"rgb(15, 21, 32)\"]') }; }")
    # Zuruecksetzen
    p.locator(".tw-main button", has_text="Zurücksetzen").first.click(timeout=5000); p.wait_for_timeout(600)
    out["reset"] = p.evaluate("() => ({ verein: document.querySelectorAll('.tw-main select')[2].value, karten: document.querySelectorAll('.tw-main .tw-card').length })")
    # Merkliste: Kasten nicht dort
    p.locator(".tw-tabs button", has_text="Merkliste").first.click(timeout=6000); p.wait_for_timeout(1500)
    out["merkliste_ohne_kasten"] = p.evaluate("() => !document.querySelector('.tw-main').innerText.includes('Verein gezielt suchen')")
    p.set_viewport_size({"width": 390, "height": 800}); p.locator(".tw-tabs button", has_text="Newsfeed").first.click(timeout=6000); p.wait_for_timeout(1500)
    out["mobil"] = p.evaluate("() => { const m = document.querySelector('.tw-main'); const sel = [...m.querySelectorAll('select')]; return { kasten: m.innerText.includes('Verein gezielt suchen'), selects_breite: sel.map(s => Math.round(s.getBoundingClientRect().width)), passt: sel.every(s => s.getBoundingClientRect().right <= 392) }; }")
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
