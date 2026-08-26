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
    p.wait_for_timeout(5000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    p.locator(".tw-tabs button", has_text="Vertragsenden").first.click(timeout=6000); p.wait_for_selector(".tw-vttable", timeout=40000); p.wait_for_timeout(3000)
    out["filter"] = p.evaluate("""() => { const f = document.querySelector('.tw-vtfilter'); const t = f.innerText; return { input: (f.querySelector('input')||{}).placeholder, selects: [...f.querySelectorAll('select')].map(s => s.options[0].text), treffer: (t.match(/[\\d.]+ Verträge/)||[''])[0], sortierung: [...f.querySelectorAll('select')].slice(-1)[0].options.length, hoehe: Math.round(f.querySelector('select').getBoundingClientRect().height), positionen_tabelle: [...new Set([...document.querySelectorAll('.tw-vttable tbody tr')].map(r => r.children[2].innerText.trim()))] }; }""")
    def setSel(idx, val):
        p.evaluate("([i, v]) => { const s = document.querySelectorAll('.tw-vtfilter select')[i]; s.value = v; s.dispatchEvent(new Event('change', { bubbles: true })); }", [idx, val]); p.wait_for_timeout(500)
    setSel(0, "frei")
    out["status_frei"] = p.evaluate("() => ({ zeilen: document.querySelectorAll('.tw-vttable tbody tr').length, alle_frei: [...document.querySelectorAll('.tw-vttable tbody tr')].every(r => /Vertragslos/.test(r.innerText)), treffer: (document.querySelector('.tw-vtfilter').innerText.match(/\\d+ Vertr[aä]ge?/)||[''])[0], reset: document.querySelector('.tw-vtfilter').innerText.includes('Filter zurücksetzen (1)') })")
    setSel(0, "alle"); setSel(1, "Mittelfeld")
    out["pos"] = p.evaluate("() => ({ zeilen: document.querySelectorAll('.tw-vttable tbody tr').length, alle_mf: [...document.querySelectorAll('.tw-vttable tbody tr')].every(r => r.children[2].innerText.trim() === 'Mittelfeld') })")
    setSel(1, ""); setSel(4, "vorhanden")
    out["mw"] = p.evaluate("() => ({ zeilen: document.querySelectorAll('.tw-vttable tbody tr').length, alle_mw: [...document.querySelectorAll('.tw-vttable tbody tr')].every(r => /Mio\\. €|Tsd\\. €/.test(r.children[6].innerText)) })")
    p.locator(".tw-vtfilter input").fill("xyzq-nichts"); p.wait_for_timeout(500)
    out["keine"] = p.evaluate("() => document.querySelector('.tw-main').innerText.includes('Keine Verträge für diese Filter')")
    p.locator(".tw-vtfilter button", has_text="Filter zurücksetzen").first.click(timeout=5000); p.wait_for_timeout(500)
    out["reset"] = p.evaluate("() => ({ zeilen: document.querySelectorAll('.tw-vttable tbody tr').length, input: document.querySelector('.tw-vtfilter input').value })")
    # Sortierung Marktwert
    p.evaluate("() => { const s = [...document.querySelectorAll('.tw-vtfilter select')].slice(-1)[0]; s.value = 'mw'; s.dispatchEvent(new Event('change', { bubbles: true })); }"); p.wait_for_timeout(500)
    out["sort_mw"] = p.evaluate("() => [...document.querySelectorAll('.tw-vttable tbody tr')].slice(0, 3).map(r => r.children[6].innerText.trim())")
    p.set_viewport_size({"width": 390, "height": 800}); p.wait_for_timeout(1200)
    out["mobil"] = p.evaluate("() => { const f = document.querySelector('.tw-vtfilter'); return { da: !!f, passt: [...f.querySelectorAll('select, input')].every(e => e.getBoundingClientRect().right <= 392), karten: document.querySelectorAll('.tw-main .tw-card').length }; }")
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
