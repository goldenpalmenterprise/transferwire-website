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
    POP = "() => { const d = document.querySelector('[role=dialog]'); if (!d) return 'KEIN POPOVER'; const r = d.getBoundingClientRect(); return { text: d.innerText.replace(/\\n+/g,' | ').slice(0,50), sichtbar: r.width > 0 && r.top >= 0 && r.left >= 0 && r.right <= innerWidth && r.bottom <= innerHeight && d.contains(document.elementFromPoint(r.left + 20, r.top + 20)) }; }"
    # Liste mit Wartezeit auf Einträge
    try:
        p.locator(".tw-tabs button", has_text="Scouting").first.click(timeout=6000); p.wait_for_timeout(3000)
        p.locator(".tw-main button", has_text="Scouting-Listen").first.click(timeout=6000); p.wait_for_timeout(2500)
        p.get_by_text("Top 25 U23-Abwehrspieler Europa", exact=True).first.click(timeout=6000)
        try: p.wait_for_function("() => /\\d+ Min\\./.test((document.querySelector('.tw-main')||document.body).innerText) || (document.querySelector('.tw-main')||document.body).innerText.includes('Keine Treffer')", timeout=25000)
        except Exception: pass
        t = main(); out["liste"] = {"legende": "TW Performance Score" in t and "Skala 0–100" in t, "eintraege": len(re.findall(r"\d+ Min\.", t)), "leer": "Keine Treffer" in t, "auszug": t[t.find("TOP 25"):t.find("TOP 25")+220].replace("\n", " | ") if "TOP 25" in t else t[:200].replace("\n", " | ")}
        if out["liste"]["eintraege"]:
            p.locator(".tw-main div").filter(has_text=re.compile(r"\d+ Min\.")).last.click(timeout=6000); p.wait_for_timeout(6000)
            bt = p.evaluate("() => document.body.innerText")
            out["detail"] = {"formkurve": bool(re.search(r"Formkurve\s+\u2014\s+TW Performance Score je Spieltag", bt, re.I)), "info_gesamt": p.locator(".tw-scoreinfo button").count(), "alt": "TW-Score" in bt}
            ib = p.locator(".tw-scoreinfo button").last; ib.click(timeout=5000); p.wait_for_timeout(400); out["detail"]["popover_im_overlay"] = p.evaluate(POP)
            p.keyboard.press("Escape"); p.wait_for_timeout(300)
    except Exception as e: out["detail"] = str(e)[:140]
    # Ersatzweg zum Spieler-Detail: Performance-Karte -> Spielername anklicken
    if not isinstance(out.get("detail"), dict):
        try:
            p.locator(".tw-tabs button", has_text="Performance").first.click(timeout=6000); p.wait_for_timeout(3500)
            p.locator(".tw-main .tw-card").filter(has_text="#1").first.locator("div").filter(has_text=re.compile(r"^[A-ZÀ-ÿ][^\n]{3,40}$")).nth(1).click(timeout=6000); p.wait_for_timeout(6000)
            bt = p.evaluate("() => document.body.innerText")
            out["detail_perf"] = {"formkurve": bool(re.search(r"Formkurve\s+\u2014\s+TW Performance Score je Spieltag", bt, re.I)), "info_gesamt": p.locator(".tw-scoreinfo button").count()}
        except Exception as e: out["detail_perf"] = str(e)[:120]
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
