# TransferWire – Stufe 3 Fortschritt (Fortsetzung 24.08.2026, Session ab ~13:30 UTC)

Vorgeschichte: siehe Übergabe-Briefing 24.08. ~06:00 (Mobil, Sprachwähler/Dark-Mode, OG, Posteingang, Community ~95%).
Arbeitsweise: Repo geklont nach /home/claude/site, Push via Boss-PAT (fine-grained, nur transferwire-website, Contents R/W;
hinterlegt in /home/claude/.git-credentials, chmod 600, stammt aus Chat "Serverumzug Stufe 3" vom 16.08.).
Tests laufen auf dem Server im Container tm-fetcher über Admin-Shell-WF umhYeTVuKBNB2Z3u.
Übergabe von Testskripten: Base64 → `echo <b64> | docker exec -i tm-fetcher sh -c 'base64 -d > /tmp/x.py && python3 /tmp/x.py'`
(umgeht die Heredoc-/Escape-Falle komplett; lokale Kopien in /home/claude/tests/).

## 24.08. 13:30 – rt10d ausgeführt (Exec 7778)
- Ergebnis rot: Community-View leer (h2 "", textarea false, Luettich false), Networking-Pille nicht gefunden, 0 pageerrors.
- Nebenbefund: sed-Marker-Patch in rt10d gescheitert (`unknown option to 's'` – Pipe-Delimiter vs. `||` im Regex) → rt10d = rt10c.
- Live-Marker per curl: 2026-08-24-zd → KEIN Cache-Problem, Bug echt.

## 24.08. 13:34 – Diagnose rt10e (Exec 7785) → Ursache gefunden
- Nach Klick auf Tab "Community": `.tw-main` = null, `.tw-tabs` leer → App unmounted, TwBoundary-Fallback.
- Konsole: `TypeError: Failed to set an indexed property [0] on 'CSSStyleDeclaration'`.
- Ursache im Code: Community/Networking-Karten nutzten `style: Object.assign({}, CARD, {...})`,
  aber `CARD` ist in index.html der Farbstring "#ffffff" (Z. 1538), kein Style-Objekt.
  Object.assign kopiert die Zeichen als Keys 0..6 → React setzt style[0] → Crash → Boundary → "leere" View.
  Der Fehler ist KEIN pageerror (React fängt ihn), darum zeigten rt10c/d 0 Fehler.

## 24.08. 13:38 – Fix gepusht: Commit d598695, Marker 2026-08-24-ze card-style-fix
- `const CARD_BOX = { background: CARD, border: "1px solid " + HAIR, borderRadius: 14 };` (Z. 1539)
- 5 Stellen `Object.assign({}, CARD, {` → `Object.assign({}, CARD_BOX, {` (Community-Formular, Info-Posts, Networking-Formular, Networking-Posts, Premium-Gate).
- node --check auf allen Inline-Script-Blöcken grün.
- Abnahme: rt10f (Tab-Klick über `.tw-tabs button`, Marker, Community-Checks, Networking-Gate, Konsolenfehler, 4xx-URLs).

## Lektionen
- `get_by_text("Community", exact=True)` in rt10c traf zwar den Tab, aber die View-Prüfung sah nur `.tw-main` – bei einem
  Boundary-Fallback sieht das wie "leer" aus. Künftig in Tests immer auch `main: !!document.querySelector('.tw-main')`
  und Konsolen-Errors (nicht nur pageerror) mitloggen.
- Style-Konstanten in index.html: HAIR/CARD/PAGE/INK sind FARBSTRINGS. Karten-Style = CARD_BOX.

## 24.08. 13:40 – Abnahme rt10f (Exec 7795) GRÜN
Marker ze live · Community-View vollständig (h2, Textarea, "Hinweis senden", Amber-Banner, Pillen) · Post 1 "Standard Luettich" sichtbar
mit Chip "Im Feed" · Networking-View: h2, Gold-Button, kein Formular (Gate greift) · FeedSuche/Feedkarten in Community ausgeblendet ·
0 Konsolen-/Page-Errors · 4xx nur gstatic faviconV2 (Google-Favicon-Dienst für Quellenlogos, extern, harmlos).
Zwei Scheinbefunde geklärt:
- "Nur im Premium-Abo" nicht gefunden → Element hat textTransform uppercase, innerText = "NUR IM PREMIUM-ABO". Test künftig case-insensitiv.
- "KV Kortrijk" nicht sichtbar → Post 2 ist kind=networking (Premium-Liste), Test-Konto sieht dort korrekt das Gate. Kein Bug.

## Datenstand Community (DB + API, Exec 7806)
- Post 1: kind info, status veroeffentlicht, agent_type verein_sucht, published_news_id cmty-1.
- Post 2: kind networking, status neu (Premium-Testkonto), erscheint in API kind=networking nur mit Premium-Code.
- Analyst-WF Z0xO8t9jEp0ffJdW: Exec 7493 um 06:05 UTC REAL mit gpt-5.5 gelaufen (762 Tokens, 163 Reasoning), publish → Feed
  cmty-1 "Standard Lüttich sucht: linker Verteidiger", reliability 1, source "TW Community (ungeprueft)", Post markiert.
  Seit 07:05 stündlich ~40 ms success (nichts zu tun). → OpenAI-Credits sind offenbar geladen; Livedemo damit erledigt.

## 24.08. 13:48 – Feed-Verifikation cmty-1 (Exec 7813) GRÜN
n8n-DB Transfernews: news_id cmty-1, type verein_sucht, reliability 1, source_name "TW Community (ungeprueft)", league Belgische Pro League.
Feed-DOM (rt10g): 1.687 Karten geladen, cmty-1 an Position 124, Kartentext: "Verein sucht | Belgische Pro League | vor 8 Std |
Standard Lüttich sucht: linker Verteidiger | Laut Community-Hinweis … | VEREINSBEDARF | Standard Lüttich | linker Verteidiger |
kleines Budget, Leihe bevorzugt | Spekulation". Quelle "TW Community" ist auf der Karte NICHT sichtbar (nur "Spekulation" + Konjunktiv-
Summary) → Badge-Idee hat echten Mehrwert. Anker für Badge: "Unbest\u00e4tigt" (escaped!) in index.html Z. 1785 und 2432.
Nebenbefund: FeedSuche-Aside enthält kein input/select (asideInputs = []) → Testselektor ".tw-main aside input" ist falsch; Suche sitzt im Header.

## STATUS COMMUNITY: 100 % live und abgenommen (Frontend ze, API 5QyzGceCwIANV4nq aktiv, Analyst Z0xO8t9jEp0ffJdW aktiv, Agent-Livelauf 06:05 UTC bestätigt).
Testskripte (lokal /home/claude/tests, auf Server /tmp): rt10e Diagnose, rt10f Abnahme Community/Networking, rt10g Feed-Scan.

## OFFEN / IDEEN (Reihenfolge = Empfehlung)
1. Lila COMMUNITY-Badge in NewsCard (Anker gefunden) – ~30 Min.
2. Feed-Paginierung "Mehr laden" 60er – Feed rendert aktuell 1.687 Karten auf einmal – ~1 h, wichtig für Mobil/Launch.
3. Melde-Button an Community-Posts (Status gemeldet + Mail info@) – ~45 Min.
4. Admin-Moderationsansicht (Liste + freigeben/ablehnen, Boss-only) – ~1,5 h.
5. Upvotes/Reputation – nach Launch (eigene Tabelle votes, GRANT tw_app!).
6. rt-Tests: Checks case-insensitiv, Konsolenfehler mitloggen, main-Existenz prüfen.
PENDING BOSS (aus Briefing): n8n-Cloud kündigen bis ~29.08. · Stripe Testkauf 49 € + alten 60 €-Link deaktivieren · Hetzner-2FA ·
GitHub-PAT rotieren (steht im Klartext im Chat vom 16.08.) · OpenAI-Credits: laut Agent-Lauf 06:05 vorhanden → Backlog-Sprint 971 Signale startklar.

## 24.08. 14:05–14:45 – COMMUNITY 1.1 (Paket vom Boss freigegeben, Auto-Freigabe durch Agent beibehalten)
### Frontend (3 Pushes)
- 9af450a / Marker zf: Lila Badge "👥 Community · ungeprüft" in NewsCard, NeedCard, MeldungsPanel (istCommunity: id cmty-* oder Quelle /community/i).
  Feed-Paginierung: FEED_SEITE=60, "Mehr laden (x von y)"-Pille, Reset bei Filter-/View-Wechsel. Community-Tab aktiv bei networking/moderation.
- 08da669 / Marker zg: ADMIN_EMAILS=['laurenzrath@gmx.de'] (Frontend nur Anzeige, Server prüft), CmtyChip (neu/prueft/veroeffentlicht/notiert/
  freigegeben/abgelehnt/gemeldet/zurueckgezogen), MeldeButton (nur Fremdbeiträge, disabled wenn gemeldet_von_mir), Networking: eigene Gesuche
  zeigen Chip statt Kontakt-Button. View "moderation" (dritte Pille 🛡 nur für Admins): Filter Alle/Gemeldet/Info/Networking/Abgelehnt/Offen,
  Karten mit KI-Label/Begründung/Melder/Notiz/Feed-ID, Aktionen Zurückziehen (confirm + Notiz-Prompt) / Freigeben / Neu prüfen.
  Sende-Erfolgsmeldung angepasst + Reload nach 9 s und 25 s (Sofortprüfung). Guards für moderation in Wrapper/Filterleiste/Aside/newsfilter.
- 2ed76bb / Marker zh: Positions-Keywords LV/RV/IV um Varianten ("linker/rechter verteidiger", EN) erweitert.
### DB (Migration 14:09): community_posts + updated_at, meldungen, admin_note, agent_headline, feed_json; Tabelle community_reports
  (UNIQUE post_id+reporter_email, CASCADE) + GRANTs tw_app + Sequence; Index (status, created_at).
### Analyst v2 (Z0xO8t9jEp0ffJdW, publiziert): Trigger "Sofort-Start" (executeWorkflowTrigger passthrough) + Cron :05; Claim-Query
  neu→prueft (prueft älter 20 Min wird erneut geclaimt); Prompt mit KIND info/networking, approve/reject für Networking, position_needed als
  Standardname (Torwart…Trainer); Meldungen formen schreibt agent_headline + feed_json, baut Autor-Mails; Posts markieren erweitert;
  Mails aufteilen → Autor-Mail (SMTP info@, onError continue). Livetests: Post 2 approve (Mail an nicht existentes Testpostfach 550 → ok),
  Post 3 (VfB RV) publish in 12 s, Mail an laurenzrath@gmx.de queued.
### API v2 (5QyzGceCwIANV4nq, publiziert): Liste = Fremdbeiträge nur veroeffentlicht/notiert/freigegeben, eigene immer; Felder own,
  gemeldet_von_mir, meldungen, agent_headline. POST → Anlage antworten → Nur bei Erfolg → Sofort pruefen (executeWorkflow, wait=false).
### Moderations-API (NEU B9z8s4orPk55Fzf9, publiziert, Credentials explizit gesetzt):
  POST /api/tw-community-report {email,code,post_id,grund} → community_reports (1×/Nutzer), meldungen+1, ab 3 → status gemeldet + Feed-Zeile
  gelöscht, Mail an info@ (→ Boss). Antworten ok / doppelt / auth.
  GET /api/tw-community-admin?email&code → alle Posts (gemeldet zuerst) inkl. agent_note, melder, hat_feed. Nur ADMINS-Whitelist (im Code-Node).
  POST /api/tw-community-admin {aktion: zurueckziehen|freigeben|neu_pruefen, note} → Status + Feed-Delete/Re-Insert aus feed_json;
  neu_pruefen startet Analyst sofort. Volltest 14:33 grün (Exec 7860), Testmeldung zurückgesetzt.
### Abnahme rt11 (Exec 7872) GRÜN: Marker zg, Feed 60→120 von 1697, Badge cmty-3, Community-Pillen inkl. Moderation, Chips, Melden nur fremd,
  Moderation 3 Karten + Aktionen, Premium: Networking-Chip ✓ Online, kein Kontakt-Button am eigenen Gesuch, 0 Fehler.
  Offen: rt11b Vereinsbedarf-Kacheln (RV cmty-3, LV cmty-1) nach Keyword-Fix.
- rt11b (Exec 7914) GRÜN: Vereinsbedarf-Kachel Rechtsverteidiger zeigt cmty-3 (VfB) mit Badge, Kachel Linksverteidiger zeigt cmty-1
  (Standard Lüttich, "linker Verteidiger" via neuem Keyword) mit Badge. NeedCard rendert KEINE Headline (Verein + Position + Summary) →
  Tests auf Vereinsnamen matchen. Kachelzähler zählen Vereine, nicht Bedarfe.
- 14:52 cmty-3 (Claude-Testhinweis über VfB) per Admin-Aktion zurueckziehen aus Feed entfernt; feed_json bleibt → "Freigeben (in Feed)" stellt wieder her.

## STATUS 24.08. 14:55: COMMUNITY 1.1 LIVE UND ABGENOMMEN
Frontend Marker zh (Commits 9af450a, 08da669, 2ed76bb) · Analyst v2 Z0xO8t9jEp0ffJdW · API v2 5QyzGceCwIANV4nq · Moderation B9z8s4orPk55Fzf9.
Testskripte lokal /home/claude/tests (rt10e/f/g, rt11, rt11b, mod_test.sh), auf Server /tmp/*.py.
Admin-Whitelist: ADMIN_EMAILS (Frontend, nur Anzeige) + ADMINS in Code-Nodes "Auth (Admin-Liste)"/"Auth (Admin-Aktion)" (Server, maßgeblich).
Zum Erweitern beide Stellen pflegen.

## IDEEN COMMUNITY 1.2 (nach Launch)
- Spielerprofil-Verknüpfung: Agent matcht player_name gegen players (15.006) → Hinweis am Profil (SpielerDrawer).
- Dubletten-/Bestätigungs-Check: gleiche Meldung aus Sportmonks/RSS vorhanden → Einstufung anheben ("Community + Presse").
- Deal-Matching im Networking: Angebot (Stürmer) ↔ Gesuch (Verein sucht Stürmer) automatisch verknüpfen, Premium-Mehrwert.
- Upvotes/Reputation (Tabelle votes, GRANT tw_app).
- Autor-Mail zusätzlich auf EN, wenn Beitrag englisch geschrieben.

## 24.08. 14:55–15:20 – BACKLOG + KOSTENKALIBRIERUNG + MODELL-MIX (WICHTIG)
- Backlog 971 Signale: bereits abgearbeitet (nur 23 offene, alle aus der laufenden Stunde; 7.505 in 7 Tagen verarbeitet). Kein Sprint nötig.
- FALLE ENTDECKT: Der nächtliche Qualitäts-Mix (~02:12, SQL auf workflow_entity.nodes + n8n-Restart) war NIE aktiv. n8n führt die
  publizierte Version aus workflow_history (activeVersionId) aus. Beweis: Analyst-Lauf 14:20 antwortete mit gpt-5-mini-2025-08-07.
  → NIE Modelle per SQL setzen. Immer update_workflow (echte Node-Änderung nötig, sonst keine Versionsrotation!) + publish_workflow.
  Trick bei "Entwurf hat schon den Zielwert": setNodePosition um 1px erzwingt eine neue Version.
- PREISE (verifiziert OpenAI-Doku 24.08.): gpt-5.5 = 5 $/M in, 30 $/M out (cached 0,50); gpt-5-mini 0,25/2; gpt-5.6-terra 2/12; luna 0,20/1,20.
  Nacht-Schätzung "Analyst 5.5 ≈ 1,80 €/Tag" war falsch: gemessen 17,3k in / 8,0k out je Lauf (davon ~4,9k Reasoning) → 0,33 $/Lauf
  → 7,8 $/Tag (24 Läufe), ≈ 31 $/Tag an Launch-Tagen (Cron :20 + :05/:35/:50 am 30./31.8. und 1./2.9.).
- Messung 24h (Regex über execution_data, prompt_tokens + promptTokens): Analyst 224k/104k (13 Läufe), Kaderstärken 67k/27k (1 Lauf, 7 Calls),
  Voll-Leser 28k/16k (1 Lauf, 30 Calls), Verletzungs-Scout 25k/13,5k, Markt-Scout 8k/3,4k, Kaderlücken 1,2k/2,4k (2), Community 1,8k/0,8k.
  Modellnamen sind in execution_data nicht per Regex greifbar (flatted-Referenzen) → aus workflow_history lesen.
- UMGESETZT + PUBLIZIERT 15:15–15:17: mini für Kaderstärken v2 (3 Modell-Nodes), Verletzungs-Scout v2 (3), Performance-Analyst, Voll-Leser
  (Redaktion), Markt-Scout (2 Code-Nodes), Kontakt-Scout (Code-Node) → spart ≈ 1,9 $/Tag. Bedarfs-Radar auf gpt-5.5 (1×/Tag, Kosten morgen messen).
  Signal-Analyst: gpt-5-mini BEHALTEN + EN-Fix aus dem Entwurf live (Upsert bewahrt headline_en/summary_en bei unveränderter Headline/Summary).
  Gerüchte-Suche bleibt mini (nutzerseitig, Traffic unbekannt). Kaderlücken bleibt 2×/Tag (0,08 $/Tag, Drosselung nicht nötig).
- Kosten jetzt: ≈ 1,2 $/Tag gemessen + Nacht-Agenten (Radar 5.5 offen) → deutlich unter 6 €/Tag.
- OFFEN (Boss-Entscheidung): Analyst-Qualität. Optionen: gpt-5.6-terra ≈ 3,1 $/Tag (Launch 12,5 $); 5.5 mit reasoning_effort low ≈ 4,6 $
  (Launch 18 $); mini + Prompt/Reasoning-Tuning ≈ 0,5 $. Empfehlung: A/B derselben Signal-Charge mini vs. terra, Launch-Extra-Läufe auf 2/Std.
- Entwurfs-Tabelle (workflow_entity.nodes) für Gerüchte-Suche enthält noch gpt-5.5 aus dem SQL → bei künftigen Updates dieses Workflows
  Modell bewusst auf mini setzen (sonst rutscht 5.5 in die nächste Version).

## 24.08. 15:20–15:55 – ANALYST-ENTSCHEIDUNG: gpt-5.6-terra
- 15:20-Lauf mit mini + EN-Fix grün (Exec 7952: 52 Signale → 15 Meldungen, Upsert ok).
- A/B-Workflow lpq85TUpim7ZcrV6 "TW Test: Analyst A/B mini vs terra (manuell)" (Exec 7972, dieselben 52 Signale):
  mini 13 Cluster / 16 Signale, 6.735 out (4.224 Reasoning), 0,016 $ · terra 16 Cluster / 19 Signale, 2.460 out (359 Reasoning), 0,045 $,
  Quellen in Summaries, konservativere Reliability (3,06 vs 3,38), 2 Talente statt 1, Status-Einstufung korrekter (Tunde geruecht statt fix).
- UMGESETZT 15:5x: Analyst ifOFnqTVjThmiFEJ auf gpt-5.6-terra (Version 9cb78146), Launch-Extra-Crons von "5,35,50" auf "50" (2 Läufe/Std. am
  30./31.8., 1./2.9.). Erwartung ≈ 1,70 $/Tag normal, ≈ 3,40 $/Tag Launch. Rückweg: vorherige Version (e78dfb6b, mini) publizieren.
- Hinweis terra: cache_write_tokens erscheint (Prompt-Caching, Writes 1,25×, 30-Min-Cache) – im Stundenlauf kaum Wirkung, an Launch-Tagen (30-Min-Takt) günstiger.
- Kontrolle: 16:20-Lauf muss model "gpt-5.6-terra" zeigen und success sein.

## 24.08. 17:05 – Kontrollen
- Analyst 16:20 (Exec 7997) mit gpt-5.6-terra GRÜN: 54 Signale → 26 Meldungen (mini: 15 aus 52), 8.556 in / 3.639 out ≈ 0,06 $.
- Parallel-Session hat 16:58/17:00 Networking-Wording ("Frage / Angebot", "Anfrage veröffentlichen", "Anfragen") + Stichwort-Suche
  (Networking + Transfer-Infos, alle Wörter, diakritik-/umlaut-insensitiv) gepusht (Commits 776fbec, 3540008, Marker zj).
  rt12 live GRÜN (Exec 8039): Kortrijk 1 Treffer, "Stürmer"/"stuermer" je 1, zwei Wörter 1, Unsinn 0 + "Keine Treffer", kein "Gesuch" mehr, 0 Fehler.
- Antworten in Networking = "Kontakt aufnehmen" → Vermittlungsmail über info@ mit replyTo des Anfragenden; keine In-App-Kommentare (bewusst).
- 17:2x: Parallel-Session Commit b1b95d5 (Marker zk) "Antworten"-Button an fremden Transfer-Info-Karten + API-Version 17:18 (Kontakt für Info-Posts
  ohne Premium-Pflicht). rt13 live GRÜN (Exec 8073, Premium-Test): Karte zeigt "↩ Antworten | ⚑ Melden", Prompt-Text, Alert "✓ Antwort zugestellt";
  Testantwort ging real an laurenzrath@gmx.de. 0 Fehler.
- HINWEIS: Es läuft eine Parallel-Session auf demselben Repo/n8n → vor jedem Push git pull, vor Workflow-Änderungen aktive Version prüfen.
- 18:35 (dieses Fenster, ab jetzt einziges aktives): Commit d5bf443 / Marker zl: AntwortButton-Komponente, einheitlich "↩ Antworten" in Transfer-Infos
  UND Networking (statt "Kontakt aufnehmen"); eigene Beiträge zeigen den Button ausgegraut mit Tooltip ("Antworten anderer erreichen dich per E-Mail").
  Networking nutzt jetzt antwortSenden (Nachricht Pflicht ≥3 Zeichen). rt14 GRÜN (Exec 8146): Infos 1 aktiv (fremd), Networking 2 ausgegraut (eigene), 0 Fehler.
- 18:40: Boss-Wunsch: Button heißt wieder "✉ Kontakt aufnehmen" (Infos + Networking, eigene Beiträge ausgegraut), Prompt "Deine Nachricht an den Autor",
  Bestätigung "Kontaktanfrage zugestellt". Commit 3703ce1 / Marker zm.
  Alle Test-Community-Beiträge (1–4) + Reports + Feed-Einträge cmty-* gelöscht, Sequenzen auf 1 zurückgesetzt → Community ist leer und launchbereit.
  rt15 GRÜN (Exec 8159): Feed ohne Community-Karten, Infos/Networking zeigen Leerzustand, 0 Fehler. Formular-Platzhalter (Beispieltexte im Eingabefeld) bewusst behalten.

## 24.08. 18:55–19:45 – VOLLSTÄNDIGE ENGLISCHE VERSION + FR/ES ENTFERNT
Ausgangslage: t()/I18N deckte ~310 Schlüssel ab, aber Hunderte Texte standen direkt im Code; Feed-/Bedarfs-Details zeigten in EN deutsche Felder.
Vorgehen: Playwright-Scanner /tmp/scan_en*.py (lokal /home/claude/tests) sammelt in EN alle sichtbaren Texte aller Ansichten (Feed, Transfers,
Bedarf-Kacheln+Liste, Performance, Players+Drawer, Openings, Watchlist, Scouting+Listen, Community/Networking/Moderation, Detail-Panel, Landing)
und schneidet sie mit den Code-Literalen → "UI-Text" vs. "Datentext".
### Umsetzung (Commits de67fa9 → 4220a2b, Marker zn…zq)
- EN-Übersetzungsschicht direkt nach `let LANG = "de";`: EN_MAP (221 Einträge, JSON), EN_COUNTRIES, EN_WORDS (Positions-/Ablöse-/Status-Fragmente,
  Unicode-Lookarounds), EN_RULES (vor N Min/Std/Tg, Live · …, Mehr laden (x von y), N Meldungen/Einträge/Treffer/Vereine/Anfragen/Hinweise,
  "· N J. ·" → y/o, "Vereine, die einen X suchen", "N bis M …"), twEnShort (nur ≤90 Zeichen mit deutschem Marker), twEn(), Patch von
  React.createElement: übersetzt String-Kinder + placeholder/title/aria-label NUR bei DOM-Elementen (typeof type === "string") und nur bei LANG==="en".
  Lektionen: (1) Kinder eigener Komponenten NICHT übersetzen (Crash), (2) Regex mit [\s\S] für mehrzeilige Texte + null-Guard,
  (3) Schlüssel immer aus dem echten Code-Literal nehmen (Scan-Ausgabe war gekürzt → Community-Beschreibung matchte nicht).
- Wörterbuch pflegen: /home/claude/i18n/en_map.json (Quelle), Einbau als JSON-Block `const EN_MAP = {...}` in index.html (json.loads-validiert).
- EN-Felder: MeldungsPanel dS(m), Spieler-Drawer dH(n), NeedCard dS(item), GerVue-Kompaktliste dH(it), Landing-Vorschau dH/dS(f).
- FR/ES: I18N.fr/es gelöscht (~20 KB), Umschalter ["de","en"], tw_lang fr/es → en, t()-Fallback entfernt.
- Übersetzer ZFTqK4CLBSTgxEeQ: Cron von stündlich :40 auf "25,55 * * * *" (folgt Analyst :20 / Launch :50), publiziert 19:32.
  DB-Abdeckung headline_en: 1.797/1.799 (Rest = laufende Stunde).
### Tests
- rt16 (Exec 8229): EN lädt, Tabs englisch, Umschalter DE/EN, 0 Fehler. rt18 (Exec 8274): Live-Toggle DE→EN→DE ohne Reload, DE unverändert.
- scan_en4 (Exec 8261): UI-Restliste nur Vereinsnamen/Demo-Name/bereits englische Sätze; Datentexte deutsch = frische Meldungen vor dem Übersetzer-Lauf.
### Grenzen
- Lange deutsche KI-Fließtexte OHNE EN-Feld in anderen Tabellen (ältere Bedarfsbegründungen im Kaderlücken-Detail, Performance-Notizen,
  Scout-Chat-Antworten, Community-Beiträge = Nutzertext) werden nicht übersetzt. Weg: Übersetzer-WF auf diese Tabellen ausweiten (Boss-Entscheidung).
- 19:55 erster Übersetzer-Lauf im neuen Takt (Exec 8283, success): 0 von 1.814 Meldungen ohne EN → Feed in EN vollständig englisch.

## 24.08. 20:00–20:20 – COMMUNITY: ÜBERSETZEN-BUTTON (jede Sprache → Englisch)
- DB: community_posts + body_en, body_lang (Cache).
- NEU Workflow C9Ez5ibrTSolSkOv "TW Community – Übersetzer API (Webhook)": POST /api/tw-community-translate {email, code, post_id} → Auth (jedes
  aktive Konto) → Post laden → Cache? → sonst gpt-5-mini (reasoning_effort low, JSON {lang, text_en}; alles übersetzen außer Eigennamen)
  → speichern → {ok, text_en, lang}. Erstaufruf ≈ 3,4 s, Cache 0,2 s. Credentials explizit gesetzt, publiziert.
  Lektion: ohne reasoning_effort low brauchte gpt-5-mini 17 s / 1.344 Denk-Tokens für zwei Zeilen; Prompt "Positionen exakt behalten" ließ
  "lateral izquierdo"/"enero" unübersetzt → Prompt: nur Eigennamen behalten.
- Frontend Commit 2d9d45f / Marker zr: UebersetzenButton ("🌐 Auf Englisch" ↔ "Original anzeigen", "… Übersetze"), an Info- und Networking-
  Karten; Textkörper wechselt, Hinweis "🌐 Übersetzt aus ES"; Zustände cUe/cUeZeige/cUeLaedt; EN-Wörterbuch ergänzt. Moderationsansicht zeigt Original.
- rt19b (Exec 8324) GRÜN: spanische Anfrage → KI freigegeben → Klick → englischer Text + "Übersetzt aus ES" → "Original anzeigen" → Spanisch
  → erneuter Klick sofort (Cache). Testbeitrag gelöscht, Sequenz zurückgesetzt. 0 Fehler.

## 24.08. 20:25–20:35 – RESTBEREICHE DE/EN + !!! OPENAI-GUTHABEN LEER !!!
- Bedarfsbegründungen = summary der verein_sucht-Zeilen (inj-*/rss-*), summary_en vorhanden → seit NeedCard-dS-Fix englisch. Scan EN Club needs: nur 1 Quellenname deutsch.
- Performance-Ansicht: 1.033 sichtbare Texte, 0 deutsch. Chat-Workflow sgfKNfoJTTGGwEuX parst lang und setzt "Antworte auf Englisch/Deutsch" → bereits zweisprachig.
- KRITISCH: OpenAI API antwortet seit ~20:15 UTC mit 429 credit_balance_exhausted ("You have no credits remaining"). Analyst 20:20 error,
  Chat-Test 20:31 error. Betroffen: Signal-Analyst, EN-Übersetzer, Community-Prüfer (Posts bleiben in prueft → Cron-Retry), Übersetzen-Button,
  Scout-Chat, alle Nacht-Agenten. Boss muss Guthaben laden (+ Auto-Recharge). Danach holen Analyst (:20, LIMIT 150) und Übersetzer (:25/:55) automatisch auf.

## 24.08. 21:05–21:35 – KOSTENPROBLEM GEFUNDEN + BEHOBEN (Boss: 50 € an einem Tag, Ziel ≤ 6 €/Tag)
Ursache: Erste Messung zählte nur prompt_tokens/promptTokens; Responses-API (Web-Suche) meldet input_tokens/output_tokens → unsichtbar.
n8n speichert Execution-Daten "flatted": Strings (Modellnamen, "web_search_call") stehen dedupliziert in einer Stringtabelle → per Regex
NICHT zählbar; Zahlen (Tokens) sind inline → zählbar. Modell daher aus workflow_history der aktiven Version ableiten.
### Verbraucher (24 h, alle Formate)
- Bedarfs-Scout Deutschland 4BjusAxYNt1uvLue: 1 Lauf, 466 Aufrufe (!), 11,47 Mio in / 1,55 Mio out, 10 h Laufzeit → ≈ 10,6 $/Tag mit mini
  (+ Web-Suche 0,01 $/Aufruf); 7 Tage: 25,2 Mio in. Code: "Variante 1: täglich ALLE Länder" = 466 Vereine aus 14 Ländern, ohne search_context_size/max_tokens.
  Auf gpt-5.5 wäre EIN Lauf > 100 $ (erklärt die 50 €).
- Vertrags-Scout 3MzOmjVwt8GaLvAs (So 5:00): 20 Liga-Recherchen gpt-5.5 + Web-Suche, 1,39 Mio in → ≈ 9 $/Lauf.
- Radar qoJpIltSvfTGt3Iw: 656k in / 84k out je Lauf → mit gpt-5.5 (heute Nachmittag gesetzt!) 5,80 $/Nacht; zurück auf mini = 0,33 $.
### Umgesetzt (alle publiziert, aktive Version geprüft)
- Bedarfs-Scout: Rotation (DE i%3==tag%3, INTL idx%7==tag%7 → ~77/Tag), tools web_search search_context_size 'low', reasoning effort low,
  max_output_tokens 900; Launch-Extra-Crons 18:30 entfernt. Erwartung ≈ 1 $/Tag. Mechanik: Entwurf per SQL (jsonb_set + Dollar-Quoting
  /tmp/bedarf_fix.py) → setNodePosition → publish (Version wird aus Entwurf gebaut).
- Vertrags-Scout: mini, search_context_size medium, reasoning low, max_output_tokens 2500 → ≈ 0,4 $/Woche.
- Radar: gpt-5-mini (Version 1dcd732c) – VOR 22:00 publiziert. (Boss-Nachtvorgabe "Radar auf 5.5" verworfen: Kostenziel geht vor.)
- NEU Workflow NZzqmm9gWrQWu4N1 "TW Kosten-Wächter (täglich 23:50)": Postgres (n8n-DB) Regex-Aggregation 24 h aller Token-Formate + Modell/Web-Suche
  je aktivem Workflow → Code (Preisliste USD/M: 5.5=5/30, terra=2/12, mini=0,25/2, 4o-mini=0,15/0,6, 4o=2,5/10; Web-Suche 0,01 $/Aufruf; EUR ×0,92)
  → Mail an laurenzrath@gmx.de, Betreff mit ⚠ ab 6 €. Testlauf 21:30: 12,66 € (24 h) – Mail zugestellt. Preis je Workflow = aktuell aktives Modell (Näherung).
- Erwartung ab morgen: Analyst ≈ 1,6 $, Bedarfs-Scout ≈ 1 $, Nacht-Agenten ≈ 0,5 $, Rest Cent → ≈ 3 $/Tag ≈ 2,8 €.
### Boss-To-do (harte Sperre): OpenAI Settings → Limits → monatliches Budget-Limit (z. B. 180 $) + Warnschwelle 90 $ + Auto-Recharge klein halten.

## 24.08. 22:05–22:20 – SICHERHEITSAUDIT + HÄRTUNG (Boss-Auftrag)
Befund Server (Hetzner, Ubuntu 24.04, Kernel 6.8): nur 22/80/443 offen; Postgres/PostgREST/n8n nur im Docker-Netz; unattended-upgrades an;
n8n 2.33.7, Diagnostics aus, Executions 7 Tage; Postgres listen * aber nicht veröffentlicht; keine Firewall (ufw/iptables leer).
KRITISCH gefunden: sshd PermitRootLogin yes + PasswordAuthentication yes, KEIN authorized_key, 9.964 fehlgeschlagene Passwortversuche (Brute-Force
laufend), kein fail2ban; KEIN Backup. Admin-Shell = n8n SSH-Node mit Passwort (Cred eRJ5pak2iZbRe8R6) aus dem Docker-Netz (172.18.0.3).
Umgesetzt (Skript /home/claude/tests/harden.sh):
- fail2ban (jail.local: sshd aggressive, maxretry 4, findtime 10m, bantime 2h, ignoreip 127/8 + 172.16/12) → sofort 2 Bans.
- sshd: /etc/ssh/sshd_config.d/00-tw-hardening.conf (PasswordAuthentication no, MaxAuthTries 3, LoginGraceTime 20) + Match-Block am Ende von
  sshd_config (Address 172.16.0.0/12,127.0.0.0/8 → PasswordAuthentication yes) — nur weil 0 externe Passwort-Logins im Log. sshd -t ok, Restart ok,
  Admin-Shell danach verifiziert. FOLGE: Boss kann von außen NUR noch per SSH-Schlüssel (oder Hetzner-Konsole) → Key hinterlegen!
- Backup: /opt/transferwire/backup.sh (pg_dumpall beider DBs gzip + .env/compose, 14 Tage), Cron 03:30 root; erster Dump 1,3 GB ok.
- Netlify _headers (Commit 4ba7152): HSTS preload, X-Frame-Options DENY, nosniff, Referrer-Policy, Permissions-Policy, COOP — live geprüft.
Geprüft/ok: keine Schlüssel im Frontend oder Git-Historie; kein dangerouslySetInnerHTML/eval in der App; keine externen Skripte; Postgres-Queries der
Webhooks parametrisiert (einzige Interpolation: Analyst "Verarbeitet markieren" mit DB-IDs, kein Nutzereingang); Stripe-Webhook durch URL-Secret
(?key=twsec_…) geschützt (keine HMAC-Prüfung – Verbesserung möglich); Admin-Endpunkte Whitelist.
OFFEN (Boss): n8n-2FA aktivieren; OpenAI Budget-Limit; GitHub-Repo auf privat + PAT rotieren; Hetzner Cloud Firewall (22 nur eigene IP);
Off-Site-Backup (Storage Box); optional Cloudflare (Rate-Limit gegen Code-Brute-Force auf /api/tw-code); SSH-Key für eigenen Zugang.

## 24.08. 23:00–23:15 – FEED-FINISH (Boss-Wünsche), Commit 89466e0 / Marker zs
- Header: eine Live-Anzeige "● LIVE · aktualisiert vor X Min" (LIVE-Pill entfernt; EN-Regeln "updated N min ago"). Lektion: Regex auf einer
  langen Zeile hatte zuerst den ⌘K-Span erwischt → exakten Pill-String ersetzt.
- Seitenleiste: Zählung nutzte to_club/from_club (snake_case), Items sind camelCase → Liste war leer. Jetzt Top-5 nummeriert mit "N Updates",
  klickbar (Vereinsfilter), Logo/Monogramm; Leerzustand für gespeicherte Filter mit Beispielen.
- NewsCard: "⚠ Unbestätigt"-Chip entfernt; Karten flex-column + .tw-feedlist align-items stretch + Footer marginTop auto → gleiche Höhe je Reihe
  (geprüft: 227/227, 256/256); Share = Icon (nur bei Hover, .tw-hover-only), Watch = Bookmark-Icon mit Tooltip statt Pill.
- Transferzeile: Spieler-Meta ohne leere Felder (kein "· J ·" mehr), Vertragslos statt leerem Von-Verein, ClubLogo an beiden Vereinen, Ablöse in
  fester rechter Spalte (minWidth 92, nowrap).
- ClubLogo: lädt /api/tw-logos (Map Name→URL, existiert noch NICHT) sonst farbiges Monogramm. Logo-Quelle fehlt: keine Team-IDs/Logos in DB
  (fixtures/players nur Namen). Folgeaufgabe: API-Football /teams je Liga → Tabelle clubs(name, api_id, logo) + Alias-Matching → Webhook /tw-logos.
- rt21 GRÜN (Exec 8488): 0 Fehler.

## 25.08. 00:25–00:35 – DESIGN-SYSTEM RUNDE 1 (Boss-Dokument 1.1–1.3), Commits 8caece9 + c8ec2ca, Marker zt/zu
- Tokens (JS-Konstanten → wirken in allen Inline-Styles): INK #14181D, MUTED #667085, HAIR #E1E5E2, PAGE #F5F6F2; body #F5F6F2.
- Breite: .tw-main + Header + Tabs max 1440, padding 24/28, gap 24. Raster mit Seitenleiste 3fr/1fr (≈9/3), Spalte 24. Ohne (leere) aside
  volle Breite via :has() – gemessen: Feed/Merkliste 1020 px Inhalt + aside, Spieler/Performance/Vertragsenden 1384 px (voll).
- Karten: .tw-card radius 14, border #E1E5E2, padding 20/22, kein Schatten; Hover border #CFD7D1 + 0 8px 24px rgba(15,23,42,.06) + -1px.
  .tw-tile analog. Eingaben 44 px / radius 10 / border #E1E5E2. Titel: h2 direkt im View 30/38, Beschreibung 14.5 #667085 (Community geprüft).
  Spieler-Datenbank-Titel ist ein div mit 30px (bereits konform).
- NOCH OFFEN aus dem Dokument: 1.2 Titelzeile mit Hauptaktion rechts + "Umfang · Datenstand" je Seite (Markup je View), 1.4 einheitliche
  Filterleiste + Ergebniszähler/Sortierung/Ansicht, 1.5 Score-Namen (Performance/Talent/Match/Opportunity + Info-Symbol), 1.6 Statussystem
  (Farben/Belastbarkeit statt 3 Badges), 1.7 Leere Zustände mit Icon/Überschrift/Aktion.

## 25.08. 00:40–00:47 – DESIGN-SYSTEM 1.2 + 1.7, Commit 05c9373 / Marker zv
- 1.2: Kopfzeilen Spieler-Datenbank, Performance, Vertragsenden, Scouting-Listen: Titel 30/38 INK + marginBottom 6, Beschreibung 14.5/1.5 MUTED,
  Abstand 22 (gemessen Spieler: 30px/38px, 14.5px rgb(102,112,133)). Hauptaktion rechts + "Umfang · Datenstand" NICHT ergänzt (wäre neuer Inhalt /
  je View eigene Variablen) → offen, mit Boss klären.
- 1.7: Komponente EmptyState({icon,title,text,action,onAction,action2,onAction2}) = .tw-card zentriert (Rahmen solid, da .tw-card !important).
  Eingesetzt (10×): Merkliste, Spieler (pl_none), Performance (rank_empty), Scouting-Listen (li_none), Vertragsenden (3 Tabs), Community,
  Networking, Moderation. Feed-Filter-Leerzustand ("Keine Meldungen für diese Auswahl") NICHT umgestellt (anderes Markup). Bestehende Texte
  bleiben als Erklärung erhalten; neue Überschriften + EN-Wörterbuch ergänzt. Technik: Wrapper per Rückwärtssuche vom Textanker ersetzt
  (Muster waren mehrzeilig/Template-Literale). rt25: Community + Merkliste zeigen Icon/Überschrift/Erklärung zentriert, 0 Fehler.

## 25.08. 00:56–01:37 – DESIGN-SYSTEM 1.5 SCORE-NAMEN, Commits d9116b8 / 80515aa / d83d6fc, Marker zw/zx/zy (neuer Chat)
- Einstieg: /home/claude/stufe3_fortschritt.md fehlte (frische Umgebung) → Stand aus docs/FORTSCHRITT.md im Repo. Boss-PAT (16.08.-Chat) wieder in
  /home/claude/.git-credentials (600). Lokale Kopien: /home/claude/tests, /home/claude/i18n/en_map.json.
- Baustein (vor EmptyState): SCORES {performance, talent, match, opportunity} mit name/scale/de/en; ScoreInfo({kind,size}) = Info-Symbol "i"
  (currentColor, 15 px) → Klick-Popover (ReactDOM.createPortal an document.body, position fixed, z 1500, misst Höhe per useLayoutEffect und klappt
  nach oben, Breite min(300, vw-16), schließt bei Esc/Klick daneben/Scroll/Resize); ScoreName({kind}) = Name + Symbol; ScoreLegend({kind,style}) =
  Farbkästchen + Name + Symbol + "· Skala 0–100" (EN "scale"). Texte DE/EN direkt über LANG (nicht über EN_MAP).
- Umbenennung TW-Score → TW Performance Score: rank_sub, totw_sub, li_s_score, li_f_score ("Min. Performance Score"), pl_form, Listen-Preset
  sde/sen "abwehr", Chat-Vorschlag "Wie wird der TW Performance Score berechnet?", Panel Spieler des Spieltags ("TW PERFORMANCE SCORE" + Symbol,
  "So entsteht der TW Performance Score: …" + EN_MAP-Key/Value angepasst). Legenden: über der Performance-Liste, in der Kopfzeile jeder
  Scouting-Liste (Titel links, Legende rechts), Vereins-Dossier "Kader (nach Einsatzminuten) · TW Performance Score ⓘ", Spieler-Detail Formkurve ⓘ.
- Talent-Rankings: "TW-Score N" → "TW Talent Score N" (Kacheln + Zeilen), Kopfzeile flex mit ScoreLegend talent rechts.
- Match/Opportunity: NUR Definitionen im Baustein, nirgends gerendert – es gibt keine Zahl dafür (Match = profilOverlap-Zählung im Gesucht-View,
  Opportunity = nichts). Berechnung wäre neuer Inhalt → Boss-Entscheidung.
- Lektionen: (1) position:fixed innerhalb einer .tw-card wird durch das Hover-transform der Karte verschoben → Popover als Portal an body.
  (2) add_init_script setzt tw_lang bei JEDEM Reload → EN im Test nur per __twToggleLang('en') ohne Reload prüfen. (3) Spieler-Detail öffnet über
  Button "Profil" (openPlayer → plDetail-Overlay); Tabellenzeile (setPlSel) ist ein anderer Drawer. (4) Listen-Preset "Top 25 U23-Abwehrspieler
  Europa" liefert aktuell 0 Treffer (API count 0, Saisonstart) – EmptyState + Legende korrekt; Filter ggf. lockern (Boss).
- Tests (docs/tests): rt26–rt31. Ergebnis rt28/rt31 (Marker zy): Popover sichtbar bei Hover-Karte (1292–1592 px), am unteren Rand (Flip),
  auf 390 px (82–382 px), im Spieler-Detail-Overlay; Klick daneben/Esc schließen; EN (rt27): "scale 0–100" + englischer Text; 0 Fehler.
- OFFEN: 1.6 Statussystem, 1.4 Filterleiste (nach Launch), Vereinslogos-Sync, Match-/Opportunity-Score-Berechnung (Freigabe), Boss-To-dos
  (PAT rotieren! OpenAI-Limit, n8n-2FA, SSH-Key, Repo privat).

## 25.08. 01:40–01:58 – DESIGN-SYSTEM 1.6 STATUSSYSTEM, Commit c607931 / Marker zz
- Meldungsarten (TYPE) bereinigt: je Art genau eine Definition (vorher leihe/vertrag doppelt, spätere Definition gewann). Farbcode eindeutig:
  Fixer Deal grün #0d8a4f · Gerücht amber #b07a05 · Verein sucht violett #6d4bc7 · Leihe blau #1a6dc0 · Verlängert/Vertrag türkis #0f8e8e (vorher
  gleiches Grün wie Fixer Deal) · Vertragslos grau #6b7280 · Trade #6b4fd8. Linke Kartenkante + Badge nutzen type.color.
- Belastbarkeitsstufen (RELIABILITY 1–5) neu benannt, damit sie nicht mit der Meldungsart kollidieren: Spekulation · Unbestätigt (vorher "Gerücht")
  · Belastbar (vorher "Konkret") · Sehr wahrscheinlich · Bestätigt; RELIABILITY_EN: Speculation · Unconfirmed · Solid · Very likely · Confirmed.
- Neuer Baustein Reliability({value,size}) = Signal-Balken + Wort in relColor + Tooltip "Belastbarkeit N von 5 — Skala: …" (className tw-rel).
  Eingesetzt in NewsCard-Fuß, NeedCard, Meldungspanel-Kopf. Signal aria-label "Belastbarkeit". Keine direkte Signal-Verwendung mehr außerhalb.
- Meldungspanel: eigene Uppercase-Pille → Badge (wie Karten), daneben Reliability; "⚠ Unbestätigt"-Chip entfernt (war redundant); Feld
  "Verlässlichkeit" → "Belastbarkeit" (DE/EN). GerVue-Kompaktliste zeigt weiter Punkt+Art (Farbcode), keine Belastbarkeit (bewusst kompakt).
- EN_MAP: Unbestätigt→Unconfirmed, Belastbar→Solid, Belastbarkeit→Reliability. Daten/Werte unverändert (nur Wörter/Darstellung).
- Tests rt32–rt36: Feed 60 Karten / 60 Reliability (Belastbar 25, Sehr wahrscheinlich 14, Unbestätigt 13, Bestätigt 8), Badges nur Meldungsarten,
  kein ⚠; EN Solid/Very likely/Unconfirmed/Confirmed; Transfers 120/120; Vereinsbedarf 46 NeedCards/46; Panel: Badge "Gerücht" + "Belastbar"
  + Liga, tw-rel 1, kein ⚠. 0 Fehler. Lektion Test: innerText liefert text-transform (BELASTBARKEIT) → Prüfungen case-insensitiv schreiben.
- OFFEN: 1.4 Filterleiste (nach Launch), Vereinslogos-Sync, Match-/Opportunity-Score (Freigabe), Listen-Preset U23-Abwehr 0 Treffer, Boss-To-dos.

## 25.08. 02:31–03:05 – TRANSFERS & GERÜCHTE: Feinbrief des Bosses (Commits c2e4217, 31270b3, 2e4c967, Marker ae/af/ag)
ACHTUNG VORGESCHICHTE: Eine Parallel-Session hatte 02:17–02:29 (a511f3b, 2f48ce8, 3b466f2, Marker ab–ad) Abschnitt 2 des Boss-Dokuments bereits
weitgehend gebaut (Beschreibung+Datenstand, Scout-Block, zweizeilige Filter mit Zählern, Weitere Filter, Sortierung, Karten/Kompakt-Tabelle,
Signalstärke/SignalLine, gespeicherte Suchen, GerAside mit Marktüberblick). Boss hat danach entschieden: diese Session übernimmt. Vor jedem Push git pull!
### Ergänzt (ae)
- Texte: Beschreibung „…Bedarfssignale – laufend aktualisiert und mit dem TW Scout durchsuchbar.“; Scout-Kopf „TW SCOUT · TRANSFERRECHERCHE“
  (uppercase, 11 px); Platzhalter „Frage z. B.: …“; Vorschläge jetzt Neue Bundesliga-Deals / Vertragslose U23-Spieler / Vereine mit aktuellem Stürmerbedarf.
- Filter: Verein-Feld „Verein oder Spieler suchen ...“ (220 px), Position → „Alle Positionen“, Zeitraum-Platzhalter „Alle Zeiträume“,
  GER_LEER.zeit = "7d" (Standard Letzte 7 Tage; zählt nicht als aktiver Filter). Sortierung „Neueste zuerst“.
- Zeile unter den Filtern: links „N Meldungen · aktualisiert vor X“ (twRelTime auf updatedAt/neueste Meldung), rechts Sortierung + Karten/Kompakt;
  alte separate Zählzeile entfernt. Aktiver Chip „Alle“ = #0f1520 (dunkel, kein Orange) – war schon so.
- Kartenraster: .tw-glist zwei Spalten, ab 860 px eine. RouteLine-Komponente in NewsCard: Pfeil NUR wenn Von- UND Zielverein bekannt; sonst
  „ZIELVEREIN [Verein]“ bzw. „AKTUELLER VEREIN [Verein]“ / „VERTRAGSLOS · ZULETZT“; Kasten entfällt ganz, wenn weder Spieler noch Verein noch Ablöse.
- Mobil (≤700 px): Filterzeile ausgeblendet, stattdessen Button „Filter (N)“ → Bottom Sheet (fixed unten, 86vh, Land/Liga/Suche/Position/Zeitraum +
  kompletter „Weitere Filter“-Block + Zurücksetzen/„N Meldungen anzeigen“); Typ-Chips horizontal scrollbar (nowrap, Scrollbar versteckt).
### Fehler gefunden und behoben (af) – WICHTIG
- Die API /api/transfernews liefert KEIN published (ISO), nur publishedAt als relativen Text („vor 2 Std“). zeitVon() gab damit 0 zurück →
  mit dem neuen Standard „Letzte 7 Tage“ filterte die Seite ALLES weg (rt37: 0 Meldungen). Fix: relToTime() parst „vor N Min/Std/Tg“ und
  „N min/h/d ago“; zeitVon(), neuesteZeit und der Heute-Zähler der Seitenleiste nutzen es. Danach 383 Meldungen (64 fix / 118 Gerüchte / 166 Bedarf).
- (ag) .tw-feedlist-Regel für ≥1280 px auf minmax(0,1fr) umgestellt – vorher konnten lange Inhalte eine Spalte breiter ziehen.
### Abnahme rt37 (Marker af/ag)
Desktop: Beschreibung/Scout-Kopf/Platzhalter/Vorschläge korrekt, Scout-Block 102 px hoch (Vorgabe ≤104), Filter wie oben, Chips „Alle 383 …“,
aktiv dunkel rgb(15,21,32), Zeile „383 Meldungen · aktualisiert gerade eben“, Sortierung „Neueste zuerst“, Karten je Reihe 2 (522/484 px, gleiche Höhe
307/307, 275/275), kein Pfeil ohne Ziel, 13× „ZIELVEREIN“-Zeile. Mobil 390 px: Filterzeile aus, Filter-Button an, Chips scrollbar, Karten 366 px einspaltig,
Sheet bündig unten (7 Auswahlfelder, 4 Haken, „383 Meldungen anzeigen“), schließt korrekt. EN: club-need signals, TW SCOUT · TRANSFER RESEARCH,
„383 reports · updated just now“, kein deutscher Rest. 0 Fehler.
### KI-Sprachregel (n8n, nicht Website)
- Analyst ifOFnqTVjThmiFEJ, System-Prompt Punkt 7 NEU: Formulierung muss zum type passen – nur type=fix darf vollendet formulieren (wechselt zu,
  verpflichtet, offiziell); geruecht IMMER vorbehaltlich (steht vor einem Wechsel zu, Gespräche mit, Interesse an); verein_sucht nie als Bewegung.
  Version 00a11cf0 publiziert (03:0x). Wirkt erst auf NEUE Meldungen ab dem nächsten Lauf (:20), Altbestand bleibt wie er ist.
### OFFEN
- Kompaktansicht-Spalten stehen (Zeit/Typ/Verein-Spieler/Bewegung/Liga/Status/Quelle) – noch nicht live gegengeprüft.
- 1.4 einheitliche Filterleiste für die ÜBRIGEN Seiten (nach Launch), Vereinslogos-Sync, Match-/Opportunity-Score (Freigabe), Boss-To-dos (PAT!).

## 25.08. 23:42–23:52 – NEWSFEED: Seitenleisten-Kasten weg, normale Filterzeile (Commit 7d6e203, Marker ah)
- Boss-Screenshot (1845 px breit): der weiße Kasten „Meistdiskutierte Vereine / Gespeicherte Filter“ lag ÜBER den Feed-Karten (Karten 617 px breit,
  Kasten 1232–1570). Headless (rt38) war das Layout korrekt (1020/340) – Ursache beim Boss nicht reproduzierbar (Tab war seit ~22 Std offen, „aktualisiert vor 22 Std“).
- Entscheidung: Feed hat KEINE Seitenleiste mehr (aside leer → :has-Regel → volle Breite 1384 px, zwei Karten à 686 px). FeedSuche bekommt
  Prop inline: Filterzeile (.tw-feedfilter) direkt unter den Typ-Chips: Label „Meistdiskutierte Vereine“, 5 Vereins-Chips (Logo, Name, Zähler),
  aktiver Chip dunkel #0f1520, „✕ Zurücksetzen“, rechts gespeicherte Filter als Chips (◎ Name, ✕ löschen) + „+ Aktuellen Filter speichern“.
  Andere Seiten behalten den Seitenleisten-Kasten (Bedingung view !== "feed").
- Abnahme rt39 (1845 px): keine Überlappung, Filterzeile 49 px, Chip-Klick → 35 Karten (Manchester United), Zurücksetzen → 60; mobil 366 px passt. 0 Fehler.
- OFFEN: Boss-Brief „Vereinsbedarf & Spieler-Matching“ (Datenlage geprüft: 584 Bedarfe, 383 mit seekStrengths, KEIN Alter; siehe Analyse im Chat) – noch nicht gebaut.

## 26.08. 00:50–01:00 – TRANSFERS: Boss-Brief erneut (Filterbereich jetzt EINGEFROREN), Commits fd6b7b9 / 6c8d02d, Marker ai/aj
- Boss-Vorgabe neu: Filterbereich (Zeile 1, Typ-Chips, Weitere Filter, mobiles Sheet) bleibt vollständig unverändert – Beschriftungen, Reihenfolge,
  Optionen, Verhalten, aktive Zustände, Abstände, mobil. NICHT MEHR ANFASSEN.
- (ai) Karten-Signalzeile exakt im Boss-Wortlaut: „Signalstärke NN/100 · Quellenvertrauen: hoch/mittel/gering“ (EN „Signal strength … · source trust: …“).
  Kompaktliste: Bewegung nur bei Von+Ziel („A → B“), sonst „Vertragslos → B“ (nur type vertragslos), „Ziel: B“ oder „von A“; keine „—“/„?“-Platzhalter
  mehr (Verein/Liga leer statt Strich); Status „Signalstärke NN/100“ bzw. „✓ Bestätigt“.
- (aj) FUND: publishedAt der API ist nur für <24 h relativ („vor 3 Std“), älter kommt als Datum „25.08.“ / „04.08.“. relToTime parst jetzt DD.MM.
  und DD.MM.JJJJ (Mittag; Zukunft → Vorjahr). Vorher zeigte der 7-Tage-Standard nur 30 Meldungen, jetzt 1015 (219 fix / 271 Gerüchte / 411 Bedarf).
- Abnahme rt40/rt41: Titel/Beschreibung/Scout-Kopf/Vorschläge ok; Zeile „N Meldungen · aktualisiert …“, „Neueste zuerst“, Karten/Kompakt; Kicker uppercase,
  Beobachten + Zeit rechts, Beschreibung 3-Zeilen-Clamp, 30/30 „Details →“, keine Pfeile ohne Ziel, keine Platzhalter, zwei gleich breite Spalten;
  Kompakt: 7 Spalten, Zeilenhöhe 31 px, keine Platzhalter; mobil: Kompakt-Button sichtbar, Tabelle horizontal scrollbar (366 px), Karten einspaltig,
  Filterbereich unverändert (Filter-Button „flex“). 0 Fehler.
- OFFEN: Altbestand der Gerüchte-Überschriften (Sprachregel greift nur für neue Meldungen) – einmalige Nachformulierung nur mit Boss-OK.

## 26.08. 01:05–01:45 – VEREINSBEDARF & SPIELER-MATCHING (Boss-Brief), Commits 5323ce5 / d696ec5 / +am, Marker ak/al/am
- Boss-Vorgabe: Kriterien- und Filterelemente (Profil-Sheet: Spielername, Position, Alter von/bis, Stärken; Beschriftung/Reihenfolge/Optionen/
  Verhalten) bleiben unverändert – NICHT ANFASSEN. Header/Navigation unverändert.
- Neue Komponente BedarfVue (vor NeedCard) ersetzt die beiden gesucht-Blöcke im TransferApp (Props: needs=needsBySport, profiles, matchProfil,
  setMatchProfil, posSet, activePos, setPosFilter, onNewProfile, onEditProfile, removeProfil, openContacts, onOpen=setMSel, onWatchClub=addWatch("verein"),
  watch=watch.items). Aufbau: Kopf (h2 + Beschreibung + grüner „+ Neues Spielerprofil“ rechts) → Intro (3 verbundene Schritte + Alert-Satz, 114 px)
  ODER „Meine Spielerprofile“ (Karten: Name, Positionslabel · Alter · Stärken, „N neue Vereinsmatches · M gesamt“, Matches ansehen / Profil bearbeiten / ×)
  → Positionsraster (.tw-pos-grid 5 je Reihe, ≤1000 px 3, ≤700 px 2; Kachel = PitchIcon (Mini-Spielfeld mit Punkt je Position) + Name + „N passende
  Vereine“ + „+M neue Treffer“ (7 Tage)) ODER Ergebnis („N Vereine mit aktuellem Xbedarf“ / „N Vereine passen zu Name“, Zurück-Button, „+N neu“).
- NeedCard erweitert (Props match{score, gruende}, onOpen, onWatchClub, watched): Block „TW Match Score ⓘ … NN/100“ (scoreColor), „Warum dieses
  Match?“ mit ✓/○-Gründen, Buttons „Match analysieren“ (→ MeldungsPanel) und „Verein beobachten“ (→ Merkliste Typ verein, Zustand „✓ Verein beobachtet“).
- matchScore(need, profil): 40 Position + rel×6 + 10 Kaderplatz-Signal (Regex Abgang/Verletzung/Ersatz…) + Aktualität (≤3 Tg 6, ≤7 Tg 3) + ≥2 Quellen 4;
  mit Profil: Stärken-Treffer ×4 (max 12), Alter passt (jung/erfahren im Text) +6; Deckel 99. matchGruende(): öffentlicher Bedarf · Quelle · Belastbarkeit,
  Position explizit gesucht / passt, Kaderplatz frei · Snippet, Markt Land · Liga (Stufe aus LAND_LIGEN), Stärken passen / gesuchtes Profil (○), Alter passt,
  gemeldet <Zeit>. Immer ≥3 Gründe. SCORES.match-Erklärung entsprechend aktualisiert.
- Profil bearbeiten: pfEdit-State; onEditProfile befüllt pfName/pfPos/pfA1/pfA2/pfSt und öffnet den unveränderten Sheet; addProfil ersetzt bei pfEdit
  das alte Profil in einem updateWatch (kein Duplikat). „+ Neues Spielerprofil“ setzt pfEdit zurück.
- (al) Feinschliff: Leerzeichen „46 passende Vereine“, „24 Jahre“ bei gleichem Von/Bis, Button dauerhaft „Matches ansehen“, „Meine Spielerprofile“ 16 px.
  (am) Satz-Stärken aus dem Bedarfs-Radar als „gesuchtes Profil: …“ (Original, 72 Zeichen) statt kleingeschriebener Liste.
- Abnahme rt45 (Marker al): Kopf/Button/Intro 114 px/Schritte/Alert ok; 10 Kacheln 5+5 mit SVG; „46 Vereine mit aktuellem Torwartbedarf“, 46 Karten,
  Score 74/100, 5 Gründe, alle Karten ≥3; Analyse-Panel öffnet; Beobachten setzt Merkliste; Sheet-Labels unverändert (3 Inputs, 1 Select); Profil
  „Sang-Yoon Kang · Achter · 24 Jahre · 22 neue · 35 gesamt“; „35 Vereine passen zu Sang-Yoon Kang“ mit Profil-Gründen; Bearbeiten vorbefüllt, nach
  Speichern weiter 1 Profil; mobil 2 Kacheln/Reihe (177 px), Matches einspaltig (366 px). 0 Fehler.
- OFFEN: „Vertrag bis“ auf der Profilkarte braucht ein Sheet-Feld (Boss-Freigabe); Gehaltsrahmen/Marktwert ohne Vereinsdaten nicht als Grund darstellbar.

## 26.08. 01:40–02:20 – SPIELER-PERFORMANCE (Boss-Brief), Commits fbac6ed / c7f24a5 / 1617ccc, Marker an/ao/ap
- Boss-Vorgabe: Such- und Filterleiste (1 Suchfeld, 4 Selects: Alle Ligen / Alle Positionen / Stärke filtern / Schwäche filtern) unverändert – NICHT ANFASSEN.
  Offene Punkte pausiert (Boss 26.08.), nur bei echter Dringlichkeit ansprechen.
- Datenlage /api/tw-performance: Zeilen der letzten 5 Tage, Top 250 nach tw_score; Felder pid, name, team, league, pos (Torwart/Abwehr/Mittelfeld/Sturm),
  date, gegner, min, sub, score, api, st/sw (Texte), stt/swt (Tags), dev, stats (JSON-String: t,a,s,st,p,pq,kp,zk "5/11",tk,ic,dr,f,g,r,sv,gc). KEIN Foto,
  KEIN Alter, KEIN Vorspieltag. pq = angekommene Pässe (Zahl) – alte Anzeige „(15%)“ war falsch; jetzt Passquote = pq/p (68 %). Analyst läuft 2:30.
- Neue Komponenten (vor NeedCard): perfStats/perfPassquote/perfPosCode/perfKeyValues/perfKurz/perfDatenstand/perfElf, PitchLines (SVG quer 150×100 bzw.
  hochkant 100×150: Außenlinien, Mittellinie, Mittelkreis, Straf-/Torräume, Elfmeterpunkte, Bögen, Eckbögen), PerfMarker (44 px Kreis mit Score, Name,
  Kürzel TW/AW/MF/ST, Hover-Karte .tw-pm-tip mit Verein/Tore/Assists bzw. Paraden/Gegentore/Minuten/Score; Klick → openPlayer), PerfPitch (Team der Woche
  als Formation über die Fläche, Joker-Zeile), SpieltagKarte (Monogramm, Name, Verein+Logo, Position·Liga, TW PERFORMANCE SCORE groß, Delta zum letzten
  Spiel per SPIELER_URL?pid (form), Matchwerte-Chips, „Analyse öffnen“, „Beobachten“), PerfTabelle (Spalten # / Spieler / Spiel / Position / Min. /
  Schlüsselwerte / Trend / TW Score ⓘ; Zeile klappt Stärken/Schwächen/Entwicklung + Analyse auf; mobil kompakte Karten), PerfVue (Layout .tw-perf-main
  3fr/1fr, ≤900 px einspaltig, Spielfeld hochkant ≤700 px; „Wie wird der Score berechnet? ⓘ“ = ScoreInfo mit label; Mindestspielzeit 30 Min – Suche hebt
  sie auf). Alter TotW-/Panel-/Listen-Block im TransferApp ersetzt; Kopf: rank_sub neu (DE/EN) + Datenstand-Zeile.
- Trend-Spalte zeigt „–“ (Tooltip): pro Zeile gibt es keinen Vorspieltag in der API. Würde eine API-Erweiterung brauchen (Vorwert je pid).
- (ao) „Wie wird der Score berechnet?“ als Label IN der ScoreInfo-Schaltfläche (Prop label). (ap) ScoreInfo: Scroll-Schonfrist 600 ms nach dem Öffnen –
  Playwright-/Trackpad-Nachlaufscrollen schloss das Popover sofort (Ursache des „KEIN POPOVER“ in rt46–48).
- Abnahme rt46/rt48/rt50: Kopf/Beschreibung/Datenstand ok; Filterleiste identisch (auch mobil); Spalten 74/25; Spielfeld 3:2 mit 5 Rechtecken, 4 Kreisen,
  3 Bögen, 1 Linie; 11 Marker (44 px), Hover-Karte sichtbar; Karte mit Titel, Monogramm, Werten „3 Tore · 1 Assist · 83 Minuten · 68 % Passquote ·
  5/11 Zweikämpfe“, Delta „▲ +20 zum letzten Spiel (77)“, Buttons; Tabelle 8 Spalten, 244 Zeilen, Details + „Analyse öffnen“ (Formkurve lädt);
  mobil Spielfeld hochkant (2:3) über Karte, Liste als Karten; EN vollständig; Erklärung öffnet per echtem Klick, Scrollen schließt. 0 Fehler.
