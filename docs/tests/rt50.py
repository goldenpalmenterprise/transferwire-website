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
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    p.locator(".tw-tabs button", has_text="Performance").first.click(timeout=6000); p.wait_for_timeout(7000)
    btn = p.get_by_role("button", name="Wie wird der Score berechnet?")
    btn.click(timeout=5000); p.wait_for_timeout(700)
    out["sofort"] = p.evaluate("() => { const d = document.querySelector('[role=dialog]'); return d ? { text: d.innerText.replace(/\\n/g,' | ').slice(0, 60), sichtbar: getComputedStyle(d).visibility === 'visible' } : 'KEIN POPOVER'; }")
    p.keyboard.press("Escape"); p.wait_for_timeout(300)
    btn.scroll_into_view_if_needed(); p.wait_for_timeout(900); btn.click(timeout=5000); p.wait_for_timeout(700)
    out["nach_scroll"] = p.evaluate("() => !!document.querySelector('[role=dialog]')")
    p.mouse.wheel(0, 200); p.wait_for_timeout(500)
    out["scroll_schliesst"] = p.evaluate("() => !document.querySelector('[role=dialog]')")
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
