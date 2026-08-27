import json, time
from playwright.sync_api import sync_playwright
out = {}; fehler = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1600, "height": 950})
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de");')
    p = ctx.new_page()
    p.on("pageerror", lambda e: fehler.append("PE: " + str(e)[:200]))
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000); p.wait_for_timeout(5000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    p.locator(".tw-tabs button", has_text="Vertragsenden").first.click(timeout=6000); p.wait_for_selector(".tw-vttable", timeout=40000); p.wait_for_timeout(2000)
    out["radar"] = p.evaluate("() => { const t = document.querySelector('.tw-main').innerText; return { titel: t.includes('PROBETRAINING-RADAR'), text: t.includes('Probetraining, Testspielern oder vereinslosen'), karten: [...document.querySelectorAll('.tw-main div')].filter(d => d.style && d.style.borderLeft && d.style.borderLeft.includes('rgb(14, 116, 144)')).length, leer: t.includes('Aktuell keine Probetraining-Meldungen') }; }")
    # Spielerprofil von Lee (Datenbank -> Suche)
    p.locator(".tw-tabs button", has_text="Spieler").first.click(timeout=6000); p.wait_for_timeout(2500)
    p.locator(".tw-main input").first.fill("Han-Beom Lee"); p.wait_for_timeout(2500)
    p.locator(".tw-main tbody tr").first.click(timeout=8000); p.wait_for_timeout(2500)
    out["profil"] = p.evaluate("() => { const t = document.body.innerText; const m = t.match(/Verein gepr[üu]ft am [^\\n]*/); return { zeile: m ? m[0] : null, brugge: /Club Brugge/.test(t) }; }")
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False)); b.close()
