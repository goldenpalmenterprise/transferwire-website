import json, time, re
from playwright.sync_api import sync_playwright
out = {}; fehler = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1600, "height": 950})
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de"); localStorage.removeItem("tw_watch"); localStorage.removeItem("tw_recent"); localStorage.removeItem("tw_notes");')
    p = ctx.new_page()
    p.on("pageerror", lambda e: fehler.append("PE: " + str(e)[:200]))
    p.on("console", lambda m: fehler.append("CE: " + m.text[:200]) if m.type == "error" and "Failed to load resource" not in m.text else None)
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000)
    p.wait_for_timeout(5000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    p.locator(".tw-tabs button", has_text="Merkliste").first.click(timeout=6000); p.wait_for_timeout(3000)
    out["leer"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const t = m.innerText; const a = m.querySelector('aside'); return { titel: (m.querySelector('h2')||{}).innerText, beschreibung: t.includes('Verfolge Spieler, Vereine und Meldungen. Änderungen bei Form, Vertrag, Verletzungen und Transfers werden automatisch angezeigt.'), tabs: [...m.querySelectorAll('.tw-mktabs button')].map(b => b.innerText.replace(/\\n/g,' ')), leer_titel: t.includes('Deine Merkliste ist noch leer'), leer_text: t.includes('Speichere Spieler, Vereine oder Transfermeldungen, um Änderungen automatisch zu verfolgen und Alerts zu erhalten.'), buttons: ['Spieler entdecken','Suchprofil erstellen'].every(x => t.includes(x)), empfohlen: t.includes('Empfohlen für dich') || /EMPFOHLEN FÜR DICH/.test(t), karten: ['Top-Performer der Woche','Neue vertragslose Spieler','Vereine mit aktuellem Positionsbedarf'].every(x => t.includes(x)), aside: a ? { alerts: a.innerText.includes('Deine Alerts'), keine: a.innerText.includes('Keine aktiven Alerts'), text: a.innerText.includes('Erhalte Benachrichtigungen bei neuen Transfermeldungen, Vertragsänderungen, Verletzungen und Veränderungen des TW-Scores.'), button: a.innerText.includes('Alert erstellen'), zuletzt: /ZULETZT ANGESEHEN|Zuletzt angesehen/.test(a.innerText), meist: a.innerText.includes('Meistdiskutierte') } : 'KEIN ASIDE', chips: [...m.querySelectorAll('.tw-chip')].map(c => c.innerText.trim()).slice(0, 6) }; }""")
    # Alert erstellen -> Dialog
    try:
        p.locator(".tw-main aside button", has_text="Alert erstellen").first.click(timeout=5000); p.wait_for_timeout(600)
        out["alert_dialog"] = p.evaluate("() => { const els = [...document.querySelectorAll('div')].filter(d => getComputedStyle(d).position === 'fixed' && /E-Mail|Alert|Benachrichtig/i.test(d.innerText)); return els.length ? els[0].innerText.split('\\n').slice(0, 3).join(' | ').slice(0, 100) : 'KEIN DIALOG'; }")
        p.keyboard.press("Escape"); p.wait_for_timeout(300)
        for txt in ["Später", "Schließen", "Nein"]:
            try: p.locator("button", has_text=txt).first.click(timeout=600); break
            except Exception: pass
    except Exception as e: out["alert_dialog"] = str(e)[:100]
    # Empfehlung klicken -> Navigation
    p.locator(".tw-main button", has_text="Top-Performer der Woche").first.click(timeout=5000); p.wait_for_timeout(1500)
    out["nav"] = p.evaluate("() => (document.querySelector('.tw-main h2')||{}).innerText || document.querySelector('.tw-main').innerText.split('\\n')[0]")
    # Spieler beobachten (Performance-Seite: Beobachten in der Karte) -> zurueck zur Merkliste
    try:
        p.wait_for_selector(".tw-perf-main", timeout=20000)
        p.locator(".tw-perf-main button", has_text="Beobachten").first.click(timeout=5000); p.wait_for_timeout(1000)
        for txt in ["Später", "Schließen", "Nein", "Ohne"]:
            try: p.locator("button", has_text=txt).first.click(timeout=600); break
            except Exception: pass
        p.keyboard.press("Escape")
        p.locator(".tw-tabs button", has_text="Merkliste").first.click(timeout=6000)
        p.wait_for_function("() => { const r = document.querySelector('.tw-mkrow'); return r && !/…/.test(r.innerText); }", timeout=30000); p.wait_for_timeout(4000)
        out["zeile"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const r = m.querySelector('.tw-mkrow'); const t = m.innerText; return { tabs: [...m.querySelectorAll('.tw-mktabs button')].map(b => b.innerText.replace(/\\n/g,' ')), kopf: (m.querySelector('.tw-mkhead')||{innerText:''}).innerText.replace(/\\n/g,' | '), zeile: r ? r.innerText.replace(/\\n/g,' | ').slice(0, 220) : null, aktionen: r ? [...r.querySelectorAll('button')].map(b => b.innerText) : null, leer_weg: !t.includes('Deine Merkliste ist noch leer'), aside_aktiv: (m.querySelector('aside')||{innerText:''}).innerText.includes('Alerts') }; }""")
        # Notiz + Alert aus + Entfernen
        p.once("dialog", lambda d: d.accept("Für Kapfenberg prüfen"))
        p.locator(".tw-mkrow button", has_text="Notiz").first.click(timeout=5000); p.wait_for_timeout(500)
        p.locator(".tw-mkrow button", has_text="Alert an").first.click(timeout=5000); p.wait_for_timeout(600)
        out["notiz_alert"] = p.evaluate("() => { const r = document.querySelector('.tw-mkrow'); return { notiz: r.innerText.includes('Für Kapfenberg prüfen'), alert_aus: r.innerText.includes('Alert aus'), stumm: (document.querySelector('.tw-main aside')||{innerText:''}).innerText.includes('stumm') }; }")
        p.locator(".tw-mkrow button", has_text="Entfernen").first.click(timeout=5000); p.wait_for_timeout(800)
        out["entfernt"] = p.evaluate("() => !document.querySelector('.tw-mkrow')")
    except Exception as e: out["zeile_fehler"] = str(e)[:160]
    # Mobil
    p.set_viewport_size({"width": 390, "height": 800}); p.wait_for_timeout(1200)
    out["mobil"] = p.evaluate("() => { const m = document.querySelector('.tw-main'); const tabs = m.querySelector('.tw-mktabs'); const a = m.querySelector('aside'); const inhalt = m.querySelector('.tw-merk'); return { tabs_scroll: tabs ? tabs.scrollWidth > tabs.clientWidth : null, aside_unten: a && inhalt ? a.getBoundingClientRect().top >= inhalt.getBoundingClientRect().bottom - 2 : null, empf_einspaltig: (() => { const g = m.querySelector('.tw-mk-empf'); return g ? getComputedStyle(g).gridTemplateColumns.split(' ').length === 1 : null; })() }; }")
    out["fehler"] = fehler[:6]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
