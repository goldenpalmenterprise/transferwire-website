import json, time
from playwright.sync_api import sync_playwright
out = {}; fehler = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1600, "height": 950})
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de");')
    p = ctx.new_page()
    p.on("pageerror", lambda e: fehler.append("PE: " + str(e)[:200]))
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000)
    p.wait_for_timeout(5000)
    p.locator(".tw-tabs button", has_text="Scouting").first.click(timeout=6000); p.wait_for_timeout(1500)
    p.locator(".tw-main button", has_text="Scouting-Listen").first.click(timeout=6000)
    p.wait_for_selector(".tw-likarte", timeout=30000); p.wait_for_timeout(1000)
    p.locator(".tw-likarte button", has_text="Liste öffnen").first.click(timeout=5000)
    p.wait_for_function("() => { const t = document.querySelector('.tw-main').innerText; return t.includes('← Alle Listen') && !/^[^\\n]*\\n[^\\n]*…/.test(t) && document.querySelectorAll('.tw-main img').length > 3; }", timeout=30000); p.wait_for_timeout(1000)
    out["liste"] = p.evaluate("() => { const t = document.querySelector('.tw-main').innerText; return { kopf: t.split('\\n').slice(0, 6).join(' | '), bilder: document.querySelectorAll('.tw-main img').length, treffer: (t.match(/TW Performance Score|\\d+ Min/g)||[]).length }; }")
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
