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
    out["desktop"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const t = m.innerText;
      const cards = [...m.querySelectorAll('article.tw-card')]; const rows = {}; cards.slice(0, 6).forEach(c => { const r = c.getBoundingClientRect(); (rows[Math.round(r.top)] = rows[Math.round(r.top)] || []).push([Math.round(r.width), Math.round(r.height)]); });
      const sels = [...m.querySelectorAll('.tw-gfilter-row select')].map(s => ({ wert: s.value, erste: s.options[0].text, gewaehlt: s.options[s.selectedIndex].text }));
      const zeile = (t.match(/\\d+ Meldungen · aktualisiert [^\\n]*/) || [''])[0];
      return { beschreibung: t.includes('Bedarfssignale – laufend aktualisiert und mit dem TW Scout durchsuchbar'), scoutkopf: /TW SCOUT · TRANSFERRECHERCHE/.test(t), platzhalter: (m.querySelector('.tw-scout input') || {}).placeholder, vorschlaege: [...m.querySelectorAll('.tw-scout button')].map(b => b.innerText.trim()).filter(x => x && !/fragen|denkt/.test(x)).slice(0, 4), scout_hoehe: Math.round((m.querySelector('.tw-scout') || { getBoundingClientRect: () => ({ height: 0 }) }).getBoundingClientRect().height), filter: sels, verein_ph: (m.querySelector('.tw-gfilter-row input') || {}).placeholder, chips: [...m.querySelectorAll('.tw-gchips button')].map(b => b.innerText.trim()), alle_bg: getComputedStyle(m.querySelector('.tw-gchips button')).backgroundColor, zeile: zeile, sortierung: [...m.querySelectorAll('select')].map(s => s.options[s.selectedIndex].text).filter(x => /zuerst|Signal|Belastbarkeit/.test(x))[0], reihen: Object.values(rows), pfeil_ohne_ziel: t.includes('→\\n—') || t.includes('→ —'), zielverein: (t.match(/ZIELVEREIN/g) || []).length, karten: cards.length }; }""")
    # Mobil
    p.set_viewport_size({"width": 390, "height": 800}); p.wait_for_timeout(1200)
    out["mobil"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const ch = m.querySelector('.tw-gchips'); const cards = [...m.querySelectorAll('article.tw-card')].slice(0, 3);
      return { filterzeile_sichtbar: getComputedStyle(m.querySelector('.tw-gfilter-row')).display, filterbutton: getComputedStyle(m.querySelector('.tw-gfilter-mobile')).display, chips_scroll: ch ? (ch.scrollWidth > ch.clientWidth) : null, chips_wrap: ch ? getComputedStyle(ch).flexWrap : null, karten_breiten: cards.map(c => Math.round(c.getBoundingClientRect().width)), einspaltig: cards.length < 2 || Math.abs(cards[0].getBoundingClientRect().top - cards[1].getBoundingClientRect().top) > 50 }; }""")
    try:
        p.locator(".tw-gfilter-mobile button").first.click(timeout=5000); p.wait_for_timeout(800)
        out["sheet"] = p.evaluate("() => { const d = document.querySelector('[role=dialog]'); if (!d) return 'KEIN SHEET'; const r = d.getBoundingClientRect(); return { unten: Math.round(innerHeight - r.bottom), breite: Math.round(r.width), selects: d.querySelectorAll('select').length, checkboxes: d.querySelectorAll('input[type=checkbox]').length, button: (d.innerText.match(/\\d+ Meldungen anzeigen/) || [''])[0] }; }")
        p.locator("[role=dialog] button", has_text="Meldungen anzeigen").first.click(timeout=5000); p.wait_for_timeout(500)
        out["sheet_zu"] = p.evaluate("() => !document.querySelector('[role=dialog]')")
    except Exception as e: out["sheet"] = str(e)[:120]
    # Englisch (Desktop)
    try:
        p.set_viewport_size({"width": 1600, "height": 950}); p.evaluate("() => __twToggleLang('en')"); p.wait_for_timeout(1500)
        out["en"] = p.evaluate("() => { const m = document.querySelector('.tw-main'); const t = m.innerText; return { beschreibung: t.includes('club-need signals'), scoutkopf: /TW SCOUT · TRANSFER RESEARCH/.test(t), zeile: (t.match(/\\d+ reports · updated [^\\n]*/) || [''])[0], vorschlag: t.includes('Clubs currently seeking strikers'), deutsch_rest: /Meldungen|aktualisiert|Vereinsbedarf \\d/.test(t) }; }")
        p.evaluate("() => __twToggleLang('de')"); p.wait_for_timeout(500)
    except Exception as e: out["en"] = str(e)[:100]
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
