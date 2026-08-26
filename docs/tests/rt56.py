import json, time, re
from playwright.sync_api import sync_playwright
out = {}; fehler = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1600, "height": 950}, accept_downloads=True)
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de"); localStorage.removeItem("tw_talent_snap");')
    p = ctx.new_page()
    p.on("pageerror", lambda e: fehler.append("PE: " + str(e)[:200]))
    p.on("console", lambda m: fehler.append("CE: " + m.text[:200]) if m.type == "error" and "Failed to load resource" not in m.text else None)
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000)
    p.wait_for_timeout(5000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    p.locator(".tw-tabs button", has_text="Scouting").first.click(timeout=6000)
    p.wait_for_selector(".tw-taltable", timeout=30000); p.wait_for_timeout(4000)
    out["kopf"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const t = m.innerText; return { titel: !!m.querySelector('h2') && m.querySelector('h2').innerText === 'Talent-Rankings', beschreibung: t.includes('U17- bis U21-Spieler nach Leistung, Entwicklung und Einsatzzeit – bewertet mit dem transparenten TW Talent Score.'), stand: (t.match(/Aktualisiert [^\\n]*/)||[''])[0], banner: (t.match(/ⓘ[^\\n]*/)||[''])[0], methodik: t.includes('Methodik ansehen'), chips: [...m.querySelectorAll('button')].map(b => b.innerText.trim()).filter(x => /Top 50 Europa|Unentdeckt|Torjäger|Vorlagen/.test(x)), lchips: [...m.querySelectorAll('button')].map(b => b.innerText.trim()).filter(x => /^(Alle|DE|EN|FR|ES|INT)$/.test(x)) }; }""")
    out["top3"] = p.evaluate("""() => { const k = [...document.querySelectorAll('.tw-taltop > div')]; return k.map((c, i) => ({ text: c.innerText.replace(/\\n/g,' | ').slice(0, 200), foto: !!c.querySelector('img') || !!c.querySelector('span[style*="border-radius: 99px"]'), rahmen: getComputedStyle(c).borderTopWidth, analyse: c.innerText.includes('Analyse öffnen') })); }""")
    out["tabelle"] = p.evaluate("""() => { const tb = document.querySelector('.tw-taltable'); const th = [...tb.querySelectorAll('thead th')].map(x => x.innerText.trim()); const rows = [...tb.querySelectorAll('tbody tr')]; const scores = rows.map(r => r.children[8].innerText.trim()); const namen = rows.map(r => r.children[1].innerText.trim()); return { kopf: th, zeilen: rows.length, scores: scores.slice(0, 8), dezimal: scores.filter(s => /\\d+,\\d/.test(s)).length, unterschiedlich: new Set(scores).size, doppelte_namen: namen.length - new Set(namen).size, zeile0: rows[0] ? rows[0].innerText.replace(/\\n/g,' | ').slice(0, 160) : null }; }""")
    # Score-Klick -> Panel
    p.locator(".tw-taltable tbody tr").first.locator("button").last.click(timeout=5000); p.wait_for_timeout(700)
    out["panel"] = p.evaluate("""() => { const q = document.querySelector('.tw-talpanel'); if (!q) return 'KEIN PANEL'; const t = q.innerText; return { faktoren: ['Leistung','Potenzial','Entwicklung','Einsatzzeit','Altersfaktor','Gegnerstärke'].every(x => t.includes(x)), aktionen: [...q.querySelectorAll('button')].map(b => b.innerText.trim()).filter(x => x && x !== '✕'), gewichte: (t.match(/\\d+ %/g)||[]).length }; }""")
    try:
        with p.expect_download(timeout=8000) as dl:
            p.locator(".tw-talpanel button", has_text="Exportieren").first.click(timeout=5000)
        out["export"] = dl.value.suggested_filename
    except Exception as e: out["export"] = str(e)[:80]
    p.keyboard.press("Escape"); p.wait_for_timeout(300)
    p.evaluate("() => { const b = document.querySelector('.tw-talpanel [aria-label]'); if (b) b.click(); }"); p.wait_for_timeout(300)
    # Methodik-Link
    p.get_by_role("button", name="Methodik ansehen").click(timeout=5000); p.wait_for_timeout(600)
    out["methodik"] = p.evaluate("() => { const d = document.querySelector('[role=dialog]'); return d ? d.innerText.replace(/\\n/g,' | ').slice(0, 90) : 'KEIN POPOVER'; }")
    p.keyboard.press("Escape"); p.wait_for_timeout(300)
    # Kategorie Torjaeger (Chips unveraendert, Tabelle passt sich an)
    p.locator(".tw-main button", has_text="Torjäger").first.click(timeout=5000); p.wait_for_selector(".tw-taltable", timeout=20000); p.wait_for_timeout(1500)
    out["tore"] = p.evaluate("() => { const th = [...document.querySelectorAll('.tw-taltable thead th')].map(x => x.innerText.trim()); const r = document.querySelector('.tw-taltable tbody tr'); return { letzte_spalte: th[th.length-1], zeile0: r ? r.innerText.replace(/\\n/g,' | ').slice(0, 120) : null, top3: document.querySelectorAll('.tw-taltop > div').length }; }")
    # Mobil
    p.set_viewport_size({"width": 390, "height": 800}); p.wait_for_timeout(1500)
    out["mobil"] = p.evaluate("() => { const top = document.querySelector('.tw-taltop'); return { top3_spalten: top ? getComputedStyle(top).gridTemplateColumns.split(' ').length : null, tabelle: !!document.querySelector('.tw-taltable'), karten: document.querySelectorAll('.tw-main .tw-card').length }; }")
    out["fehler"] = fehler[:6]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
