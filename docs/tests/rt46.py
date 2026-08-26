import json, time, re
from playwright.sync_api import sync_playwright
out = {}; fehler = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1600, "height": 950})
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de"); localStorage.removeItem("tw_watch");')
    p = ctx.new_page()
    p.on("pageerror", lambda e: fehler.append("PE: " + str(e)[:200]))
    p.on("console", lambda m: fehler.append("CE: " + m.text[:200]) if m.type == "error" and "Failed to load resource" not in m.text else None)
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000)
    p.wait_for_timeout(5000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    p.locator(".tw-tabs button", has_text="Performance").first.click(timeout=6000); p.wait_for_timeout(6000)
    out["kopf"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const t = m.innerText; return { titel: (m.querySelector('h2')||{}).innerText || t.split('\\n')[0], beschreibung: t.includes('Positionsgewichtete Spieltagsanalyse aus offiziellen Leistungsdaten. Der TW Performance Score wird jede Nacht neu berechnet.'), datenstand: (t.match(/Datenstand:[^\\n]*/)||[''])[0], filter: { inputs: [...m.querySelectorAll('input')].map(i => i.placeholder), selects: [...m.querySelectorAll('select')].map(s => s.options[0].text) } }; }""")
    out["haupt"] = p.evaluate("""() => { const g = document.querySelector('.tw-perf-main'); if (!g) return 'KEIN HAUPTBEREICH'; const kids = [...g.children]; const gw = g.getBoundingClientRect().width; const pitch = g.querySelector('.tw-pitch'); const svg = pitch ? pitch.querySelector('svg') : null; const marker = [...g.querySelectorAll('.tw-pm')];
      const karte = kids[1]; const kt = karte ? karte.innerText : '';
      return { spalten: kids.map(k => Math.round(k.getBoundingClientRect().width / gw * 100)), pitch_ar: pitch ? Math.round(pitch.getBoundingClientRect().width / pitch.getBoundingClientRect().height * 100) / 100 : null, linien: svg ? { rects: svg.querySelectorAll('rect').length, circles: svg.querySelectorAll('circle').length, paths: svg.querySelectorAll('path').length, lines: svg.querySelectorAll('line').length } : null, marker: marker.length, marker0: marker[0] ? marker[0].innerText.replace(/\\n/g,' | ').slice(0, 80) : null, marker_groesse: marker[0] ? Math.round(marker[0].querySelector('span').getBoundingClientRect().width) : null, karte: { titel: /SPIELER DES SPIELTAGS/.test(kt), score: (kt.match(/TW PERFORMANCE SCORE[^\\n]*\\n?\\s*(\\d+)/) || ['',''])[1], delta: (kt.match(/(▲|▼|▶)[^\\n]*|Erstes erfasstes Spiel|Vergleich[^\\n]*/) || [''])[0], werte: (kt.match(/\\d+ (Tore?|Assists?|Minuten|Paraden?|Gegentore?)|\\d+ % Passquote|\\d+\\/\\d+ Zweikämpfe/g) || []).slice(0, 6), buttons: ['Analyse öffnen', 'Beobachten'].every(x => kt.includes(x)), monogramm: !!karte.querySelector('div[style*="linear-gradient"]') } }; }""")
    # Hover auf Marker
    try:
        p.locator(".tw-pm").first.hover(); p.wait_for_timeout(500)
        out["hover"] = p.evaluate("() => { const tip = document.querySelector('.tw-pm:hover .tw-pm-tip') || document.querySelector('.tw-pm-tip'); const cs = getComputedStyle(tip); return { sichtbar: cs.opacity === '1' && cs.visibility === 'visible', text: tip.innerText.replace(/\\n/g, ' | ').slice(0, 120) }; }")
    except Exception as e: out["hover"] = str(e)[:100]
    # Wie wird der Score berechnet?
    try:
        p.locator(".tw-main span", has_text="Wie wird der Score berechnet?").first.click(timeout=5000); p.wait_for_timeout(500)
        out["erklaerung"] = p.evaluate("() => { const d = document.querySelector('[role=dialog]'); return d ? d.innerText.replace(/\\n/g,' | ').slice(0, 80) : 'KEIN POPOVER'; }")
        p.keyboard.press("Escape"); p.wait_for_timeout(300)
    except Exception as e: out["erklaerung"] = str(e)[:100]
    out["tabelle"] = p.evaluate("""() => { const tb = document.querySelector('.tw-ptable'); if (!tb) return 'KEINE TABELLE'; const head = tb.querySelector('.tw-phead'); const rows = [...tb.querySelectorAll('.tw-prow')].filter(r => !r.classList.contains('tw-phead')); const r0 = rows[0]; return { kopf: head.innerText.replace(/\\n/g,' | '), zeilen: rows.length, zeile0: r0 ? r0.innerText.replace(/\\n/g,' | ').slice(0, 140) : null, spalten: r0 ? r0.children.length : null }; }""")
    try:
        p.locator(".tw-ptable .tw-prow:not(.tw-phead)").first.click(timeout=5000); p.wait_for_timeout(500)
        out["details"] = p.evaluate("() => { const d = document.querySelector('.tw-prow-details'); return d ? { text: d.innerText.replace(/\\n/g,' | ').slice(0, 120), analyse: d.innerText.includes('Analyse öffnen') } : 'KEINE DETAILS'; }")
    except Exception as e: out["details"] = str(e)[:100]
    # Analyse oeffnen -> Spieler-Detail
    try:
        p.locator(".tw-perf-main button", has_text="Analyse öffnen").first.click(timeout=5000)
        p.wait_for_function("() => document.querySelectorAll('.tw-scoreinfo button').length > 2", timeout=15000); p.wait_for_timeout(800)
        out["analyse"] = p.evaluate("() => /Formkurve/i.test(document.body.innerText)")
        p.keyboard.press("Escape"); p.wait_for_timeout(500)
    except Exception as e: out["analyse"] = str(e)[:100]
    # Mobil
    p.set_viewport_size({"width": 390, "height": 800}); p.wait_for_timeout(1500)
    out["mobil"] = p.evaluate("""() => { const g = document.querySelector('.tw-perf-main'); const kids = g ? [...g.children] : []; const pitch = document.querySelector('.tw-pitch'); return { pitch_ueber_karte: kids.length === 2 && kids[0].getBoundingClientRect().bottom <= kids[1].getBoundingClientRect().top + 1, pitch_portrait: pitch ? pitch.classList.contains('portrait') : null, pitch_ar: pitch ? Math.round(pitch.getBoundingClientRect().width / pitch.getBoundingClientRect().height * 100) / 100 : null, marker: document.querySelectorAll('.tw-pm').length, tabelle: !!document.querySelector('.tw-ptable'), karten: document.querySelectorAll('.tw-main .tw-card').length, filter_inputs: document.querySelectorAll('.tw-main input').length, filter_selects: document.querySelectorAll('.tw-main select').length }; }""")
    out["fehler"] = fehler[:6]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
