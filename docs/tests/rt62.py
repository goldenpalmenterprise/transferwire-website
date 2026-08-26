import json, time
from playwright.sync_api import sync_playwright
out = {}; fehler = []
VIEWS = ["Newsfeed", "Transfers", "Vereinsbedarf", "Performance", "Spieler", "Vertragsenden", "Merkliste", "Scouting", "Community"]
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 390, "height": 800}, is_mobile=True, has_touch=True, device_scale_factor=2)
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de");')
    p = ctx.new_page()
    p.on("pageerror", lambda e: fehler.append("PE: " + str(e)[:200]))
    p.on("console", lambda m: fehler.append("CE: " + m.text[:200]) if m.type == "error" and "Failed to load resource" not in m.text else None)
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000)
    p.wait_for_timeout(6000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    out["header"] = p.evaluate("""() => { const b = document.querySelector('.tw-burger'); const hw = document.querySelector('.tw-headwrap'); return { burger_sichtbar: b && getComputedStyle(b).display !== 'none', burger_links: b ? Math.round(b.getBoundingClientRect().left) : null, tabbar_weg: !document.querySelector('.tw-tabbar') || getComputedStyle(document.querySelector('.tw-tabbar')).display === 'none', kopf_hoehe: hw ? Math.round(hw.getBoundingClientRect().height) : null, kopf_passt: hw ? [...hw.querySelectorAll('*')].every(e => e.getBoundingClientRect().right <= 392) : null, live_weg: !document.querySelector('.tw-livetime') || getComputedStyle(document.querySelector('.tw-livetime')).display === 'none' }; }""")
    p.locator(".tw-burger").click(timeout=5000); p.wait_for_timeout(500)
    out["menue"] = p.evaluate("() => { const n = document.querySelector('.tw-mobnav'); return n ? { eintraege: [...n.querySelectorAll('button')].map(b => b.innerText.trim()).filter(x => x && x !== '✕'), breite: Math.round(n.getBoundingClientRect().width), links: Math.round(n.getBoundingClientRect().left), symbole: [...n.querySelectorAll('button span:first-child')].map(s => s.innerText.trim()).filter(Boolean).length } : 'KEIN MENUE'; }")
    p.locator(".tw-mobnav button", has_text="Vertragsenden").click(timeout=5000); p.wait_for_timeout(1500)
    out["nav_klick"] = p.evaluate("() => ({ menue_zu: !document.querySelector('.tw-mobnav'), titel: (document.querySelector('.tw-main h2')||{}).innerText })")
    # Overflow-Audit je Seite
    audit = {}
    for v in VIEWS:
        p.locator(".tw-burger").click(timeout=5000); p.wait_for_timeout(300)
        p.locator(".tw-mobnav button", has_text=v).click(timeout=5000)
        try: p.wait_for_function("() => !document.querySelector('.tw-skel')", timeout=25000)
        except Exception: pass
        p.wait_for_timeout(2500)
        audit[v] = p.evaluate("""() => { const w = window.innerWidth; const sw = document.documentElement.scrollWidth; const bad = [...document.querySelectorAll('.tw-main *')].filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && (r.right > w + 1 || r.left < -1) && getComputedStyle(e).position !== 'fixed'; }).slice(0, 6).map(e => (e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.split(' ')[0] : '') + ' ' + Math.round(e.getBoundingClientRect().right) + 'px "' + (e.innerText || '').slice(0, 30).replace(/\\n/g, ' ') + '"')); const h2 = document.querySelector('.tw-main h2'); return { scrollWidth: sw, innerWidth: w, ueberlauf: sw > w, treffer: bad, h2: h2 ? Math.round(parseFloat(getComputedStyle(h2).fontSize)) : null, nebeneinander: (() => { const m = document.querySelector('.tw-main'); return m ? getComputedStyle(m).gridTemplateColumns.split(' ').filter(x => x !== '0px').length : null; })() }; }""")
    out["audit"] = audit
    out["fehler"] = fehler[:6]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
