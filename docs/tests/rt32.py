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
    p.wait_for_timeout(6000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    feed = p.evaluate("() => { const f = document.querySelector('.tw-feedlist') || document.querySelector('.tw-main'); const rels = [...f.querySelectorAll('.tw-rel')]; const words = {}; rels.forEach(r => { const w = (r.innerText||'').trim(); words[w] = (words[w]||0) + 1; }); return { karten: f.querySelectorAll('.tw-card').length, rel: rels.length, woerter: words, tooltip: rels[0] ? rels[0].getAttribute('title') : null, konkret: f.innerText.includes('Konkret'), warnchip: f.innerText.includes('⚠'), badges: [...new Set([...f.querySelectorAll('.tw-card span')].filter(s => getComputedStyle(s).borderRadius === '999px' && s.innerText.trim().length < 20).map(s => s.innerText.trim()))].slice(0,12) }; }")
    out["feed"] = feed
    # Meldungspanel oeffnen
    try:
        p.locator(".tw-feedlist .tw-card h3, .tw-feedlist .tw-card h2, .tw-feedlist .tw-card [class*='headline']").first.click(timeout=5000)
    except Exception:
        p.locator(".tw-feedlist .tw-card").first.click(timeout=5000)
    p.wait_for_timeout(1500)
    out["panel"] = p.evaluate("() => { const els = [...document.querySelectorAll('div')].filter(d => getComputedStyle(d).position === 'fixed' && d.innerText.includes('Belastbarkeit')); const d = els[0]; if (!d) return 'KEIN PANEL'; const t = d.innerText; return { belastbarkeit_feld: t.includes('Belastbarkeit'), verlaesslichkeit_alt: t.includes('Verlässlichkeit'), warnchip: t.includes('⚠'), rel_kopf: d.querySelectorAll('.tw-rel').length, kopf: t.split('\\n').slice(0, 6).join(' | ').slice(0, 160) }; }")
    p.keyboard.press("Escape"); p.wait_for_timeout(500); p.mouse.click(5, 300); p.wait_for_timeout(500)
    # Vereinsbedarf
    try:
        p.locator(".tw-tabs button", has_text="Vereinsbedarf").first.click(timeout=6000); p.wait_for_timeout(4000)
        out["bedarf"] = p.evaluate("() => { const m = document.querySelector('.tw-main'); return { rel: m.querySelectorAll('.tw-rel').length, konkret: m.innerText.includes('Konkret') }; }")
    except Exception as e: out["bedarf"] = str(e)[:80]
    # Englisch
    try:
        p.evaluate("() => __twToggleLang('en')"); p.wait_for_timeout(1500)
        p.locator(".tw-tabs button", has_text="Feed").first.click(timeout=6000); p.wait_for_timeout(3000)
        out["en"] = p.evaluate("() => { const f = document.querySelector('.tw-feedlist') || document.querySelector('.tw-main'); const rels = [...f.querySelectorAll('.tw-rel')]; const words = {}; rels.forEach(r => { const w = (r.innerText||'').trim(); words[w] = (words[w]||0) + 1; }); return { woerter: words, tooltip: rels[0] ? rels[0].getAttribute('title') : null, deutsch: /Unbestätigt|Belastbar|Bestätigt|Spekulation/.test(f.innerText) }; }")
        p.evaluate("() => __twToggleLang('de')"); p.wait_for_timeout(500)
    except Exception as e: out["en"] = str(e)[:100]
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
