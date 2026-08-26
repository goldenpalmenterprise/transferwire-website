import json, time
from playwright.sync_api import sync_playwright
out = {}
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1600, "height": 950})
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de");')
    p = ctx.new_page()
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000)
    p.wait_for_timeout(5000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    p.locator(".tw-tabs button", has_text="Transfers").first.click(timeout=6000); p.wait_for_timeout(4500)
    out["zeile"] = p.evaluate("() => (document.querySelector('.tw-main').innerText.match(/\\d+ Meldungen · aktualisiert [^\\n]*/) || [''])[0]")
    out["chips"] = p.evaluate("() => [...document.querySelectorAll('.tw-gchips button')].map(b => b.innerText.replace(/\\n/g,' '))")
    out["signalzeile"] = p.evaluate("() => { const r = document.querySelector('.tw-main article .tw-rel'); return r ? r.innerText.replace(/\\s+/g, ' ').trim() : null; }")
    print(json.dumps(out, ensure_ascii=False))
    b.close()
