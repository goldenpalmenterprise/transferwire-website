import json, time, re
from playwright.sync_api import sync_playwright
out = {}; fehler = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1600, "height": 950}, accept_downloads=True)
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de"); localStorage.removeItem("tw_lists"); localStorage.removeItem("tw_listmeta");')
    p = ctx.new_page()
    p.on("pageerror", lambda e: fehler.append("PE: " + str(e)[:200]))
    p.on("console", lambda m: fehler.append("CE: " + m.text[:200]) if m.type == "error" and "Failed to load resource" not in m.text else None)
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000)
    p.wait_for_timeout(5000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    p.locator(".tw-tabs button", has_text="Scouting").first.click(timeout=6000); p.wait_for_timeout(1500)
    p.locator(".tw-main button", has_text="Scouting-Listen").first.click(timeout=6000)
    p.wait_for_function("() => { const k = [...document.querySelectorAll('.tw-likarte')]; return k.length && k.every(c => !/…/.test(c.innerText)); }", timeout=40000); p.wait_for_timeout(1500)
    out["kopf"] = p.evaluate("""() => { const m = document.querySelector('.tw-main'); const t = m.innerText; return { titel: (m.querySelector('.tw-listen h2')||{}).innerText, beschreibung: t.includes('Kuratierte Rankings aus der Spieler-Datenbank und eigene dynamische Listen mit deinen Filtern und Alerts.'), button: (() => { const b = [...m.querySelectorAll('button')].find(x => x.innerText.trim() === '+ Neue Scouting-Liste'); return b ? { farbe: getComputedStyle(b).backgroundColor, rechts: b.getBoundingClientRect().right > m.getBoundingClientRect().right - 80 } : null; })(), tabs: [...m.querySelectorAll('.tw-litabs button')].map(b => b.innerText.replace(/\\n/g,' ')), rot: [...m.querySelectorAll('.tw-listen *')].filter(e => { const cs = getComputedStyle(e); return /rgb\\(1[6-9]\\d, (7\\d|8\\d|4\\d), (5\\d|6\\d|4\\d|3\\d)\\)/.test(cs.backgroundColor) || /rgb\\(176, 74, 58\\)/.test(cs.borderLeftColor); }).length }; }""")
    out["karten"] = p.evaluate("""() => { const k = [...document.querySelectorAll('.tw-likarte')]; const g = document.querySelector('.tw-ligrid'); return { anzahl: k.length, spalten: g ? getComputedStyle(g).gridTemplateColumns.split(' ').length : null, karte0: k[0] ? k[0].innerText.replace(/\\n/g,' | ').slice(0, 260) : null, fotos0: k[0] ? k[0].querySelectorAll('img, span[style*="border-radius: 99px"]').length : null, alle_mit_button: k.every(c => c.innerText.includes('Liste öffnen')), alle_mit_zahl: k.every(c => /\\d+ Spieler/.test(c.innerText)), alle_mit_stand: k.every(c => /Zuletzt aktualisiert: /.test(c.innerText)), status: k.map(c => (c.innerText.match(/KURATIERT|PRIVAT|GETEILT/)||[''])[0]), alerts: k.filter(c => /ALERT INAKTIV/.test(c.innerText)).length }; }""")
    # Menue
    p.locator(".tw-likarte button[aria-label='Listenaktionen']").first.click(timeout=5000); p.wait_for_timeout(400)
    out["menue"] = p.evaluate("() => [...document.querySelectorAll('.tw-likarte button')].map(b => b.innerText.trim()).filter(x => /^(Öffnen|Duplizieren|Teilen|Exportieren|Alert aktivieren|Alert deaktivieren|Löschen)$/.test(x))")
    p.locator(".tw-likarte button", has_text="Duplizieren").first.click(timeout=5000); p.wait_for_timeout(800)
    out["dupliziert"] = p.evaluate("() => { const m = document.querySelector('.tw-main'); return { tabs: [...m.querySelectorAll('.tw-litabs button')].map(b => b.innerText.replace(/\\n/g,' ')), karte: (m.querySelector('.tw-likarte')||{innerText:''}).innerText.replace(/\\n/g,' | ').slice(0, 120), hinweis: (m.innerText.match(/Liste nach[^\\n]*/)||[''])[0] }; }")
    # Alert aktivieren + Teilen + Loeschen auf der eigenen Liste
    p.locator(".tw-likarte button[aria-label='Listenaktionen']").first.click(timeout=5000); p.wait_for_timeout(300)
    p.locator(".tw-likarte button", has_text="Alert aktivieren").first.click(timeout=5000); p.wait_for_timeout(500)
    p.locator(".tw-likarte button[aria-label='Listenaktionen']").first.click(timeout=5000); p.wait_for_timeout(300)
    p.locator(".tw-likarte button", has_text="Teilen").first.click(timeout=5000); p.wait_for_timeout(500)
    out["alert_teilen"] = p.evaluate("() => { const c = document.querySelector('.tw-likarte'); return { alert: /ALERT AKTIV/.test(c.innerText), geteilt: /GETEILT/.test(c.innerText), tabs: [...document.querySelectorAll('.tw-litabs button')].map(b => b.innerText.replace(/\\n/g,' ')) }; }")
    p.locator(".tw-litabs button", has_text="Geteilte Listen").first.click(timeout=5000); p.wait_for_timeout(500)
    out["geteilt_tab"] = p.evaluate("() => document.querySelectorAll('.tw-likarte').length")
    p.locator(".tw-litabs button", has_text="Meine Listen").first.click(timeout=5000); p.wait_for_timeout(400)
    try:
        with p.expect_download(timeout=10000) as dl:
            p.locator(".tw-likarte button[aria-label='Listenaktionen']").first.click(timeout=5000); p.wait_for_timeout(300)
            p.locator(".tw-likarte button", has_text="Exportieren").first.click(timeout=5000)
        out["export"] = dl.value.suggested_filename
    except Exception as e: out["export"] = str(e)[:80]
    p.once("dialog", lambda d: d.accept())
    p.locator(".tw-likarte button[aria-label='Listenaktionen']").first.click(timeout=5000); p.wait_for_timeout(300)
    p.locator(".tw-likarte button", has_text="Löschen").first.click(timeout=5000); p.wait_for_timeout(700)
    out["leer"] = p.evaluate("() => { const t = document.querySelector('.tw-main').innerText; return { titel: t.includes('Noch keine eigenen Scouting-Listen'), text: t.includes('Erstelle eine dynamische Liste und lasse neue passende Spieler automatisch hinzufügen.'), button: t.includes('Neue Liste erstellen') }; }")
    # Neue Liste -> Formular (unveraendert)
    p.locator(".tw-main button", has_text="Neue Liste erstellen").first.click(timeout=5000); p.wait_for_timeout(500)
    out["formular"] = p.evaluate("() => { const m = document.querySelector('.tw-main'); return { inputs: [...m.querySelectorAll('input')].map(i => i.placeholder || i.type), selects: [...m.querySelectorAll('select')].map(s => [...s.options].map(o => o.text).slice(0, 3).join('/')), labels: [...m.querySelectorAll('label')].map(l => l.innerText.split('\\n')[0].trim()).slice(0, 8), buttons: [...m.querySelectorAll('button')].map(b => b.innerText.trim()).filter(x => /Speichern|Abbrechen/.test(x)) }; }")
    p.locator(".tw-main button", has_text="Abbrechen").first.click(timeout=5000); p.wait_for_timeout(400)
    # Liste oeffnen -> Listenansicht (unveraendert)
    p.locator(".tw-litabs button", has_text="Empfohlen").first.click(timeout=5000); p.wait_for_timeout(300)
    p.locator(".tw-likarte button", has_text="Liste öffnen").first.click(timeout=5000); p.wait_for_timeout(4000)
    out["liste"] = p.evaluate("() => { const t = document.querySelector('.tw-main').innerText; return { zurueck: t.includes('← Alle Listen'), titel: t.includes('Top 50 U21-Talente Europa'), eintraege: (t.match(/#\\d+/g)||[]).length }; }")
    # Mobil
    p.locator(".tw-main button", has_text="← Alle Listen").first.click(timeout=5000); p.wait_for_timeout(600)
    p.set_viewport_size({"width": 390, "height": 800}); p.wait_for_timeout(1500)
    out["mobil"] = p.evaluate("() => { const g = document.querySelector('.tw-ligrid'); const tabs = document.querySelector('.tw-litabs'); return { spalten: g ? getComputedStyle(g).gridTemplateColumns.split(' ').length : null, breite: g ? Math.round(g.querySelector('.tw-likarte').getBoundingClientRect().width) : null, tabs_scroll: tabs ? tabs.scrollWidth > tabs.clientWidth : null }; }")
    out["fehler"] = fehler[:6]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
