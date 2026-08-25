import json, time
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
    main = lambda: p.evaluate("() => (document.querySelector('.tw-main')||document.body).innerText")
    # Performance
    p.locator(".tw-tabs button", has_text="Performance").first.click(timeout=6000); p.wait_for_timeout(3500)
    t = main()
    out["perf"] = {"legende": "TW Performance Score" in t and "Skala 0–100" in t, "panel": "TW PERFORMANCE SCORE" in t, "alt_TW-Score": "TW-Score" in t, "info_buttons": p.locator(".tw-main .tw-scoreinfo button").count()}
    try:
        btn = p.locator(".tw-main .tw-scoreinfo button").first; btn.click(timeout=5000); p.wait_for_timeout(500)
        out["perf"]["popover"] = p.evaluate("() => { const d = document.querySelector('[role=dialog]'); if (!d) return 'KEIN POPOVER'; const r = d.getBoundingClientRect(); return { text: d.innerText.replace(/\\n+/g,' | ').slice(0,120), sichtbar: r.width > 0 && r.right <= innerWidth && r.bottom <= innerHeight }; }")
        p.keyboard.press("Escape"); p.wait_for_timeout(300)
        out["perf"]["esc_schliesst"] = p.evaluate("() => !document.querySelector('[role=dialog]')")
    except Exception as e: out["perf"]["popover"] = str(e)[:80]
    # Talente
    p.locator(".tw-tabs button", has_text="Scouting").first.click(timeout=6000); p.wait_for_timeout(3500)
    t = main()
    out["talente"] = {"legende": "TW Talent Score" in t, "kachel": bool(__import__('re').search(r'TW Talent Score \d+', t)), "alt": "TW-Score" in t}
    # Scouting-Listen
    try:
        p.locator(".tw-main button", has_text="Scouting-Listen").first.click(timeout=6000); p.wait_for_timeout(2500)
        t = main(); out["listen_uebersicht"] = {"sde": "TW Performance Score" in t, "alt": "TW-Score" in t}
        p.locator(".tw-main .tw-tile, .tw-main .tw-card").filter(has_text="Abwehr").first.click(timeout=6000); p.wait_for_timeout(3500)
        t = main(); out["liste"] = {"legende": "TW Performance Score" in t and "Skala" in t, "titel": (t.split("\n")[1] if "\n" in t else t)[:60]}
    except Exception as e: out["liste"] = str(e)[:100]
    # Spieler-Drawer
    try:
        p.locator(".tw-tabs button", has_text="Spieler").first.click(timeout=6000); p.wait_for_timeout(2000)
        p.locator(".tw-main input").first.fill("Kane"); p.wait_for_timeout(3000)
        p.locator(".tw-main .tw-card, .tw-main .tw-tile").filter(has_text="Kane").first.click(timeout=6000); p.wait_for_timeout(3000)
        out["drawer"] = p.evaluate("() => { const t = document.body.innerText; return { formkurve: /FORMKURVE\\s+—\\s+TW PERFORMANCE SCORE/i.test(t) || t.includes('TW Performance Score je Spieltag'), info: document.querySelectorAll('.tw-scoreinfo button').length }; }")
    except Exception as e: out["drawer"] = str(e)[:100]
    # EN
    try:
        p.evaluate("() => localStorage.setItem('tw_lang','en')")
        p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000); p.wait_for_timeout(5000)
        p.locator(".tw-tabs button", has_text="Performance").first.click(timeout=6000); p.wait_for_timeout(3500)
        p.locator(".tw-main .tw-scoreinfo button").first.click(timeout=5000); p.wait_for_timeout(500)
        out["en"] = p.evaluate("() => { const d = document.querySelector('[role=dialog]'); const t = (document.querySelector('.tw-main')||document.body).innerText; return { popover: d ? d.innerText.replace(/\\n+/g,' | ').slice(0,100) : 'KEIN POPOVER', legende: t.includes('scale 0–100'), deutsch_rest: /Skala|Spieltag/.test(t) }; }")
    except Exception as e: out["en"] = str(e)[:100]
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
