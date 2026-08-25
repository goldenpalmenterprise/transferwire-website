import json, time
from playwright.sync_api import sync_playwright
out = {}
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1845, "height": 700})
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de");')
    p = ctx.new_page()
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000)
    p.wait_for_timeout(6000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    out["layout"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const cs = getComputedStyle(m); const kids = [...m.children].map(k => { const r = k.getBoundingClientRect(); return { tag: k.tagName, cls: k.className, x: Math.round(r.left), w: Math.round(r.width), y: Math.round(r.top), h: Math.round(r.height), col: getComputedStyle(k).gridColumnStart + '/' + getComputedStyle(k).gridColumnEnd, leer: k.children.length === 0 }; });
      const fl = document.querySelector('.tw-feedlist'); const a = m.querySelector('aside');
      return { mainClass: m.className, cols: cs.gridTemplateColumns, display: cs.display, kids: kids, feedlist: fl ? { x: Math.round(fl.getBoundingClientRect().left), w: Math.round(fl.getBoundingClientRect().width), parentTag: fl.parentElement.tagName, parentCls: fl.parentElement.className, cols: getComputedStyle(fl).gridTemplateColumns } : null, aside: a ? { x: Math.round(a.getBoundingClientRect().left), w: Math.round(a.getBoundingClientRect().width), y: Math.round(a.getBoundingClientRect().top), pos: getComputedStyle(a).position, kinder: a.children.length, text: a.innerText.slice(0, 60) } : null, live: (document.body.innerText.match(/LIVE[^\\n]{0,40}/) || [''])[0] }; }""")
    print(json.dumps(out, ensure_ascii=False))
    b.close()
