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
    p.locator(".tw-tabs button", has_text="Transfers").first.click(timeout=6000); p.wait_for_timeout(4500)
    out["karten"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const t = m.innerText; const cards = [...m.querySelectorAll('article.tw-card')];
      const c0 = cards[0]; const kopf = c0 ? c0.innerText.split('\\n').slice(0, 3) : [];
      const sig = [...m.querySelectorAll('article .tw-rel')].map(x => x.innerText.trim());
      const clamp = c0 ? (getComputedStyle(c0.querySelector('.tw-clamp3') || c0).webkitLineClamp) : null;
      return { titel: t.includes('Transfers & Gerüchte'), beschreibung: t.includes('Bedarfssignale – laufend aktualisiert und mit dem TW Scout durchsuchbar'), scoutkopf: /TW SCOUT · TRANSFERRECHERCHE/.test(t), vorschlaege: ['Neue Bundesliga-Deals','Vertragslose U23-Spieler','Vereine mit aktuellem Stürmerbedarf'].every(x => t.includes(x)), zeile: (t.match(/\\d+ Meldungen · aktualisiert [^\\n]*/) || [''])[0], sort_toggle: t.includes('Neueste zuerst') && t.includes('Karten') && t.includes('Kompakt'), karten: cards.length, kopf: kopf, kicker_uppercase: c0 ? getComputedStyle(c0.querySelector('.tw-kicker')).textTransform : null, clamp3: clamp, details: (t.match(/Details →/g) || []).length, signal_wortlaut: sig.filter(x => /Signalstärke \\d+\\/100 · Quellenvertrauen: (hoch|mittel|gering)/.test(x)).length, bestaetigt: sig.filter(x => /✓ Bestätigt · /.test(x)).length, signal_alt: sig.filter(x => /^Signal \\d/.test(x) || x.includes('Konkret')).length, pfeil_ohne_ziel: /→\\s*\\?|→\\s*—/.test(t), leere_platzhalter: /·\\s*J\\s*·/.test(t), zwei_spalten: cards.length > 1 && Math.abs(cards[0].getBoundingClientRect().top - cards[1].getBoundingClientRect().top) < 2 && Math.abs(cards[0].getBoundingClientRect().width - cards[1].getBoundingClientRect().width) < 2 }; }""")
    # Kompakt
    p.locator(".tw-main button", has_text="Kompakt").first.click(timeout=5000); p.wait_for_timeout(1500)
    out["kompakt"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const rows = [...m.querySelectorAll('.tw-grow')]; const head = rows[0] ? rows[0].innerText.replace(/\\n+/g,' | ') : ''; const body = rows.slice(1); const hs = body.slice(0, 20).map(r => Math.round(r.getBoundingClientRect().height)); const txt = body.map(r => r.innerText).join('\\n');
      return { kopf: head, zeilen: body.length, zeilenhoehe: hs.length ? Math.round(hs.reduce((a,b)=>a+b,0)/hs.length) : null, platzhalter: /(^|\\n)[^\\n]*(—|\\?)\\s*($|\\n)/.test(txt) || txt.includes('→ ?') || txt.includes('Vertragslos → ?'), status_beispiel: [...new Set(body.slice(0, 40).map(r => r.children[5] ? r.children[5].innerText : ''))].slice(0, 4), bewegung_beispiel: body.slice(0, 6).map(r => r.children[3] ? r.children[3].innerText : '') }; }""")
    # Mobil: Kompakt verfuegbar, Karten einspaltig
    p.set_viewport_size({"width": 390, "height": 800}); p.wait_for_timeout(1200)
    out["mobil"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const tb = m.querySelector('.tw-gtable'); const kb = [...m.querySelectorAll('button')].find(b => b.innerText.trim() === 'Kompakt'); const ka = [...m.querySelectorAll('button')].find(b => b.innerText.trim() === 'Karten');
      return { kompakt_button_sichtbar: !!kb && kb.getBoundingClientRect().width > 0, tabelle_scrollbar: tb ? tb.scrollWidth > tb.clientWidth : null, tabelle_breite: tb ? Math.round(tb.getBoundingClientRect().width) : null, filterbutton: getComputedStyle(m.querySelector('.tw-gfilter-mobile')).display }; }""")
    p.locator(".tw-main button", has_text="Karten").first.click(timeout=5000); p.wait_for_timeout(1500)
    out["mobil_karten"] = p.evaluate("() => { const cards = [...document.querySelectorAll('.tw-main article.tw-card')].slice(0, 3); return { breiten: cards.map(c => Math.round(c.getBoundingClientRect().width)), einspaltig: cards.length < 2 || cards[1].getBoundingClientRect().top - cards[0].getBoundingClientRect().top > 50 }; }")
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
