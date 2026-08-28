# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright

ACC = 'localStorage.setItem("tw_account", JSON.stringify({email:"tw-premium-test@transferwire.de", code:"TW-PREMTEST99", plan:"premium", start: Date.now(), name:"Premium Test"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de"); localStorage.setItem("tw_chat","[]");'

def lauf(pw, breite, hoehe, tag):
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={"width": breite, "height": hoehe})
    ctx.add_init_script(ACC)
    p = ctx.new_page()
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000)
    p.wait_for_timeout(7000)
    aus = [tag]
    aus.append("marker=" + str(p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build: ([0-9a-z-]+)/) || ['','?'])[1]")))
    aus.append("fab=" + str(p.evaluate("() => document.querySelectorAll('.tw-fab').length")))
    aus.append("bubble=" + str(p.evaluate("() => document.body.innerText.includes('Frag den TW Scout')")))
    # Scout-Leiste im Feed + Chat oeffnen
    aus.append("leiste=" + str(p.evaluate("() => [...document.querySelectorAll('button')].some(b => b.textContent.trim() === 'Scout fragen')")))
    p.evaluate("() => { const b = [...document.querySelectorAll('button')].find(x => x.textContent.trim() === 'Scout fragen'); if (b) b.click(); }")
    p.wait_for_timeout(1200)
    aus.append("chatpanel=" + str(p.evaluate("() => document.body.innerText.includes('KI-Scout')")))
    try:
        p.fill("input[placeholder*='Frag den Scout']", "Kurzer Test")
        p.keyboard.press("Enter")
        p.wait_for_timeout(9000)
        aus.append("chatwartung=" + str(p.evaluate("() => document.body.innerText.includes('Wartung')")))
    except Exception as e:
        aus.append("chatfehler=" + str(e)[:60])
    p.evaluate("() => { const b = [...document.querySelectorAll('button')].find(x => (x.getAttribute('aria-label') || '') === 'Schliessen' || x.textContent.trim() === '\u00d7'); if (b) b.click(); }")
    p.wait_for_timeout(600)
    # Header-KI-Suche
    fs = p.evaluate("() => { const i = document.getElementById('tw-gsuche'); return i ? getComputedStyle(i).fontSize : '?'; }")
    aus.append("suchfont=" + str(fs))
    p.fill("#tw-gsuche", "Murat Satin")
    p.keyboard.press("Enter")
    p.wait_for_timeout(11000)
    aus.append("panel=" + str(p.evaluate("() => document.querySelectorAll('.tw-ki-panel').length")))
    aus.append("panelbreit=" + str(p.evaluate("() => { const x = document.querySelector('.tw-ki-panel'); return x ? Math.round(x.getBoundingClientRect().width) : 0; }")))
    t = p.evaluate("() => { const x = document.querySelector('.tw-ki-panel'); return x ? x.innerText.slice(0, 900) : ''; }")
    aus.append("antwort_wartung=" + str("Wartung" in t))
    aus.append("treffer_satin=" + str("Murat Satin" in t))
    aus.append("treffer_fix=" + str("WSG Tirol" in t))
    br.close()
    return " | ".join(aus)

with sync_playwright() as pw:
    print(lauf(pw, 1280, 900, "DESKTOP"))
    print(lauf(pw, 390, 844, "MOBILE"))
