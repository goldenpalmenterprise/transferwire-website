import json, time, re
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
    out["tabs"] = p.evaluate("() => [...document.querySelectorAll('.tw-tabs button')].map(b => b.innerText.trim())")
    p.locator(".tw-tabs button", has_text="Transfers").first.click(timeout=6000); p.wait_for_timeout(4000)
    out["vor_klick"] = p.evaluate("() => { const a = document.querySelector('.tw-main article'); return { artikel: document.querySelectorAll('.tw-main article').length, cursor: a ? getComputedStyle(a).cursor : null, kopf: a ? a.innerText.split('\\n').slice(0,3).join(' | ').slice(0,100) : null }; }")
    p.evaluate("() => { const a = [...document.querySelectorAll('.tw-main article')].find(x => x.querySelector('.tw-rel')); if (a) a.click(); }")
    p.wait_for_timeout(1800)
    out["nach_klick"] = p.evaluate("() => { const fixed = [...document.querySelectorAll('div')].filter(d => getComputedStyle(d).position === 'fixed' && d.innerText.trim().length > 40); return { belastbarkeit_im_body: document.body.innerText.includes('Belastbarkeit'), verlaesslichkeit_im_body: document.body.innerText.includes('Verlässlichkeit'), warnchip: document.body.innerText.includes('⚠'), fixed: fixed.map(d => d.innerText.replace(/\\n+/g,' | ').slice(0, 120)).slice(0, 3), rel_in_fixed: fixed.map(d => d.querySelectorAll('.tw-rel').length), pills_in_fixed: fixed.map(d => [...d.querySelectorAll('span')].filter(s => getComputedStyle(s).borderRadius === '999px').map(s => s.innerText.trim()).slice(0,3)) }; }")
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
