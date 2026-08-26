import json, time, re
from playwright.sync_api import sync_playwright
out = {}; fehler = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1600, "height": 950}, accept_downloads=True)
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de"); localStorage.removeItem("tw_scoutlist"); localStorage.removeItem("tw_dbsearches"); localStorage.removeItem("tw_dbcols");')
    p = ctx.new_page()
    p.on("pageerror", lambda e: fehler.append("PE: " + str(e)[:200]))
    p.on("console", lambda m: fehler.append("CE: " + m.text[:200]) if m.type == "error" and "Failed to load resource" not in m.text else None)
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000)
    p.wait_for_timeout(5000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    p.locator(".tw-tabs button", has_text="Spieler").first.click(timeout=6000); p.wait_for_timeout(8000)
    out["kopf"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const t = m.innerText; return { titel: (m.querySelector('h2')||{}).innerText || t.split('\\n')[0], beschreibung: (t.match(/[\\d.]+ Spieler aus \\d+ Ligen[^\\n]*/)||[''])[0], filter: { inputs: [...m.querySelectorAll('input:not([type=checkbox])')].map(i => i.placeholder), selects: [...m.querySelectorAll('.tw-main > div > div:nth-child(2) select, select')].slice(0,4).map(s => s.options[0].text) }, kpis: [...m.querySelectorAll('.tw-db > div:first-child > div')].map(k => k.innerText.replace(/\\n/g,' ')), marketing_weg: !t.includes('Blitzsuche') && !t.includes('Entdecke ') }; }""")
    out["tabelle"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const t = m.innerText; const tb = m.querySelector('.tw-dbtable'); const rows = tb ? [...tb.querySelectorAll('tbody tr')] : []; const th = tb ? [...tb.querySelectorAll('thead th')].map(x => x.innerText.trim()).filter(Boolean) : [];
      return { titel: t.includes('Empfohlene Spieler'), sub: t.includes('Sortiert nach aktueller Relevanz und Datenqualität'), ergebnisse: (t.match(/[\\d.]+ Ergebnisse/)||[''])[0], toolbar: ['Sortierung:', 'Spalten anpassen', 'Suche speichern', 'Exportieren'].every(x => t.includes(x)), kopf: th, sticky: tb ? getComputedStyle(tb.querySelector('thead th')).position : null, zeilen: rows.length, zeile0: rows[0] ? rows[0].innerText.replace(/\\n/g,' | ').slice(0, 160) : null, scores_tw: rows.filter(r => r.querySelector('td:nth-last-child(3) span') && !r.innerText.includes('API')).length, vertrag_spalte: rows.slice(0, 40).filter(r => /\\d{2}\\.\\d{2}\\.\\d{4}/.test(r.innerText)).length, mw_spalte: rows.slice(0, 40).filter(r => /Mio\\. €|Tsd\\. €/.test(r.innerText)).length }; }""")
    # Sortieren: Klick auf Alter
    p.locator(".tw-dbtable thead th", has_text="Alter").first.click(timeout=5000); p.wait_for_timeout(600)
    out["sort"] = p.evaluate("() => { const rows = [...document.querySelectorAll('.tw-dbtable tbody tr')].slice(0, 5); const ages = rows.map(r => Number(r.children[2].innerText)); return { alter: ages, absteigend: ages.every((v, i) => i === 0 || ages[i-1] >= v) }; }")
    # Hover-Aktionen + Vergleich + Scouting-Liste
    r0 = p.locator(".tw-dbtable tbody tr").first
    r0.hover(); p.wait_for_timeout(400)
    out["hover"] = p.evaluate("() => { const r = document.querySelector('.tw-dbtable tbody tr'); const act = r.querySelector('.tw-dbact'); return { sichtbar: getComputedStyle(act).opacity === '1', labels: [...act.querySelectorAll('button')].map(b => b.title) }; }")
    r0.locator(".tw-dbact button").nth(2).click(timeout=5000); p.wait_for_timeout(400)
    r0.locator(".tw-dbact button").nth(3).click(timeout=5000); p.wait_for_timeout(600)
    out["aktionen"] = p.evaluate("() => { const r = document.querySelector('.tw-dbtable tbody tr'); const t = document.querySelector('.tw-main').innerText; return { vergleich_markiert: r.classList.contains('on'), scoutliste_button: (t.match(/Scouting-Liste \\d+/)||[''])[0], vergleich_leiste: /Vergleich/.test(document.body.innerText) }; }")
    # Kurzansicht
    p.locator(".tw-dbtable tbody tr").nth(1).click(timeout=5000)
    try: p.wait_for_function("() => { const q = document.querySelector('.tw-quick'); return q && !q.querySelector('.tw-skel'); }", timeout=20000)
    except Exception: pass
    p.wait_for_timeout(500)
    out["quick"] = p.evaluate("""() => { const q = document.querySelector('.tw-quick'); if (!q) return 'KEINE KURZANSICHT'; const t = q.innerText; return { name: t.split('\\n')[1], score: /TW PERFORMANCE SCORE/.test(t), marktwert: t.includes('Marktwert'), vertrag: t.includes('Vertragsende'), form: t.includes('Formkurve'), spark: !!q.querySelector('svg polyline'), staerken: t.includes('Stärken'), buttons: ['Volles Profil öffnen', 'Beobachten'].every(x => t.includes(x)), breite: Math.round(q.getBoundingClientRect().width) }; }""")
    p.keyboard.press("Escape"); p.wait_for_timeout(400)
    out["quick_zu"] = p.evaluate("() => !document.querySelector('.tw-quick')")
    # Spalten anpassen
    p.locator(".tw-main button", has_text="Spalten anpassen").first.click(timeout=5000); p.wait_for_timeout(400)
    p.locator(".tw-main label", has_text="Marktwert").locator("input").click(timeout=5000); p.wait_for_timeout(500)
    out["spalten"] = p.evaluate("() => [...document.querySelectorAll('.tw-dbtable thead th')].map(x => x.innerText.trim()).filter(Boolean)")
    p.locator(".tw-main button", has_text="Spalten anpassen").first.click(timeout=5000); p.wait_for_timeout(300)
    # Export
    try:
        with p.expect_download(timeout=8000) as dl:
            p.locator(".tw-main button", has_text="Exportieren").first.click(timeout=5000)
        out["export"] = dl.value.suggested_filename
    except Exception as e: out["export"] = str(e)[:80]
    # Suche: Filterleiste nutzen
    p.locator(".tw-main input[placeholder*='Spielername']").first.fill("Palmer"); p.wait_for_timeout(3500)
    out["suche"] = p.evaluate("() => { const t = document.querySelector('.tw-main').innerText; return { titel: t.includes('Suchergebnisse'), zeilen: document.querySelectorAll('.tw-dbtable tbody tr').length, palmer: t.includes('Palmer'), ergebnisse: (t.match(/\\d+ Ergebnisse/)||[''])[0] }; }")
    # Mobil
    p.locator(".tw-main input[placeholder*='Spielername']").first.fill(""); p.wait_for_timeout(1500)
    p.set_viewport_size({"width": 390, "height": 800}); p.wait_for_timeout(1500)
    out["mobil"] = p.evaluate("() => { const m = document.querySelector('.tw-main'); return { tabelle: !!m.querySelector('.tw-dbtable'), karten: m.querySelectorAll('.tw-db .tw-card').length, karte0: (m.querySelector('.tw-db .tw-card')||{innerText:''}).innerText.replace(/\\n/g,' | ').slice(0, 120), filter_inputs: m.querySelectorAll('input:not([type=checkbox])').length, filter_selects: m.querySelectorAll('select').length }; }")
    out["fehler"] = fehler[:6]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
