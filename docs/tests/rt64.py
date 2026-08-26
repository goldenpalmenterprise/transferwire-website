import json, time
from playwright.sync_api import sync_playwright
out = {}; fehler = []
VIEWS = ["Newsfeed", "Transfers", "Vereinsbedarf", "Performance", "Spieler", "Vertragsenden", "Merkliste", "Scouting", "Community"]
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    # Mobil
    ctx = b.new_context(viewport={"width": 390, "height": 800}, is_mobile=True, has_touch=True)
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de");')
    p = ctx.new_page()
    p.on("pageerror", lambda e: fehler.append("PE: " + str(e)[:200]))
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000); p.wait_for_timeout(5000)
    out["marker"] = p.evaluate("() => (document.documentElement.outerHTML.match(/tw-build:[^>]{0,50}/)||['?'])[0]")
    audit = {}
    for v in VIEWS:
        p.locator(".tw-burger").click(timeout=5000); p.wait_for_timeout(300); p.locator(".tw-mobnav button", has_text=v).click(timeout=5000)
        try: p.wait_for_function("() => !document.querySelector('.tw-skel')", timeout=25000)
        except Exception: pass
        p.wait_for_timeout(2500)
        audit[v] = p.evaluate("""() => { const w = window.innerWidth; const scrollbar = e => { const cs = getComputedStyle(e); return /(auto|scroll)/.test(cs.overflowX); }; const inScroller = e => { let x = e.parentElement; while (x && x !== document.body) { if (scrollbar(x)) return true; x = x.parentElement; } return false; };
          const bad = [...document.querySelectorAll('.tw-main *')].filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.right > w + 1 && getComputedStyle(e).position !== 'fixed' && !inScroller(e); }).slice(0, 4).map(e => e.tagName.toLowerCase() + '.' + (typeof e.className === 'string' ? e.className.split(' ')[0] : '') + ' ' + Math.round(e.getBoundingClientRect().right) + 'px "' + (e.innerText || '').slice(0, 25).replace(/\\n/g, ' ') + '"');
          const h2 = document.querySelector('.tw-main h2'); const p = h2 ? h2.nextElementSibling : null;
          return { scrollWidth: document.documentElement.scrollWidth, ausserhalb: bad, h2: h2 ? getComputedStyle(h2).fontSize : null, beschreibung: p ? getComputedStyle(p).fontSize : null, karten_breit: [...document.querySelectorAll('.tw-main .tw-card')].filter(c => c.getBoundingClientRect().width > w).length }; }""")
    out["audit"] = audit
    ctx.close()
    # Desktop-Vergleich: Kopf und Tab-Leiste unveraendert
    ctx2 = b.new_context(viewport={"width": 1600, "height": 950})
    ctx2.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de");')
    d = ctx2.new_page(); d.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000); d.wait_for_timeout(5000)
    out["desktop"] = d.evaluate("""() => { const hw = document.querySelector('.tw-headwrap'); const b = document.querySelector('.tw-burger'); return { burger_weg: !b || getComputedStyle(b).display === 'none', tabs: document.querySelectorAll('.tw-tabs button').length, tabbar_sichtbar: getComputedStyle(document.querySelector('.tw-tabbar')).display !== 'none', kopf_hoehe: Math.round(hw.getBoundingClientRect().height), live_sichtbar: getComputedStyle(document.querySelector('.tw-livetime')).display !== 'none', h2: (() => { const h = document.querySelector('.tw-main h2'); return h ? getComputedStyle(h).fontSize : null; })(), feed_spalten: (() => { const g = document.querySelector('.tw-feedlist'); return g ? getComputedStyle(g).gridTemplateColumns.split(' ').length : null; })() }; }""")
    out["fehler"] = fehler[:5]
    print(json.dumps(out, ensure_ascii=False))
    b.close()
