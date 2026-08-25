import json, time, re
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
    # Transfers & Geruechte -> Karte -> Meldungspanel
    try:
        p.locator(".tw-tabs button", has_text="Transfers").first.click(timeout=6000); p.wait_for_timeout(4000)
        out["transfers"] = p.evaluate("() => { const m = document.querySelector('.tw-main'); return { karten: m.querySelectorAll('.tw-card').length, rel: m.querySelectorAll('.tw-rel').length }; }")
        p.locator(".tw-main .tw-card").first.click(timeout=6000); p.wait_for_timeout(1500)
        out["panel"] = p.evaluate("() => { const els = [...document.querySelectorAll('div')].filter(d => getComputedStyle(d).position === 'fixed' && /Belastbarkeit|Quellen|Verl\\u00e4sslichkeit/.test(d.innerText)); const d = els[0]; if (!d) return 'KEIN PANEL'; const t = d.innerText; return { feld_belastbarkeit: t.includes('Belastbarkeit'), alt_verlaesslichkeit: t.includes('Verlässlichkeit'), warnchip: t.includes('⚠'), rel_kopf: d.querySelectorAll('.tw-rel').length, badge_kopf: [...d.querySelectorAll('span')].filter(s => getComputedStyle(s).borderRadius === '999px').map(s => s.innerText.trim()).slice(0,3), kopf: t.split('\\n').slice(0, 5).join(' | ').slice(0, 140) }; }")
        p.keyboard.press("Escape"); p.wait_for_timeout(400); p.mouse.click(5, 400); p.wait_for_timeout(500)
    except Exception as e: out["panel"] = str(e)[:120]
    # Vereinsbedarf -> Position waehlen -> NeedCards
    try:
        p.locator(".tw-tabs button", has_text="Vereinsbedarf").first.click(timeout=6000); p.wait_for_timeout(4000)
        p.locator(".tw-main .tw-tile").first.click(timeout=6000); p.wait_for_timeout(3000)
        out["bedarf"] = p.evaluate("() => { const m = document.querySelector('.tw-main'); const rels = [...m.querySelectorAll('.tw-rel')]; return { needcards: m.querySelectorAll('article').length, rel: rels.length, woerter: [...new Set(rels.map(r => r.innerText.trim()))].slice(0,6), badge: [...m.querySelectorAll('article span')].filter(s => getComputedStyle(s).borderRadius === '999px').map(s => s.innerText.trim()).slice(0,3) }; }")
    except Exception as e: out["bedarf"] = str(e)[:120]
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
