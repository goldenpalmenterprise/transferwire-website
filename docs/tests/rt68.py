import json, time
from playwright.sync_api import sync_playwright
out = {}; fehler = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1600, "height": 950})
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de");')
    p = ctx.new_page(); p.on("pageerror", lambda e: fehler.append(str(e)[:160]))
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000); p.wait_for_timeout(7000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    out["register"] = p.evaluate("() => ({ geladen: TW_QV.geladen, hosts: Object.keys(TW_QV.host).length, namen: Object.keys(TW_QV.name).length, kicker: TW_QV.host['kicker.de'] || null, bbc: TW_QV.host['bbc.co.uk'] || TW_QV.host['bbc.com'] || null, thesun: TW_QV.host['thesun.co.uk'] || null })")
    out["feed"] = p.evaluate("""() => { const rel = [...document.querySelectorAll('.tw-main .tw-rel')].map(e => e.innerText.trim()); return { rel_gesamt: rel.length, bestaetigt: rel.filter(x => x.startsWith('✓')).length, unbestaetigt_fix: rel.filter(x => /Als fix gemeldet/.test(x)).length, mit_stufe: rel.filter(x => /\\((A1|A2|B|C|D) ·/.test(x)).length, beispiele: [...new Set(rel)].slice(0, 6) }; }""")
    p.locator(".tw-main button", has_text="FIXER DEAL").first.click(timeout=5000); p.wait_for_timeout(1500)
    out["fix"] = p.evaluate("""() => { const rel = [...document.querySelectorAll('.tw-main .tw-rel')].map(e => e.innerText.trim()); return { karten: rel.length, bestaetigt: rel.filter(x => x.startsWith('✓')).length, unbestaetigt: rel.filter(x => /Als fix gemeldet/.test(x)).length, beispiel_unbest: rel.find(x => /Als fix gemeldet/.test(x)) || null, beispiel_best: rel.find(x => x.startsWith('✓')) || null }; }""")
    out["fehler"] = fehler[:3]
    print(json.dumps(out, ensure_ascii=False)); b.close()
