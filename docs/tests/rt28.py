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
    POP = "() => { const d = document.querySelector('[role=dialog]'); if (!d) return 'KEIN POPOVER'; const r = d.getBoundingClientRect(); return { text: d.innerText.replace(/\\n+/g,' | ').slice(0,60), top: Math.round(r.top), bottom: Math.round(r.bottom), left: Math.round(r.left), right: Math.round(r.right), sichtbar: r.width > 0 && r.top >= 0 && r.left >= 0 && r.right <= innerWidth && r.bottom <= innerHeight && getComputedStyle(d).visibility === 'visible' && document.elementFromPoint(r.left + 20, r.top + 20) && d.contains(document.elementFromPoint(r.left + 20, r.top + 20)) }; }"
    p.locator(".tw-tabs button", has_text="Performance").first.click(timeout=6000); p.wait_for_timeout(3500)
    out["perf"] = {"buttons": p.locator(".tw-main .tw-scoreinfo button").count()}
    p.locator(".tw-main .tw-scoreinfo button").first.hover(); p.wait_for_timeout(200)
    p.locator(".tw-main .tw-scoreinfo button").first.click(timeout=5000); p.wait_for_timeout(400); out["perf"]["pop_panel_hover"] = p.evaluate(POP)
    p.keyboard.press("Escape"); p.wait_for_timeout(300)
    last = p.locator(".tw-main .tw-scoreinfo button").last
    last.evaluate("el => el.scrollIntoView({block: 'end'})"); p.wait_for_timeout(400); last.click(timeout=5000); p.wait_for_timeout(400)
    out["perf"]["pop_unten"] = p.evaluate(POP)
    p.mouse.click(5, 5); p.wait_for_timeout(300); out["perf"]["klick_daneben_schliesst"] = p.evaluate("() => !document.querySelector('[role=dialog]')")
    # Scouting-Listen -> Liste -> Spieler-Detail (Overlay) -> Popover im Overlay
    try:
        p.locator(".tw-tabs button", has_text="Scouting").first.click(timeout=6000); p.wait_for_timeout(3000)
        p.locator(".tw-main button", has_text="Scouting-Listen").first.click(timeout=6000); p.wait_for_timeout(2500)
        p.get_by_text("Top 25 U23-Abwehrspieler Europa", exact=True).first.click(timeout=6000); p.wait_for_timeout(4500)
        t = main(); out["liste"] = {"legende": "TW Performance Score" in t and "Skala 0–100" in t, "eintraege": len(re.findall(r"\d+ Min\.", t))}
        p.locator(".tw-main div").filter(has_text=re.compile(r"\d+ Min\.")).last.click(timeout=6000); p.wait_for_timeout(5000)
        bt = p.evaluate("() => document.body.innerText")
        out["detail"] = {"formkurve": bool(re.search(r"Formkurve\s+\u2014\s+TW Performance Score je Spieltag", bt, re.I)), "info_gesamt": p.locator(".tw-scoreinfo button").count(), "alt": "TW-Score" in bt}
        ib = p.locator(".tw-scoreinfo button").last; ib.click(timeout=5000); p.wait_for_timeout(400); out["detail"]["popover_im_overlay"] = p.evaluate(POP)
        p.keyboard.press("Escape"); p.wait_for_timeout(300)
    except Exception as e: out["detail"] = str(e)[:140]
    # Mobil 390px: Popover passt in den Bildschirm
    try:
        p.set_viewport_size({"width": 390, "height": 800}); p.wait_for_timeout(800)
        p.locator(".tw-tabs button", has_text="Performance").first.click(timeout=6000); p.wait_for_timeout(3000)
        fb = p.locator(".tw-main .tw-scoreinfo button").first; fb.evaluate("el => el.scrollIntoView({block: 'center'})"); p.wait_for_timeout(400); fb.click(timeout=5000); p.wait_for_timeout(400)
        out["mobil"] = p.evaluate(POP)
    except Exception as e: out["mobil"] = str(e)[:120]
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
