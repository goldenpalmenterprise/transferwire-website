import json, time
from playwright.sync_api import sync_playwright
out = {}; fehler = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1600, "height": 950})
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de"); localStorage.setItem("tw_watch", JSON.stringify({asked: true, items: [{t:"spieler", w:"Luís Asué"}, {t:"spieler", w:"Cole Palmer"}, {t:"verein", w:"Manchester United"}]}));')
    p = ctx.new_page()
    p.on("pageerror", lambda e: fehler.append("PE: " + str(e)[:200]))
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000)
    p.wait_for_timeout(5000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    p.locator(".tw-tabs button", has_text="Merkliste").first.click(timeout=6000)
    p.wait_for_function("() => { const rs = [...document.querySelectorAll('.tw-mkrow')]; return rs.length >= 2 && rs.every(r => !/…/.test(r.innerText)); }", timeout=30000); p.wait_for_timeout(6000)
    out["zeilen"] = p.evaluate("() => [...document.querySelectorAll('.tw-mkrow')].map(r => r.innerText.replace(/\\n/g,' | ').slice(0, 200))")
    out["tabs"] = p.evaluate("() => [...document.querySelectorAll('.tw-mktabs button')].map(b => b.innerText.replace(/\\n/g,' '))")
    p.locator(".tw-mktabs button", has_text="Vereine").first.click(timeout=5000); p.wait_for_timeout(600)
    out["vereine"] = p.evaluate("() => [...document.querySelectorAll('.tw-mkrow')].map(r => r.innerText.replace(/\\n/g,' | ').slice(0, 160))")
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
