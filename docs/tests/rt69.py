import json, time
from playwright.sync_api import sync_playwright
out = {}; fehler = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1600, "height": 950})
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de");')
    p = ctx.new_page(); p.on("pageerror", lambda e: fehler.append(str(e)[:160]))
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000); p.wait_for_timeout(7000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    sp1 = p.evaluate("""async () => { const r = await fetch('/db/players?select=player_id,name,team,foot,tm_joined,tm_team&foot=not.is.null&tm_joined=not.is.null&league=eq.Liga%20Portugal&order=tm_value_eur.desc.nullslast&limit=1'); const j = await r.json(); return j[0] || null; }""")
    out["spieler1_daten"] = sp1
    def offne_profil(name, tag):
        try:
            klick = p.evaluate("""() => { const bs = [...document.querySelectorAll('button')]; const perf = bs.find(b => b.textContent.trim() === 'Performance'); if (!perf) return 'kein Performance-Tab'; const sp = [...perf.parentElement.querySelectorAll('button')].find(b => b.textContent.trim() === 'Spieler'); if (!sp) return 'kein Spieler-Tab'; sp.click(); return 'ok'; }""")
            out[tag + "_nav"] = klick
            p.wait_for_timeout(2500)
            inp = p.locator('input[placeholder^="Spielername oder Verein"]')
            out[tag + "_inputs"] = inp.count()
            if not inp.count():
                out[tag + "_diag_placeholder"] = p.evaluate("() => [...document.querySelectorAll('input')].map(i => i.placeholder || i.type).slice(0, 15)")
                out[tag + "_diag_text"] = p.evaluate("() => document.body.innerText.slice(0, 400)").replace("\n", " | ")
                return ""
            feld = inp.first
            feld.fill(""); feld.fill(name); p.wait_for_timeout(2600)
            ziel = p.get_by_text(name, exact=False)
            out[tag + "_treffer"] = ziel.count()
            if ziel.count() > 1: ziel.nth(1).click(timeout=5000)
            elif ziel.count(): ziel.first.click(timeout=5000)
            p.wait_for_timeout(3200)
            txt = p.evaluate("() => document.body.innerText")
            k = txt.find(name)
            out[tag + "_kontext"] = txt[max(0, k-40):k+220].replace("\n", " | ") if k >= 0 else ""
            return txt
        except Exception as e:
            out[tag + "_fehler"] = str(e)[:200]
            try: out[tag + "_diag_placeholder"] = p.evaluate("() => [...document.querySelectorAll('input')].map(i => i.placeholder || i.type).slice(0, 15)")
            except Exception: pass
            return ""
    if sp1 and sp1.get("name"):
        txt = offne_profil(sp1["name"], "sp1")
        out["sp1_fuss"] = ("Fu\u00df:" in txt)
        out["sp1_seit"] = ("Im Verein seit" in txt)
        out["sp1_geprueft"] = ("Verein gepr\u00fcft" in txt)
        i = txt.find("Fu\u00df:")
        out["sp1_snippet"] = txt[max(0, i-120):i+120].replace("\n", " | ") if i >= 0 else ""
        try:
            p.keyboard.press("Escape"); p.wait_for_timeout(800)
        except Exception: pass
    txt2 = offne_profil("Bazunu", "sp2")
    out["sp2_hinweis"] = ("TM-Kader f\u00fchrt:" in txt2)
    j = txt2.find("TM-Kader f\u00fchrt:")
    out["sp2_snippet"] = txt2[max(0, j-80):j+140].replace("\n", " | ") if j >= 0 else ""
    out["fehler"] = fehler[:3]
    print(json.dumps(out, ensure_ascii=False)); b.close()
