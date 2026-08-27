import json, time
from playwright.sync_api import sync_playwright
out = {}; fehler = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1600, "height": 950})
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de");')
    p = ctx.new_page(); p.on("pageerror", lambda e: fehler.append(str(e)[:150]))
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000); p.wait_for_timeout(5000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    p.locator(".tw-tabs button", has_text="Spieler").first.click(timeout=6000); p.wait_for_timeout(2500)
    p.locator(".tw-main input").first.fill("Han-Beom Lee"); p.wait_for_timeout(2500)
    p.locator(".tw-main tbody tr").first.click(timeout=8000); p.wait_for_timeout(2500)
    out["schnell"] = p.evaluate("() => { const t = document.body.innerText; const m = t.match(/Verein gepr[üu]ft am [^\\n]*/); return m ? m[0] : null; }")
    p.locator("button", has_text="Volles Profil").first.click(timeout=6000); p.wait_for_timeout(3000)
    out["profil"] = p.evaluate("() => { const t = document.body.innerText; const ms = t.match(/Verein gepr[üu]ft am [^\\n]*/g); return ms ? ms.length : 0; }")
    out["fehler"] = fehler[:3]
    print(json.dumps(out, ensure_ascii=False)); b.close()
