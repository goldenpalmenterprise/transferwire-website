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
    main = lambda: p.evaluate("() => (document.querySelector('.tw-main')||document.body).innerText")
    POP = "() => { const d = document.querySelector('[role=dialog]'); if (!d) return 'KEIN POPOVER'; const r = d.getBoundingClientRect(); return { text: d.innerText.replace(/\\n+/g,' | ').slice(0,90), top: Math.round(r.top), bottom: Math.round(r.bottom), right: Math.round(r.right), vh: innerHeight, sichtbar: r.width > 0 && r.top >= 0 && r.right <= innerWidth && r.bottom <= innerHeight && getComputedStyle(d).visibility === 'visible' }; }"
    # Performance: erster Info-Button oben, letzter Button an den unteren Rand gescrollt (Flip-Test)
    p.locator(".tw-tabs button", has_text="Performance").first.click(timeout=6000); p.wait_for_timeout(3500)
    t = main(); out["perf"] = {"legende": "TW Performance Score" in t and "Skala 0–100" in t, "panel": "TW PERFORMANCE SCORE" in t, "buttons": p.locator(".tw-main .tw-scoreinfo button").count()}
    p.locator(".tw-main .tw-scoreinfo button").first.click(timeout=5000); p.wait_for_timeout(400); out["perf"]["pop1"] = p.evaluate(POP)
    p.keyboard.press("Escape"); p.wait_for_timeout(300)
    last = p.locator(".tw-main .tw-scoreinfo button").last
    last.evaluate("el => el.scrollIntoView({block: 'end'})"); p.wait_for_timeout(400); last.click(timeout=5000); p.wait_for_timeout(400)
    out["perf"]["pop_unten"] = p.evaluate(POP)
    p.mouse.click(5, 5); p.wait_for_timeout(300); out["perf"]["klick_daneben_schliesst"] = p.evaluate("() => !document.querySelector('[role=dialog]')")
    # Talente
    p.locator(".tw-tabs button", has_text="Scouting").first.click(timeout=6000); p.wait_for_timeout(3500)
    t = main(); out["talente"] = {"legende": "TW Talent Score" in t, "kachel": bool(re.search(r'TW Talent Score \d+', t)), "alt": "TW-Score" in t}
    # Scouting-Listen -> Liste -> Spieler-Detail
    try:
        p.locator(".tw-main button", has_text="Scouting-Listen").first.click(timeout=6000); p.wait_for_timeout(2500)
        p.get_by_text("Top 25 U23-Abwehrspieler Europa", exact=True).first.click(timeout=6000); p.wait_for_timeout(4000)
        t = main(); out["liste"] = {"legende": "TW Performance Score" in t and "Skala 0–100" in t, "titel": "TOP 25 U23-ABWEHRSPIELER EUROPA" in t.upper()}
        p.locator(".tw-main div[style*='cursor: pointer']").filter(has_text="Min.").first.click(timeout=6000); p.wait_for_timeout(4000)
        bt = p.evaluate("() => document.body.innerText")
        out["detail"] = {"formkurve": bool(re.search(r'Formkurve\s+—\s+TW Performance Score je Spieltag', bt, re.I)), "info_gesamt": p.locator(".tw-scoreinfo button").count(), "alt": "TW-Score" in bt}
    except Exception as e: out["detail"] = str(e)[:120]
    # Englisch per Umschalter (ohne Reload)
    try:
        p.keyboard.press("Escape"); p.wait_for_timeout(300)
        p.evaluate("() => __twToggleLang('en')"); p.wait_for_timeout(1500)
        p.locator(".tw-tabs button", has_text="Performance").first.click(timeout=6000); p.wait_for_timeout(3000)
        t = main()
        p.locator(".tw-main .tw-scoreinfo button").first.click(timeout=5000); p.wait_for_timeout(400)
        d = p.evaluate(POP)
        out["en"] = {"legende": "scale 0–100" in t, "skala_deutsch": "Skala" in t, "popover": d["text"] if isinstance(d, dict) else d, "sichtbar": d.get("sichtbar") if isinstance(d, dict) else None}
        p.evaluate("() => __twToggleLang('de')"); p.wait_for_timeout(800)
    except Exception as e: out["en"] = str(e)[:120]
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
