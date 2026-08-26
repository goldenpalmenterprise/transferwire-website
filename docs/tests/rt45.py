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
    p.locator(".tw-tabs button", has_text="Vereinsbedarf").first.click(timeout=6000); p.wait_for_timeout(3500)
    out["kopf"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const t = m.innerText; const btn = [...m.querySelectorAll('button')].find(b => b.innerText.trim() === '+ Neues Spielerprofil'); const h2 = m.querySelector('h2'); const intro = m.querySelector('.tw-bedarf-intro');
      const tiles = [...m.querySelectorAll('.tw-pos-grid .tw-tile')]; const tops = {}; tiles.forEach(x => { const y = Math.round(x.getBoundingClientRect().top); tops[y] = (tops[y]||0)+1; });
      return { titel: h2 ? h2.innerText : null, beschreibung: t.includes('Erstelle ein Spielerprofil und finde Vereine, deren aktueller Bedarf zu Position, Alter, Vertragsstatus und Zielmarkt passt.'), button_gruen: btn ? getComputedStyle(btn).backgroundColor : null, button_rechts: btn && h2 ? btn.getBoundingClientRect().left > h2.getBoundingClientRect().right : null, intro_hoehe: intro ? Math.round(intro.getBoundingClientRect().height) : null, schritte: ['1','Spielerprofil anlegen','2','Kriterien festlegen','3','Vereine vergleichen'].every(x => t.includes(x)), alert: t.includes('Neue passende Vereine werden automatisch erkannt und können per E-Mail-Alert gemeldet werden.'), kacheln: tiles.length, je_reihe: Object.values(tops), kachel0: tiles[0] ? { svg: !!tiles[0].querySelector('svg'), text: tiles[0].innerText.replace(/\\n/g,' | ') } : null }; }""")
    # Position waehlen
    p.locator(".tw-pos-grid .tw-tile").first.click(timeout=5000); p.wait_for_timeout(2000)
    out["position"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const t = m.innerText; const cards = [...m.querySelectorAll('.tw-need-grid article')]; const c0 = cards[0];
      return { ueberschrift: (t.match(/\\d+ Verein[e]? mit aktuellem [^\\n]*/) || [''])[0], karten: cards.length, score: c0 ? (c0.innerText.match(/TW Match Score[^\\n]*\\n?\\s*\\d+\\s*\\/100/) || c0.innerText.match(/\\d+\\s*\\/100/) || [''])[0].replace(/\\n/g,' ') : null, warum: c0 ? c0.innerText.includes('Warum dieses Match?') : null, gruende: c0 ? c0.querySelectorAll('.tw-match li').length : null, gruende_text: c0 ? [...c0.querySelectorAll('.tw-match li')].map(l => l.innerText.replace(/\\n/g,' ')).slice(0, 5) : null, buttons: c0 ? ['Match analysieren','Verein beobachten'].every(x => c0.innerText.includes(x)) : null, min3: cards.every(c => c.querySelectorAll('.tw-match li').length >= 3), liga: c0 ? !!c0.innerText.match(/Bundesliga|Liga|League|Serie|Eredivisie|Championship|MLS|Ligue|Superliga/) : null }; }""")
    # Match analysieren -> Panel
    try:
        p.locator(".tw-need-grid article button", has_text="Match analysieren").first.click(timeout=5000); p.wait_for_timeout(1200)
        out["analyse"] = p.evaluate("() => { const els = [...document.querySelectorAll('div')].filter(d => getComputedStyle(d).position === 'fixed' && /BELASTBARKEIT|QUELLEN/i.test(d.innerText)); return els.length ? els[0].innerText.split('\\n').slice(0,4).join(' | ').slice(0,120) : 'KEIN PANEL'; }")
        p.keyboard.press("Escape"); p.wait_for_timeout(400); p.mouse.click(5, 400); p.wait_for_timeout(500)
    except Exception as e: out["analyse"] = str(e)[:100]
    # Verein beobachten
    try:
        p.locator(".tw-need-grid article button", has_text="Verein beobachten").first.click(timeout=5000); p.wait_for_timeout(1000)
        out["beobachten"] = p.evaluate("() => { const t = document.body.innerText; return { dialog: /E-Mail|Alert|beobachten/i.test(t), beobachtet: t.includes('Verein beobachtet') }; }")
        # evtl. Dialog schliessen
        for txt in ["Später", "Schließen", "Nein", "Ohne"]:
            try: p.locator("button", has_text=txt).first.click(timeout=800); p.wait_for_timeout(300); break
            except Exception: pass
        p.keyboard.press("Escape"); p.wait_for_timeout(400)
        out["beobachten"]["danach"] = p.evaluate("() => document.body.innerText.includes('Verein beobachtet')")
    except Exception as e: out["beobachten"] = str(e)[:100]
    # Profil anlegen (Sheet unveraendert), dann Profilkarte
    try:
        p.locator(".tw-main button", has_text="Alle Positionen").first.click(timeout=5000); p.wait_for_timeout(800)
        p.locator(".tw-main button", has_text="+ Neues Spielerprofil").first.click(timeout=5000); p.wait_for_timeout(800)
        out["sheet"] = p.evaluate("() => { const els = [...document.querySelectorAll('div')].filter(d => getComputedStyle(d).position === 'fixed' && d.innerText.includes('Profil speichern')); const d = els[0]; if (!d) return 'KEIN SHEET'; return { labels: [...d.querySelectorAll('label')].map(l => l.innerText.trim()).slice(0,6), inputs: d.querySelectorAll('input').length, selects: d.querySelectorAll('select').length }; }")
        sh = "div[style*='position: fixed'] "
        p.locator(sh + "input").nth(0).fill("Sang-Yoon Kang")
        p.locator(sh + "select").first.select_option("ZM")
        p.locator(sh + "input").nth(1).fill("24"); p.locator(sh + "input").nth(2).fill("24")
        p.locator("button", has_text="Profil speichern").first.click(timeout=5000); p.wait_for_timeout(1500)
        for txt in ["Später", "Schließen", "Nein", "Ohne"]:
            try: p.locator("button", has_text=txt).first.click(timeout=800); p.wait_for_timeout(300); break
            except Exception: pass
        out["profil"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const t = m.innerText; const k = m.querySelector('.tw-profil-grid .tw-card'); return { meine: t.includes('Meine Spielerprofile'), intro_weg: !m.querySelector('.tw-bedarf-intro'), karte: k ? k.innerText.replace(/\\n/g,' | ').slice(0, 160) : null, buttons: k ? ['Matches ansehen','Profil bearbeiten'].every(x => k.innerText.includes(x)) : null }; }""")
        p.locator(".tw-profil-grid button", has_text="Matches ansehen").first.click(timeout=5000); p.wait_for_timeout(1500)
        out["profil_matches"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const t = m.innerText; const c0 = m.querySelector('.tw-need-grid article'); return { ueberschrift: (t.match(/\\d+ Verein[e]? passen zu [^\\n]*/) || [''])[0], karten: m.querySelectorAll('.tw-need-grid article').length, gruende: c0 ? [...c0.querySelectorAll('.tw-match li')].map(l => l.innerText.replace(/\\n/g,' ')).slice(0,6) : null, score: c0 ? (c0.innerText.match(/(\\d+)\\s*\\/100/) || ['',''])[1] : null }; }""")
        p.locator(".tw-main button", has_text="Alle Profile").first.click(timeout=5000); p.wait_for_timeout(800)
        p.locator(".tw-profil-grid button", has_text="Profil bearbeiten").first.click(timeout=5000); p.wait_for_timeout(800)
        out["bearbeiten"] = p.evaluate("() => { const els = [...document.querySelectorAll('div')].filter(d => getComputedStyle(d).position === 'fixed' && d.innerText.includes('Profil speichern')); const d = els[0]; if (!d) return 'KEIN SHEET'; const inp = d.querySelector('input'); const sel = d.querySelector('select'); return { name: inp ? inp.value : null, pos: sel ? sel.value : null }; }")
        p.locator("button", has_text="Profil speichern").first.click(timeout=5000); p.wait_for_timeout(1200)
        out["nach_bearbeiten"] = p.evaluate("() => document.querySelectorAll('.tw-profil-grid .tw-card').length")
    except Exception as e: out["profil_fehler"] = str(e)[:160]
    # Mobil
    p.set_viewport_size({"width": 390, "height": 800}); p.wait_for_timeout(1000)
    try: p.locator(".tw-main button", has_text="Alle Profile").first.click(timeout=2000); p.wait_for_timeout(600)
    except Exception: pass
    out["mobil"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const tiles = [...m.querySelectorAll('.tw-pos-grid .tw-tile')].slice(0, 4); const tops = {}; tiles.forEach(x => { const y = Math.round(x.getBoundingClientRect().top); tops[y] = (tops[y]||0)+1; }); return { je_reihe: Object.values(tops), breite: tiles[0] ? Math.round(tiles[0].getBoundingClientRect().width) : null }; }""")
    try:
        p.locator(".tw-pos-grid .tw-tile").first.click(timeout=5000); p.wait_for_timeout(1500)
    except Exception as e: out["mobil_klick"] = str(e)[:80]
    out["mobil_matches"] = p.evaluate("() => { const cards = [...document.querySelectorAll('.tw-need-grid article')].slice(0, 2); return { breiten: cards.map(c => Math.round(c.getBoundingClientRect().width)), einspaltig: cards.length < 2 || cards[1].getBoundingClientRect().top - cards[0].getBoundingClientRect().top > 50 }; }")
    out["fehler"] = fehler[:6]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
