import json, time
from playwright.sync_api import sync_playwright
out = {}; fehler = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1845, "height": 800})
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de");')
    p = ctx.new_page()
    p.on("pageerror", lambda e: fehler.append("PE: " + str(e)[:200]))
    p.on("console", lambda m: fehler.append("CE: " + m.text[:200]) if m.type == "error" and "Failed to load resource" not in m.text else None)
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000)
    p.wait_for_timeout(6000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    out["feed"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const a = m.querySelector('aside'); const ff = m.querySelector('.tw-feedfilter'); const cards = [...m.querySelectorAll('article.tw-card')].slice(0, 2).map(c => { const r = c.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.width)]; });
      const ueberlappt = (() => { if (!a || getComputedStyle(a).display === 'none') return false; const ar = a.getBoundingClientRect(); return [...m.querySelectorAll('article.tw-card')].some(c => { const r = c.getBoundingClientRect(); return r.right > ar.left + 2 && r.top < ar.bottom && r.bottom > ar.top; }); })();
      return { cols: getComputedStyle(m).gridTemplateColumns, aside_sichtbar: a ? getComputedStyle(a).display !== 'none' && a.children.length > 0 : false, ueberlappung: ueberlappt, filterzeile: ff ? { y: Math.round(ff.getBoundingClientRect().top), h: Math.round(ff.getBoundingClientRect().height), text: ff.innerText.replace(/\\n+/g, ' | ').slice(0, 160), chips: ff.querySelectorAll('button').length } : null, karten: cards, live: (document.body.innerText.match(/LIVE[^\\n]{0,30}/) || [''])[0] }; }""")
    # Vereins-Chip klicken -> Filter aktiv -> zuruecksetzen
    try:
        p.locator(".tw-feedfilter button").first.click(timeout=5000); p.wait_for_timeout(1200)
        out["chip"] = p.evaluate("() => { const ff = document.querySelector('.tw-feedfilter'); const b = ff.querySelector('button'); return { aktiv_bg: getComputedStyle(b).backgroundColor, reset_da: ff.innerText.includes('Zurücksetzen'), karten: document.querySelectorAll('.tw-main article.tw-card').length }; }")
        p.locator(".tw-feedfilter button", has_text="Zurücksetzen").first.click(timeout=5000); p.wait_for_timeout(800)
        out["reset"] = p.evaluate("() => ({ karten: document.querySelectorAll('.tw-main article.tw-card').length, reset_weg: !document.querySelector('.tw-feedfilter').innerText.includes('Zurücksetzen') })")
    except Exception as e: out["chip"] = str(e)[:100]
    # Mobil
    p.set_viewport_size({"width": 390, "height": 800}); p.wait_for_timeout(1000)
    out["mobil"] = p.evaluate("() => { const ff = document.querySelector('.tw-feedfilter'); const r = ff ? ff.getBoundingClientRect() : null; return r ? { w: Math.round(r.width), h: Math.round(r.height), passt: r.right <= innerWidth + 1 } : null; }")
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
