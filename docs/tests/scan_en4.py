import json, time, re
from playwright.sync_api import sync_playwright
GER = re.compile(r'[äöüßÄÖÜ]|\b(und|oder|für|mit|von|vom|der|die|das|den|dem|des|ein|eine|einen|einem|nicht|kein|keine|Verein|Vereine|Vereins|Spieler|Liga|Ligen|suchen|Suche|alle|Alle|noch|Noch|jetzt|Jetzt|bei|Bei|zum|zur|nach|wird|werden|ist|sind|hier|Hier|dein|deine|Dein|Deine|neu|Neu|laden|Laden|mehr|Mehr|Woche|Tage|Tag|heute|gestern|Gestern|Heute|Uhr|Min|Std|Bitte|bitte|Keine|Kein|Alter|Marktwert|Marktwerte|Vertrag|Vertragsenden|Gerücht|Meldung|Meldungen|Wechsel|Leihe|sucht|gesucht|Prüfung|Verletzung|Talent|Talente|Bedarf|Kader|Saison|Tor|Tore|Vorlagen|Minuten|Einsätze|Antwort|Sekunden|täglich|Blitzsuche|Entdecke|abgedeckt|Abgleich|letzte|Letzte|aus|auf|im|am|an|über|unter|zwischen|wenn|dann|auch|nur|schon|ab|bis|seit|durch|gegen|ohne|um|als|wie|so|sehr|viel|viele|wenig|kaum|erst|noch|wieder|immer|nie|oft|manchmal|Zurück|weiter|Weiter|Öffnen|öffnen|Schließen|schließen|Speichern|speichern|Löschen|löschen|Abbrechen|Senden|senden|Anfrage|Anfragen|Hinweis|Hinweise|Beitrag|Beiträge|Mitglied|Mitglieder|Konto|Zugang|Abo|Monat|Jahr|Preis|kostenlos|Test|Woche)\b')
out = {"views": {}, "strings": []}; seen = set(); fehler = []
JS = """() => { const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); const res = new Set(); let n;
  const vis = el => { if (!el) return false; const r = el.getBoundingClientRect(); const cs = getComputedStyle(el); return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none'; };
  while ((n = w.nextNode())) { const t = n.textContent.replace(/\\s+/g, ' ').trim(); if (t.length >= 2 && vis(n.parentElement)) res.add(t); }
  document.querySelectorAll('input,textarea').forEach(e => { if (e.placeholder) res.add('[ph] ' + e.placeholder); });
  document.querySelectorAll('[title]').forEach(e => { if (e.title && vis(e)) res.add('[title] ' + e.title); });
  return [...res]; }"""
def sammeln(p, name):
    neu = []
    for t in p.evaluate(JS):
        if t not in seen:
            seen.add(t); neu.append(t)
    out["views"][name] = len(neu); out["strings"] += [(name, t) for t in neu]
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1600, "height": 950})
    ctx.add_init_script('localStorage.setItem("tw_account", JSON.stringify({email:"laurenzrath@gmx.de", code:"TWT-2JCT3", plan:"test", start: Date.now(), name:"Laurenz"})); localStorage.setItem("tw_tour","1"); localStorage.setItem("tw_lang","en");')
    p = ctx.new_page()
    p.on("pageerror", lambda e: fehler.append(str(e)[:150]))
    p.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000)
    p.wait_for_timeout(5000)
    sammeln(p, "feed")
    def tab(name, wait=2500):
        try: p.locator(".tw-tabs button", has_text=name).first.click(timeout=6000); p.wait_for_timeout(wait); return True
        except Exception as e: fehler.append("tab " + name + ": " + str(e)[:80]); return False
    def klick(sel, name, wait=2000):
        try: p.locator(sel, has_text=name).first.click(timeout=5000); p.wait_for_timeout(wait); return True
        except Exception as e: fehler.append("klick " + name + ": " + str(e)[:80]); return False
    tab("Transfers"); sammeln(p, "transfers")
    tab("Club needs"); sammeln(p, "bedarf_kacheln")
    klick(".tw-main .tw-tile", "Right-back") or klick(".tw-main .tw-tile", "Rechtsverteidiger"); sammeln(p, "bedarf_liste")
    tab("Performance"); sammeln(p, "performance")
    tab("Players"); sammeln(p, "players")
    try:
        p.locator(".tw-main input").first.fill("Kane"); p.wait_for_timeout(2500); sammeln(p, "players_suche")
        p.locator(".tw-main .tw-card").first.click(timeout=4000); p.wait_for_timeout(2500); sammeln(p, "players_drawer")
        p.keyboard.press("Escape"); p.wait_for_timeout(800)
    except Exception as e: fehler.append("players: " + str(e)[:80])
    tab("Openings"); sammeln(p, "openings")
    tab("Watchlist"); sammeln(p, "watchlist")
    tab("Scouting"); sammeln(p, "scouting")
    for sub in ["Scouting lists", "Lists", "Listen", "Rankings", "Ranking"]:
        if klick(".tw-main button", sub, 2000): sammeln(p, "scouting_" + sub)
    tab("Community"); sammeln(p, "community")
    klick(".tw-main button", "Networking"); sammeln(p, "networking")
    klick(".tw-main button", "Moderation"); sammeln(p, "moderation")
    # Feed-Detail: erste Karte anklicken
    tab("News feed")
    try:
        p.locator(".tw-main .tw-card").first.click(timeout=4000); p.wait_for_timeout(2000); sammeln(p, "feed_detail"); p.keyboard.press("Escape"); p.wait_for_timeout(600)
    except Exception as e: fehler.append("detail: " + str(e)[:80])
    # Avatar-Menü / Einstellungen
    try:
        p.locator("header button").last.click(timeout=4000); p.wait_for_timeout(1500); sammeln(p, "menu")
    except Exception as e: fehler.append("menu: " + str(e)[:80])
    # KI-Scout-Chat öffnen
    try:
        p.get_by_text("TW", exact=True).last.click(timeout=4000); p.wait_for_timeout(1500); sammeln(p, "chat")
    except Exception as e: fehler.append("chat: " + str(e)[:80])
    ctx.close()
    # Ausgeloggt: Landing / Login
    ctx2 = b.new_context(viewport={"width": 1600, "height": 950}); ctx2.add_init_script('localStorage.setItem("tw_lang","en");')
    q = ctx2.new_page(); q.goto("https://transferwire.de/?v=" + str(int(time.time())), wait_until="domcontentloaded", timeout=25000); q.wait_for_timeout(4000)
    for t in q.evaluate(JS):
        if t not in seen: seen.add(t); out["strings"].append(("landing", t))
    try:
        q.get_by_text("Login", exact=False).first.click(timeout=4000); q.wait_for_timeout(1500)
        for t in q.evaluate(JS):
            if t not in seen: seen.add(t); out["strings"].append(("login", t))
    except Exception as e: fehler.append("login: " + str(e)[:80])
    b.close()
import urllib.request
src = urllib.request.urlopen("https://transferwire.de/?src=" + str(int(time.time()))).read().decode("utf-8")
LIT = set()
for raw in re.findall(r'"((?:[^"\\]|\\.)*)"', src):
    try: LIT.add(json.loads('"' + raw + '"').strip())
    except Exception: pass
i = src.find("const I18N = {"); j = src.find("\nfunction t(k)")
blk = src[i:j]; m = re.search(r'\n  en: \{(.*?)\n  \}', blk, re.S)
ENV = set()
if m:
    for raw in re.findall(r':\s*"((?:[^"\\]|\\.)*)"', m.group(1)):
        try: ENV.add(json.loads('"' + raw + '"').strip())
        except Exception: pass
def rel(t):
    t2 = t.replace("[ph] ", "").replace("[title] ", "")
    return t2 in LIT and t2 not in ENV and re.search(r"[A-Za-zÄÖÜäöüß]{2}", t2) and not re.fullmatch(r"[a-z0-9_]+", t2)
ui = [(v, t) for v, t in out["strings"] if rel(t)]
daten = [(v, t) for v, t in out["strings"] if not rel(t) and GER.search(t)]
out["ui"] = len(ui); out["daten_deutsch"] = len(daten)
ger = [(v, t) for v, t in ui if GER.search(t.replace("[ph] ","").replace("[title] ","")) and not re.search(r"\b(FC|SV|SK|SC|TSV|VfB|VfL|SG|FK|Austria Wien|Sturm Graz|Real|Atl|Borussia|Bayern|Fortuna|Hertha|Union|Eintracht|Werder|Hamburger|Holstein|Mainz|Freiburg|Heidenheim|Hoffenheim|Bochum|St\. Pauli|Rapid|Salzburg|LASK|Ried|Hartberg|Tirol|Altach|Klagenfurt|Wolfsberg|Lustenau|Blau|Linz|Wien|Graz|Lugano|Luzern|Basel|Sion|Zürich|Lausanne|Yverdon|Winterthur|Servette|Grasshopper|Thun|Aarau|Schaffhausen|Bellinzona|Stade|Vaduz|Kickers|Preußen|Rot-Weiss|Alemannia|Saarbrücken|Aue|Regensburg|Ingolstadt|Ulm|Cottbus|Osnabrück|Verl|Wehen|Sandhausen|Havelse|Hannover|Essen|Mannheim|Bielefeld|Elversberg|Fürth|Nürnberg|Karlsruhe|Braunschweig|Kaiserslautern|Magdeburg|Paderborn|Darmstadt|Dresden|Düsseldorf|Schalke|Köln|Münster|Kiel|Lübeck|Rostock|Duisburg|Dortmund|Leverkusen|Bremen|Stuttgart|Augsburg|Leipzig|Wolfsburg|Gladbach|Frankfurt|Mönchengladbach|Zwolle|Sittard|Waregem|Brügge|Löwen|Kortrijk|Genk|Gent|Anderlecht|Antwerpen|Mechelen|Westerlo|Charleroi|Standard|Lüttich|Eyüpspor|Göztepe|Kasımpaşa|Konyaspor|Samsunspor|Trabzonspor|Fenerbahçe|Beşiktaş|Galatasaray|Kayserispor|Alanyaspor|Gaziantep|Rizespor|Sivasspor|Hatayspor|Antalyaspor|Başakşehir|Adana|Bodrum|Kocaelispor|Karagümrük|Süper Lig|Serie|Liga|League|Ligue|Ere|Pro League|Superliga|Primeira|Championship|Bundesliga)\b", t)]
out["gesamt"] = len(out["strings"]); out["deutsch"] = len(ger); out["fehler"] = fehler[:8]
print(json.dumps({k: out[k] for k in ["gesamt", "ui", "daten_deutsch", "fehler"]}, ensure_ascii=False))
print("=== NOCH DEUTSCH (UI, ohne Vereins-/Liganamen) ===")
for v, t in ger: print(t[:170])
print("=== DATEN-TEXTE DEUTSCH (Auszug) ===")
for v, t in daten[:30]: print(v + " | " + t[:110])
