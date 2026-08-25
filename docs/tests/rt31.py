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
    POP = "() => { const d = document.querySelector('[role=dialog]'); if (!d) return 'KEIN POPOVER'; const r = d.getBoundingClientRect(); return { text: d.innerText.replace(/\\n+/g,' | ').slice(0,50), sichtbar: r.width > 0 && r.top >= 0 && r.left >= 0 && r.right <= innerWidth && r.bottom <= innerHeight && d.contains(document.elementFromPoint(r.left + 20, r.top + 20)) }; }"
    try:
        p.locator(".tw-tabs button", has_text="Spieler").first.click(timeout=6000); p.wait_for_timeout(2500)
        p.locator(".tw-main input[placeholder*='Spielername']").first.fill("Kane"); p.wait_for_timeout(4000)
        out["suche"] = {"profil_buttons": p.locator(".tw-main button", has_text="Profil").count()}
        p.locator(".tw-main button", has_text="Profil").first.click(timeout=6000)
        try: p.wait_for_function("() => document.querySelectorAll('.tw-scoreinfo button').length > 0", timeout=20000)
        except Exception: pass
        p.wait_for_timeout(1500)
        bt = p.evaluate("() => document.body.innerText")
        out["detail"] = {"formkurve": bool(re.search(r"Formkurve\s+\u2014\s+TW Performance Score je Spieltag", bt, re.I)), "info_buttons": p.locator(".tw-scoreinfo button").count(), "alt": "TW-Score" in bt, "auszug": (bt[bt.lower().find("formkurve"):bt.lower().find("formkurve")+90].replace("\n"," | ") if "formkurve" in bt.lower() else "-")}
        ib = p.locator(".tw-scoreinfo button").last; ib.evaluate("el => el.scrollIntoView({block: 'center'})"); p.wait_for_timeout(300); ib.click(timeout=5000); p.wait_for_timeout(500)
        out["detail"]["popover_im_overlay"] = p.evaluate(POP)
        p.keyboard.press("Escape"); p.wait_for_timeout(300); out["detail"]["esc"] = p.evaluate("() => !document.querySelector('[role=dialog]')")
    except Exception as e: out["detail"] = str(e)[:160]
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
