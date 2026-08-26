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
    p.locator(".tw-tabs button", has_text="Vertragsenden").first.click(timeout=6000); p.wait_for_selector(".tw-vttable", timeout=40000); p.wait_for_timeout(3000)
    out["kopf"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const t = m.innerText; return { titel: t.includes('Auslaufende Verträge & verfügbare Spieler'), beschreibung: t.includes('Spieler mit auslaufenden Verträgen, bestätigte Free Agents und Vereine unter Verkaufsdruck – täglich aktualisiert.'), kpis: [...m.querySelectorAll('.tw-vt-kpis > div')].map(k => k.innerText.replace(/\\n/g,' ')), kategorien: ['Auslaufende Verträge (binnen 12 Monaten)', 'Vertragslos gemeldet', 'Klubs unter Verkaufsdruck'].map(k => t.includes(k)) }; }""")
    out["tabelle"] = p.evaluate("""() => { const tb = document.querySelector('.tw-vttable'); if (!tb) return 'KEINE TABELLE'; const th = [...tb.querySelectorAll('thead th')].map(x => x.innerText.trim()); const rows = [...tb.querySelectorAll('tbody tr')]; const txt = rows.map(r => r.innerText).join('\\n');
      const statusZellen = rows.map(r => r.children[4].innerText.replace(/\\n/g,' | '));
      return { kopf: th, zeilen: rows.length, sticky: getComputedStyle(tb.querySelector('thead th')).position, status_beispiele: [...new Set(statusZellen.map(s => s.replace(/\\d{2}\\.\\d{2}\\.\\d{4}/, 'DD.MM.YYYY').replace(/\\d+ Tag(en)?/, 'N Tagen')))].slice(0, 6), vertragslos_seit: statusZellen.filter(s => /^Vertragslos seit \\d{2}\\.\\d{2}\\.\\d{4}/.test(s)).length, sofort_badges: statusZellen.filter(s => s.includes('SOFORT VERFÜGBAR') || s.includes('Sofort verfügbar')).length, endet_in: statusZellen.filter(s => /^Endet in/.test(s)).length, vertrag_bis: statusZellen.filter(s => /^Vertrag bis \\d{2}\\.\\d{2}\\.\\d{4}$/.test(s.split(' | ')[0])).length, verboten: /Vertrag bis vertragslos/i.test(txt), orange_ohne_dringlichkeit: rows.filter(r => { const s = r.children[4].querySelector('span span'); return s && /^Vertrag bis/.test(s.innerText) && getComputedStyle(s).color === 'rgb(176, 122, 5)'; }).length, mw_zellen: rows.filter(r => /Mio\\. €|Tsd\\. €/.test(r.children[6].innerText)).length, quellen: [...new Set(rows.map(r => r.children[7].innerText.trim()))], scores: rows.slice(0, 5).map(r => r.children[8].innerText.replace(/\\n/g,'')), zeile0: rows[0] ? rows[0].innerText.replace(/\\n/g,' | ').slice(0, 160) : null }; }""")
    # Score-Erklaerung
    try:
        p.locator(".tw-vttable thead .tw-scoreinfo button").first.click(timeout=5000); p.wait_for_timeout(600)
        out["erklaerung"] = p.evaluate("() => { const d = document.querySelector('[role=dialog]'); return d ? { text: d.innerText.replace(/\\n/g,' | ').slice(0, 140), faktoren: /Verfügbarkeit|Alter|Einsatzminuten|Marktwert|Quelle/.test(d.innerText) } : 'KEIN POPOVER'; }")
        p.keyboard.press("Escape"); p.wait_for_timeout(300)
    except Exception as e: out["erklaerung"] = str(e)[:100]
    # Zeile klicken -> Spielerprofil
    try:
        p.locator(".tw-vttable tbody tr").first.click(timeout=5000)
        p.wait_for_function("() => /Formkurve/i.test(document.body.innerText)", timeout=20000); out["profil"] = True
        p.keyboard.press("Escape"); p.wait_for_timeout(400)
    except Exception as e: out["profil"] = str(e)[:80]
    # Mobil
    p.set_viewport_size({"width": 390, "height": 800}); p.wait_for_timeout(1500)
    out["mobil"] = p.evaluate("() => { const m = document.querySelector('.tw-main'); const karten = [...m.querySelectorAll('.tw-card')].filter(c => /Vertrag|Vertragslos|Endet/.test(c.innerText)); return { tabelle: !!m.querySelector('.tw-vttable'), karten: karten.length, karte0: karten[0] ? karten[0].innerText.replace(/\\n/g,' | ').slice(0, 140) : null, kpis: m.querySelectorAll('.tw-vt-kpis > div').length }; }")
    out["fehler"] = fehler[:6]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
