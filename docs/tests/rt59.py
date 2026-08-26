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
    p.locator(".tw-tabs button", has_text="Community").first.click(timeout=6000); p.wait_for_timeout(3500)
    out["kopf"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const t = m.innerText; return { titel: (m.querySelector('h2')||{}).innerText, beschreibung: t.includes('Teile belastbare Hinweise aus deinem Netzwerk. Beiträge werden gekennzeichnet, geprüft und nach Relevanz in TransferWire eingeordnet.'), unterbereiche: [...m.querySelectorAll('button')].map(b => b.innerText.trim()).filter(x => /^(Transferhinweise|Networking Pro|Moderation)$/.test(x)), banner: (t.match(/ⓘ[^\\n]*/)||[''])[0], suche: [...m.querySelectorAll('input')].map(i => i.placeholder), composer: t.includes('Teile einen Transferhinweis aus deinem Netzwerk …') && t.includes('Hinweis erstellen'), textarea_sichtbar: !!m.querySelector('textarea'), leer: ['Noch keine Community-Hinweise', 'Für die aktuelle Auswahl liegen noch keine Hinweise vor. Teile den ersten Hinweis oder versuche es später erneut.', 'Hinweis teilen'].map(x => t.includes(x)), aside: ['Aktueller Prüfstatus', 'Häufig genannte Vereine', 'Community-Regeln'].map(x => /AKTUELLER PRÜFSTATUS|HÄUFIG GENANNTE VEREINE|COMMUNITY-REGELN/.test(t) || t.includes(x)), spalten: (() => { const g = m.querySelector('.tw-cmgrid'); return g ? getComputedStyle(g).gridTemplateColumns.split(' ').length : null; })() }; }""")
    # Mehr zur Verifizierung
    p.locator(".tw-main button", has_text="Mehr zur Verifizierung").first.click(timeout=5000); p.wait_for_timeout(300)
    out["verif"] = p.evaluate("() => document.querySelector('.tw-main').innerText.includes('TW geprüft: vom TransferWire-Team')")
    # Panel oeffnen
    p.locator(".tw-main button", has_text="Hinweis erstellen").first.click(timeout=5000); p.wait_for_timeout(500)
    out["panel"] = p.evaluate("""() => { const q = document.querySelector('.tw-cmpanel'); if (!q) return 'KEIN PANEL'; const t = q.innerText; return { felder: ['Art des Hinweises','Verein','Spieler oder Position','Zeitraum','Liga oder Region','Beschreibung','Quelle oder Kontext','Mit Profil veröffentlichen','Anonym veröffentlichen','Ich bestätige'].map(x => t.includes(x)), placeholder: (q.querySelector('textarea')||{}).placeholder, button: (() => { const b = [...q.querySelectorAll('button')].find(x => x.innerText.includes('Hinweis zur Prüfung einreichen')); return b ? { da: true, disabled: b.disabled } : null; })(), breite: Math.round(q.getBoundingClientRect().width), arten: [...q.querySelectorAll('select')][0].options.length, zeitraeume: [...q.querySelectorAll('select')][1].options.length }; }""")
    p.locator(".tw-cmpanel textarea").fill("Aus dem Umfeld des Vereins ist zu hören, dass ein zusätzlicher Mittelstürmer gesucht wird."); p.locator(".tw-cmpanel input[type=checkbox]").check(); p.wait_for_timeout(300)
    out["panel_gueltig"] = p.evaluate("() => { const b = [...document.querySelectorAll('.tw-cmpanel button')].find(x => x.innerText.includes('Hinweis zur Prüfung einreichen')); return b ? !b.disabled : null; }")
    p.keyboard.press("Escape"); p.wait_for_timeout(300)
    out["panel_zu"] = p.evaluate("() => !document.querySelector('.tw-cmpanel')")
    # Mobil
    p.set_viewport_size({"width": 390, "height": 800}); p.wait_for_timeout(1200)
    p.locator(".tw-main button", has_text="Hinweis erstellen").first.click(timeout=5000); p.wait_for_timeout(500)
    out["mobil"] = p.evaluate("() => { const q = document.querySelector('.tw-cmpanel'); const g = document.querySelector('.tw-cmgrid'); return { panel_breite: q ? Math.round(q.getBoundingClientRect().width) : null, vollbild: q ? Math.round(q.getBoundingClientRect().width) >= 388 : null, spalten: g ? getComputedStyle(g).gridTemplateColumns.split(' ').length : null }; }")
    out["fehler"] = fehler[:6]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
