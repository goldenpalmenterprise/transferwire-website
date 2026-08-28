# rt71: Mobile-Suchfeld unter der Kopfzeile, volle Headerbreite, Placeholder wie Web; Desktop unveraendert
import asyncio, time
from playwright.async_api import async_playwright

URL = "https://transferwire.de/?v=" + str(int(time.time()))
PH_DE = "Frag die TW KI-Suche \u2014 Spieler, Vereine, Transfers \u2026"

INIT = 'localStorage.setItem("tw_account", JSON.stringify({email:"tw-premium-test@transferwire.de", code:"TW-PREMTEST99", plan:"premium", start: Date.now(), name:"Premium Test"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","de"); localStorage.setItem("tw_chat","[]");' 

async def lauf(pw, breite, hoehe, name):
    b = await pw.chromium.launch(args=["--no-sandbox"])
    ctx = await b.new_context(viewport={"width": breite, "height": hoehe},
                              user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15" if breite < 700 else None)
    pg = await ctx.new_page()
    await pg.add_init_script(INIT)
    await pg.goto(URL, wait_until="domcontentloaded", timeout=60000)
    await pg.wait_for_timeout(7000)

    marker = await pg.evaluate("""() => { const m = document.documentElement.outerHTML.match(/tw-build: ([0-9a-z-]+)/); return m ? m[1] : 'fehlt'; }""")

    mess = await pg.evaluate("""() => {
      const inp = document.getElementById('tw-gsuche');
      if (!inp) return { fehler: 'kein input' };
      const box = inp.closest('.tw-gsuche-box');
      const wrap = document.querySelector('.tw-headwrap');
      const logo = document.querySelector('.tw-logo');
      const rb = box.getBoundingClientRect();
      const rw = wrap.getBoundingClientRect();
      const rl = logo.getBoundingClientRect();
      const cs = getComputedStyle(wrap);
      const innenBreite = rw.width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      // Placeholder-Textbreite in echter Input-Schrift messen
      const ics = getComputedStyle(inp);
      const pcs = getComputedStyle(inp, '::placeholder');
      const sp = document.createElement('span');
      sp.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap;font:' + ics.font + ';font-size:' + pcs.fontSize + ';letter-spacing:' + pcs.letterSpacing;
      sp.textContent = inp.placeholder;
      document.body.appendChild(sp);
      const phBreite = sp.getBoundingClientRect().width;
      sp.remove();
      return {
        placeholder: inp.placeholder,
        boxTop: Math.round(rb.top), boxBreite: Math.round(rb.width),
        logoUnten: Math.round(rl.bottom),
        innenBreite: Math.round(innenBreite),
        rechtsLuecke: Math.round((rw.right - parseFloat(cs.paddingRight)) - rb.right),
        inputBreite: Math.round(inp.getBoundingClientRect().width),
        phBreite: Math.round(phBreite),
        fontSize: ics.fontSize, phFont: pcs.fontSize
      };
    }""")

    # Funktionscheck: Enter oeffnet Panel
    await pg.fill('#tw-gsuche', 'Murat Satin')
    await pg.press('#tw-gsuche', 'Enter')
    await pg.wait_for_timeout(4500)
    panel = await pg.evaluate("""() => { const p = document.querySelector('.tw-ki-panel'); return p ? Math.round(p.getBoundingClientRect().width) : 0; }""")

    unterHeader = mess.get('boxTop', 0) >= mess.get('logoUnten', 9e9)
    volleBreite = abs(mess.get('boxBreite', 0) - mess.get('innenBreite', -1)) <= 3
    phPasst = mess.get('phBreite', 9e9) <= mess.get('inputBreite', 0) + 1
    print(name, "| marker=" + marker,
          "| unterHeader=" + str(unterHeader),
          "| boxBreite=" + str(mess.get('boxBreite')) + "/" + str(mess.get('innenBreite')),
          "| rechtsLuecke=" + str(mess.get('rechtsLuecke')),
          "| font=" + str(mess.get('fontSize')) + "/ph" + str(mess.get('phFont')),
          "| phGleich=" + str(mess.get('placeholder') == PH_DE),
          "| phPasst=" + str(phPasst) + " (" + str(mess.get('phBreite')) + "/" + str(mess.get('inputBreite')) + ")",
          "| panel=" + str(panel))
    await b.close()

async def main():
    async with async_playwright() as pw:
        await lauf(pw, 1280, 900, "DESKTOP")
        await lauf(pw, 390, 844, "MOBILE ")
        await lauf(pw, 360, 780, "MOBIL36")

asyncio.run(main())
