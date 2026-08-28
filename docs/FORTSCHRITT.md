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

## 26.08. 02:25–03:05 – SPIELER-DATENBANK (Boss-Brief) + DATENFEHLER Transfermarkt-Spalten, Commits 3867ecc / df0a391, Marker aq/ar
- Boss-Vorgabe: Such- und Filterleiste (Suchfeld + Alle Länder / Alle Ligen / Erst Liga wählen / Alle Positionen) unverändert – NICHT ANFASSEN.
- Datenlage /db/players (PostgREST, max 200 Zeilen je Antwort, KEINE Aggregate): 15.315 Spieler; Spalten u. a. age, apps, minutes, rating, goals,
  assists, pass_acc, duels_pct, contract_until, contract_note, fitness_note, photo, tm_id, tm_value_eur, tm_value_text, tm_contract_until,
  tm_updated_at, imported_at. Zähler per GET + Header „Prefer: count=exact“ + „Range: 0-0“ (content-range „0-0/N“).
  /api/tw-listen?sort=score&limit=200&min_minutes=270 liefert pid/name/team/league/pos/age/photo/score/src(tw|api)/sp/goals/assists/min.
- Neue Komponenten (vor NeedCard): DB_COLS, dbFmtZahl/dbDatum/dbMwEur/dbBald/dbNormDb/dbRelevanz, DbFoto (Foto oder Monogramm), DbSpark (Formkurve),
  SpielerQuick (Kurzansicht rechts als Portal: Name, Alter·Position·Nation, Verein+Logo, TW PERFORMANCE SCORE + Quelle, Marktwert, Vertragsende,
  Minuten, Fitness, Formkurve aus SPIELER_URL?pid (form), Stärken aus f.st der letzten Spiele, „Volles Profil öffnen“, „Beobachten“; Esc schließt),
  DbVue (Kennzahlen Spieler/Ligen/Verträge 12 Monate; „Empfohlene Spieler“ = tw-listen Top 200 + Anreicherung aus /db/players per player_id=in.(…);
  Relevanz = Score + 10 bei TW-Analyse + Minuten/90 (max 10) + 4 Marktwert + 2 Vertrag + 1 Foto; Toolbar Ergebnisse/Sortierung-Select/Spalten anpassen
  (localStorage tw_dbcols)/Suche speichern (tw_dbsearches, Chips)/Exportieren (CSV, Semikolon, BOM)/Scouting-Liste (tw_scoutlist, Filter);
  Tabelle .tw-dbtable maxHeight 72vh, sticky th, sortierbare Spalten, Vergleichs-Häkchen (plVergleich, max 3), Hover-Aktionen .tw-dbact
  (öffnen/beobachten/vergleichen/Scouting-Liste); Suchmodus nutzt dieselbe Tabelle (Score = rating×10 „API“, TW-Score wenn in Empfehlungen);
  Form-Spalte = letzter Spieltag aus PERF_URL vs. Score (▲/▼/▶), sonst „–“; mobil ≤760 px Karten). Kopf-Beschreibung dynamisch aus dbStats
  (TransferApp: gesamt, v12, stand=imported_at, ligen=dbLigenZahl() – Alias-Namen Jupiler Pro League/Premiership/Superligaen zählen nicht → 20).
- Abnahme rt51: Kopf „15.315 Spieler aus 20 Ligen · … · aktualisiert heute um 02:30 Uhr“, Filterleiste identisch, Kennzahlen, Marketingblock weg,
  „Empfohlene Spieler“ + Unterzeile, „15.315 Ergebnisse“, Toolbar, 9 Spalten, sticky, 60 Zeilen, Sortierung Alter ok, Hover-Aktionen sichtbar,
  Vergleich markiert, Scouting-Liste 1, Kurzansicht 420 px mit allen Feldern, Spalten abwählbar, Export „transferwire-spieler.csv“, Suche „Palmer“
  → 5 Ergebnisse, mobil Karten (60), Filter unverändert. 0 Fehler.
### DATENFEHLER (behoben, Boss informiert)
- Der „TW DB: Spieler-Spiegel (täglich 4:30)“ (/opt/transferwire/tw_players_sync.sql, per SSH-Workflow 4IpxlFUalqigwT64) macht TRUNCATE players +
  INSERT aus der n8n-Datentabelle – OHNE die Transfermarkt-Spalten. Folge: Marktwerte/TM-Verträge des 2:40-Imports wurden täglich um 4:30 gelöscht
  (26.08. 02:29 UTC: 94 Verträge; 02:43 UTC: 0). FIX: Skript sichert vor dem TRUNCATE die tm_*-Spalten in TEMP tm_keep und spielt sie nach dem
  INSERT per UPDATE zurück (Backup: tw_players_sync.sql.bak-2026-08-26). Test: Spiegel-Lauf mit 376 Marktwerten vorher/nachher identisch.
- Transfermarkt-Import manuell nachgeholt (Rotation tm_state.liga_index gesetzt): LaLiga 379, Bundesliga 408, Premier League 469, Serie A, Ligue 1.
  Rotation läuft ab jetzt nächtlich weiter (eine Liga pro Nacht, 20 Ligen). Hinweis: Das SQL-Skript enthält das DB-Passwort im Klartext (dblink).

## 26.08. 03:05–03:20 – VERTRAGSRADAR „Auslaufende Verträge & verfügbare Spieler“ (Boss-Brief), Commit 09573cf, Marker as
- Boss-Vorgabe: vorhandene Filter/Kategorien/Sortierungen unverändert – die Seite hat drei Kategorien (Auslaufende Verträge binnen 12 Monaten /
  Vertragslos gemeldet / Klubs unter Verkaufsdruck), keine Filter- oder Sortier-Elemente. Kategorien und ihre Inhalte für frei/druck unverändert.
- Datenlage /api/tw-markt (dauert ~10 s!): auslaufend (33: pid,name,team,league,pos,age,bis „YYYY-MM-DD“ oder „vertragslos“, note mit Datum,
  minutes,rating – KEIN Marktwert), frei (18 News: headline,summary,player,league,datum), druck (0). Marktwert/Vertrag aus /db/players (tm_*).
- Neue Komponenten (vor NeedCard): vtDatum (YYYY-MM-DD, YYYY-MM, YYYY, DD.MM.YYYY), vtFmt, vtTage, vtStatus (frei → „Vertragslos seit DD.MM.YYYY“ +
  Badge „Sofort verfügbar“ orange; <30 Tage → „Endet in N Tagen“ orange; sonst „Vertrag bis DD.MM.YYYY“ neutral; nie „Vertrag bis vertragslos“),
  vtScore (Opportunity 0–99: Verfügbarkeit 40/32/24/14, Alter 15/9, Minuten 15/9/4, Rating 15/10/5, Marktwert 8/4, Quelle 7/3), vtRadarZeile,
  VertragKpis (sofort = Radar-Vertragslose; Verträge 6 Monate + Marktwert>1 Mio innerhalb 12 Monaten per PostgREST-Count; neu = frei-Meldungen der
  letzten 7 Tage + Radar-Vertragslose mit Datum der letzten 7 Tage), VertragTabelle (Radar + DB-Verträge 12 Monate, Dedupe per pid, Reihenfolge
  vertragslos → früheste Enddaten → Score; Spalten Spieler/Alter/Position/Verein-Liga/Status/Vertragsende/Marktwert/Quelle/TW Opportunity Score ⓘ;
  sticky Kopf, Zeile → openPlayer; mobil ≤760 px Vertragskarten). SCORES.opportunity-Text nennt jetzt die Faktoren mit Punkten.
- Abnahme rt53: Titel/Beschreibung; Kennzahlen „3 sofort verfügbar · 29 Verträge enden in 6 Monaten · 285 Spieler mit Marktwert über 1 Mio. € ·
  12 neue Einträge diese Woche“; Tabelle 9 Spalten, 232 Zeilen, sticky; Status-Varianten korrekt (Vertragslos seit + Badge, Vertragslos + Badge,
  Vertrag bis), kein „Vertrag bis vertragslos“, kein Orange bei normalen Enden, 195 Marktwerte, Quellen Markt-Scout/Transfermarkt, Scores 83/72/66,
  Erklärung öffnet mit Faktoren, Zeile öffnet Profil, mobil 232 Karten + 4 Kennzahlen. 0 Fehler.

## 26.08. 03:20–03:35 – MERKLISTE & ALERTS (Boss-Brief), Commits c7b37d4 / 41e75db / +av, Marker at/au/av
- Boss-Vorgabe: vorhandene Filter unverändert – auf der Merkliste sind das die Meldungs-Chips (Alle Meldungen / Leihe / Vertragslos) des gemeinsamen
  Feed-Bausteins; unangetastet. Die Meldungsliste (watchList) läuft weiter unter dem neuen Cockpit.
- Neue Komponenten (vor NeedCard): mkLese/mkSchreib, mkMerkeZuletzt (openPlayer schreibt tw_recent, max 8), mkGespeicherteSuchen (tw_savedfilters /
  tw_gsearches / tw_dbsearches), MerkSpielerZeile (Datenbank-Lookup über search_name: normalisiert → Vor-+Nachname → Name; Kurzansicht-Daten
  Verein·Position, TW Performance Score + Veränderung aus SPIELER_URL-Form (sonst Rating×10 „API“), neue Meldungen (7 Tage) aus watchList,
  Vertragsende, letzte Aktualisierung; Aktionen Profil öffnen / Notiz (tw_notes) / Alert ein-aus (item.alert=false = stumm, per updateWatch) /
  Scouting-Liste / Vergleichen / Entfernen; mobil Karte), MerkVue (Titel, Beschreibung, Tabs Spieler/Vereine/Meldungen/Spielerprofile/Gespeicherte
  Suchen mit Zählern; Leerzustand kompakt mit „Spieler entdecken“ → players, „Suchprofil erstellen“ → gesucht + Profil-Sheet; „Empfohlen für dich“
  3 Karten → ranking/chancen/gesucht; Vereins-Tab mit Meldungszähler; Profil-Tab „Matches ansehen“; Suchen-Tab „Anwenden“ (feed: Filter setzen,
  transfers: setGerApply, db: setPl*)), MerkAside (ersetzt FeedSuche auf der Merkliste: „Deine Alerts“ mit Status aktiv/keine, Text, Button →
  setWatchDlg; „Zuletzt angesehen“ aus tw_recent).
- Abnahme rt54/rt55: leer: Titel, Beschreibung, 5 Tabs mit 0, Leerzustand-Texte, beide Buttons, drei Empfehlungen, Aside „Deine Alerts“ / „Keine
  aktiven Alerts“ / Text / „Alert erstellen“ (öffnet E-Mail-Dialog) / „Zuletzt angesehen“, kein „Meistdiskutierte“; Chips unverändert. Befüllt:
  Tabs „Spieler 2 · Vereine 1 · Meldungen 40“, Zeile Cole Palmer „Chelsea · Sturm | 89 API | keine | 30.06.2033 | heute“ mit allen sechs Aktionen,
  Notiz + Alert aus + Entfernen funktionieren; Vereinszeile „Manchester United | 13 neue Meldungen | heute“; mobil Tabs scrollbar, Aside unter dem
  Inhalt, Empfehlungen einspaltig. 0 Fehler. (av: Namensvariante „Luís Asué“ ↔ DB „Luís Nlavo Asué“ wird jetzt über Vor-/Nachname gefunden.)

## 26.08. 03:30–03:45 – TALENT-RANKINGS (Boss-Brief), Commits d307282 / +ax, Marker aw/ax
- Boss-Vorgabe: Kategorien (🏆 Top 50 Europa / 💎 Unentdeckt / ⚽ Torjäger / 🎯 Vorlagen), Länder-Chips (Alle/DE/EN/FR/ES/INT), ScoutSub-Tabs
  unverändert – Chips, Reihenfolge, Abfragen (URLs) und Lade-/Leer-Texte 1:1 übernommen.
- Datenlage /db/talent_profiles: talent_key („name-slug|2007“ oder „name-slug|a18“ – beide Formate für denselben Spieler möglich → Dedupe über den
  Slug vor „|“), scout_score 0–10 grob (9, 8.5, 8, 7.6 …), strengths (Kommaliste), minutes, rating, mentions_7d, goals, assists, begruendung,
  updated_at; KEIN player_id/Foto/Vertrag/Vorwoche. Anreicherung per Name aus players_youth (player_id, photo, minutes, rating) und players
  (Vertrag, Foto). Torjäger/Vorlagen aus players_youth (order=goals.desc liefert NULL zuerst → Anzeige sortiert clientseitig).
- Transparenter TW Talent Score (talFaktoren, eine Nachkommastelle): Potenzial (scout_score×10, 30 %), Leistung (Rating 6→40 … 8→95, sonst
  Potenzial, 25 %), Entwicklung (45 + Torbeteiligung/90 bis 30 + Medienmomentum bis 25, 15 %), Einsatzzeit (Minuten 0→20, 450→55, 900→75,
  1500→90, 15 %), Altersfaktor (16→95 … 21→58, 10 %), Gegnerstärke (Top-5 90 / Erstligen 75 / Zweitligen 62 / Jugend-Reserve 45 / sonst 55, 5 %).
  SCORES.talent-Text nennt die Formel. Vorwochen-Delta: Client-Snapshot tw_talent_snap (wöchentlich rollend; bis dahin „erste Bewertung in
  diesem Ranking“) – ein serverseitiger Wochen-Snapshot wäre der saubere Ausbau.
- UI: Kopf (h2 „Talent-Rankings“, Beschreibung, „Aktualisiert … um … Uhr“ aus max(updated_at)), Hinweisbalken kurz + ScoreInfo-Label „Methodik
  ansehen“ (öffnet Talent-Score-Erklärung); Top-3-Karten (Rang, Foto/Monogramm, Name, Alter · Position, Verein · Liga, Score-Pill klickbar,
  Vorwochen-Text, stärkste Eigenschaft = erste Stärke, „Analyse öffnen“ → openPlayer bei pid, sonst Panel; #1 mit Outline/Schatten/Verlauf);
  Tabelle (Rang/Spieler/Alter/Position/Verein-Liga/Minuten/Vertrag/Trend/TW Talent Score, sticky Kopf, Zeile → Profil/Panel); Panel (Portal
  rechts): sechs Faktoren mit Balken/Wert/Gewicht, Stärken, Begründung, Aktionen Beobachten/Analyse öffnen/Vergleichen/Scouting-Liste/Exportieren
  (CSV je Spieler); Vergleich/Analyse nur mit pid (Hinweis). Mobil: Top-3 untereinander, Liste als Karten.
- Abnahme rt56: Titel/Beschreibung/„Aktualisiert am 24.08. um 19:42 Uhr“, Banner kurz + Methodik-Link (öffnet Popover), Chips 4 + 6 unverändert,
  Top-3 mit allen Elementen („81,1“, „erste Bewertung …“, „Stärkste Eigenschaft: Konstanz“), Tabelle 9 Spalten, 44 Zeilen, alle Scores mit
  Nachkommastelle, 35 verschiedene Werte, 0 doppelte Namen, Panel mit 6 Faktoren/Gewichten und 5 Aktionen, Export „talent-florian-hellstern.csv“,
  Torjäger-Ansicht mit Spalte „Tore“, mobil einspaltig/Karten. 0 Fehler.

## 26.08. 03:45–03:57 – SCOUTING-LISTEN (Boss-Brief), Commit cd232fa, Marker ay
- Boss-Vorgabe: Filter-/Sortierfunktionen unverändert – das Listenformular (Name, Max. Alter, Region, Liga, Position, Min. Performance Score,
  Max. Minuten, Sortierung, Speichern/Abbrechen) und die geöffnete Listenansicht (← Alle Listen, Titel, ScoreLegend, Einträge) sind 1:1 geblieben.
  Nur die Übersicht wurde ersetzt.
- Neue Komponente ListenVue (vor NeedCard) + liFilterChips/liExportCsv: Kopf (h2, Beschreibung, grüner Hauptbutton „+ Neue Scouting-Liste“ →
  setListFormOpen), Tabs Empfohlen (LIST_PRESETS) / Meine Listen (myLists) / Geteilte Listen (shared-Flag bzw. tw_listmeta), Kartenraster 3
  Spalten (mobil 1): Titel, Beschreibung, drei Spielerbilder (aus den Listentreffern, DbFoto), „N Spieler · automatisch aktualisiert“ (N = Treffer
  der Liste per LISTEN_URL, gecacht), „Zuletzt aktualisiert: heute, HH:MM Uhr“ (imported_at der Spielertabelle), Filter-Chips aus den Parametern,
  Status Kuratiert/Privat/Geteilt, Alert aktiv/inaktiv (tw_listmeta), „Liste öffnen →“ (ladeListe). Drei-Punkte-Menü: Öffnen, Duplizieren (Kopie in
  Meine Listen), Teilen (Link #liste=<base64 JSON> in die Zwischenablage, Liste als geteilt markiert; Import beim Laden per Hash → Meine Listen mit
  shared=true, von=„Link“), Exportieren (CSV der Treffer), Alert aktivieren/deaktivieren, Löschen (nur eigene, rot, mit Rückfrage).
  Leerzustände: „Noch keine eigenen Scouting-Listen“ + Text + „Neue Liste erstellen“; analog für Geteilte. Keine roten Linien/Buttons mehr
  (Türkis #0e7490 / Grün #149a59 / Grau).
- Abnahme rt57/rt58: Kopf/Beschreibung, grüner Button rechts, Tabs „Empfohlen 10 · Meine Listen 0 · Geteilte Listen 0“, 0 rote Elemente, 10 Karten
  in 3 Spalten mit allen Elementen, Menü (5 Punkte bei kuratierten), Duplizieren → „Meine Listen 1“, Alert + Teilen → „Geteilte Listen 1“,
  Export „scouting-top-50-u21-talente-europa-kopie.csv“, Löschen → Leerzustand mit allen Texten, Formular unverändert (Labels/Optionen), Liste öffnen
  → Listenansicht mit 50 Einträgen, mobil einspaltig (366 px) mit scrollbaren Tabs. 0 Fehler.

## 26.08. 03:58–04:10 – COMMUNITY – TRANSFERHINWEISE (Boss-Brief), Commit 28f2d6c, Marker az
- Boss-Vorgabe: Such-/Filterbereich unverändert – das CmtySuche-Feld („Hinweise durchsuchen: Spieler, Verein, Position, Stichwort …“ mit
  Treffer-Zähler) ist 1:1 an seiner Stelle geblieben. Networking-Unterbereich inhaltlich unverändert (nur Tab-Label „Networking Pro“).
- Datenlage community_posts: id, kind, author_name/rolle, body, created_at, status (neu/prueft/veroeffentlicht/notiert/freigegeben/abgelehnt/
  gemeldet/zurueckgezogen), meldungen, agent_headline, feed_json, body_en/lang. Aktuell 0 Beiträge. Neue Einreichungen bekommen einen
  strukturierten Kopf im Body: „Art · Verein · Spieler/Position · Zeitraum · Liga“ + Leerzeile + Beschreibung + „Quelle/Kontext: …“;
  sendeCommunity(kind, textOverride, anonym) sendet zusätzlich anonym:true (Backend ignoriert es ggf.; die Karte zeigt ohnehin keinen Autor).
- Neue Komponenten (vor NeedCard): cmParse (Kopfzeile/feed_json → Verein/Position/Zeitraum, Headline = agent_headline oder erster Satz),
  cmStatus (Ungeprüft / Mehrfach gemeldet (≥1 ähnliche: gleicher Verein + Position) / TW geprüft (freigegeben) / Offiziell bestätigt
  (bestaetigt) / Abgelehnt/Zurückgezogen grau), CommunityPanel (Portal rechts 560 px, mobil Vollbild: Art (6), Verein, Spieler oder Position,
  Zeitraum (5), Liga oder Region, Beschreibung mit Boss-Platzhalter, Quelle oder Kontext, Radio mit Profil/anonym, Bestätigungscheckbox,
  „Hinweis zur Prüfung einreichen“ erst gültig ab 10 Zeichen + Checkbox; Esc schließt; schließt nach „✓“), CommunityVue (Warnhinweis kurz +
  „Mehr zur Verifizierung“ mit Status-Erklärung; eingeklappter Composer „Teile einen Transferhinweis aus deinem Netzwerk …“ + „Hinweis erstellen“;
  Karten „COMMUNITY-HINWEIS · <Status>“, Zeit, Überschrift, 3-Zeilen-Clamp, Verein·Position·Zeitraum, ähnliche Meldungen, Prüfstatus-Pill,
  Speichern (tw_saved_hints) / Ergänzen (Panel mit Vorlage aus der Karte) / Melden (meldePost) + Übersetzen; ein Leerzustand „Noch keine
  Community-Hinweise“ + Text + „Hinweis teilen“; rechte Spalte ≥1100 px: Aktueller Prüfstatus (Zähler je Status), Häufig genannte Vereine,
  Community-Regeln). Kopf h2 „Community – Transferhinweise“ + Beschreibung.
- Abnahme rt59: Titel/Beschreibung, Unterbereiche „Transferhinweise · Networking Pro“, Banner-Text exakt + Verifizierungs-Erklärung, Suchfeld
  identisch, Composer statt Formular (kein Textarea sichtbar), Leerzustand mit allen Texten, rechte Spalte (2 Spalten), Panel mit allen Feldern,
  Platzhalter exakt, Button erst nach Text+Checkbox aktiv, Esc schließt; mobil Panel 390 px Vollbild, Feed einspaltig. 0 Fehler.

## 26.08. 04:15–04:25 – NEWSFEED: alter Vereinsfilter wieder da (Boss-Screenshot), Commit 3a0cba7, Marker ba
- Boss: „den alten Filter auf der Seite bitte wieder rein machen“ (Screenshot Newsfeed mit Prompt „Name für diesen Filter“). Befund: Der Kasten
  „Verein gezielt suchen“ (1 · Land wählen → 2 · Liga wählen → 3 · Verein wählen, SelectField-Kaskade aus HIERARCHY) hing an
  `cascade = sport === "fussball" || "basketball"`; sport ist seit dem Basis-Import fest „alle“ und sportTabs = [] → der Kasten war nie sichtbar.
- Fix: hierSport = sport === "alle" ? "fussball" : sport; cascade = !!HIERARCHY[hierSport]; countryOpts/leagueOpts/clubOpts und die Farben
  (SPORT[hierSport].color statt SPORT[sport] – sonst Absturz bei „alle“) darauf umgestellt; Kasten nur bei view === "feed" (nicht Merkliste).
  Filterlogik unverändert (Verein-Auswahl filtert den Feed; Land/Liga nur zur Auswahl). „Aktuellen Filter speichern“ sichert Land/Liga/Verein mit.
- Abnahme rt60: Kasten mit drei Selects (14 Länder; Liga/Verein bis zur Auswahl deaktiviert) zwischen Zähler-Zeile und Chips; Auswahl USA →
  Major League Soccer → Inter Miami CF filtert („Gefiltert nach Inter Miami CF — 0 Meldungen“), Zurücksetzen stellt 60 Karten wieder her,
  Merkliste ohne Kasten, mobil passt (Selects 164/164/336 px). 0 Fehler.

## 26.08. 04:25–04:35 – VERTRAGSRADAR: Filterleiste (Boss-Wunsch per Screenshot), Commit 76ecf13, Marker bb
- Neue Filterleiste in VertragTabelle (oberhalb der Tabelle, unterhalb der Kategorie-Überschrift): Suchfeld „Spieler oder Verein suchen …“,
  Status (Alle / Sofort verfügbar / Endet in 30 Tagen / Endet in 6 Monaten / Vertrag bis 12 Monate), Position (Torwart/Abwehr/Mittelfeld/Sturm),
  Liga (aus den Zeilen), Alter (U21/U23/U25/U30), Marktwert (mit Marktwert / über 1 Mio / über 5 Mio), Quelle (aus den Zeilen); darunter
  Trefferzahl „N Verträge“, „✕ Filter zurücksetzen (n)“ (rot, nur bei aktiven Filtern) und Sortierung (Dringlichkeit/Vertragsende/Marktwert/
  TW Opportunity Score/Alter/Name). Leer-Treffer: „Keine Verträge für diese Filter.“ + Zurücksetzen. Aktive Felder mit dunklem Rand + fett.
  Nebenbei: Positionen der Datenbank-Zeilen (Goalkeeper/Defender/Midfielder/Attacker) auf Torwart/Abwehr/Mittelfeld/Sturm vereinheitlicht (vtPos).
- Abnahme rt61: 7 Selects + Suchfeld, „232 Verträge“; Status „Sofort verfügbar“ → 3 Zeilen, alle vertragslos, „Filter zurücksetzen (1)“; Position
  Mittelfeld → 71 Zeilen; Marktwert vorhanden → 195 Zeilen; Suche ohne Treffer → Leerhinweis; Zurücksetzen → 232; Sortierung Marktwert →
  95,00 / 72,50 / 57,37 Mio. €; mobil alles im Bild, Karten. 0 Fehler.

## 26.08. 04:40–05:00 – HANDY-LAYOUT (Boss-Auftrag), Commits 785f253 / fd54a58 / 4e47271, Marker bc/bd/be
- Prinzip: nur Darstellung, nur ≤760 px (Media Query im App-Style-Block) – Desktop unverändert (rt64: Burger versteckt, 9 Tabs sichtbar,
  Kopf 60 px, LIVE-Text sichtbar, Feed zweispaltig).
- MobilNav (vor NeedCard): Burger-Knopf (.tw-burger, 40×40, drei Striche) als erstes Kind der .tw-headwrap; Portal-Panel links (min(320px,86vw))
  mit Logo, ✕, allen Seiten als Buttons (Symbol NAV_ICONS + Label + Farbpunkt NAV_FARBE, aktive Seite dunkel, 48 px hoch); Auswahl schließt und
  scrollt nach oben; Esc/Overlay schließen; Body-Scroll gesperrt. Klassen ergänzt: .tw-logo, .tw-gsuche-box, .tw-kbd, .tw-tabbar.
- Mobil-CSS: .tw-burger sichtbar, .tw-tabbar (Pillenreihe) aus, Kopf 56 px/Abstand 8/Padding 10, .tw-livetime aus, Logo 24 px/17 px, Suchbox
  ohne Rand-Margin, ⌘K aus; html/body overflow-x hidden; .tw-main Padding 12/12/96, Gap 14, einspaltig, aside in Spalte 1; alle Kopfzeilen
  (h2 inkl. der spezifischen Design-System-Regel und div-Titel [style*="font-size: 30px"]) 24 px/30 px, Beschreibungen 13.5 px; .tw-feedfilter
  wischbar; .tw-feedlist minmax(0,1fr) (Scouting-Karten liefen auf 771 px, weil 1fr Mindestbreite = Inhalt); Karten/Bilder/SVG max 100 %;
  Kennzahlen zweispaltig; .tw-perf-main einspaltig.
- Abnahme rt62/rt64/rt65 (390×800, mobile Emulation): Burger links (13 px), Menü mit 9 Einträgen + 9 Symbolen, Navigation funktioniert;
  alle 9 Seiten: scrollWidth 390 = kein Überlauf, keine Elemente außerhalb (außer in bewusst wischbaren Zeilen), keine Karte breiter als
  das Fenster, Titel 24 px, Beschreibungen 13.5 px (Transfers-Beschreibung 14.5 – Kopf dort anders gebaut, harmlos). 0 Fehler.

## 26.08. 05:00–05:25 – KADER-ABGLEICH: veraltete Vereine (Boss: Han-Beom Lee stand noch bei Midtjylland, spielt seit Aug. für Club Brugge)
- Befund: Der nächtliche Spieler-Sync (zzZkTERPpYvofNhr, 3:30, 7 Ligen/Nacht) nimmt den Verein aus `statistics[0].team` der Abfrage
  players?team=X – bei Wechseln liefert die alte Liga-Nacht wieder den alten Verein (Flattern zwischen Nächten). Die TW-Performance-Tabelle
  wusste es richtig (Fixture 07.08. Club Brugge KV), die players-Tabelle/Datentabelle nicht.
- Neu: Workflow „TW Kader-Abgleich (täglich 5:00)“ (7cz9uum6cWPGK8Sm, aktiv, Error-Workflow gesetzt; SDK-Code in docs/n8n-kader-abgleich.sdk.js):
  Ligen (20) → teams?league → players/squads?team (≈372 Aufrufe, 350 ms Abstand) → Kader-Karte (pid → Verein/Liga, 11.146 Spieler) →
  Spiele laden (Postgres n8n-DB: letzte Fixture je Spieler aus TW-Performance-Tabelle, 30 Tage) → Spieler laden (players) → Vergleich
  (Evidenz: letztes Spiel ≤30 Tage schlägt Kader; sonst API-Kader; Namensvergleich normalisiert) → Batch → UPDATE players (team, league,
  team_source, team_updated_at) + Datentabelle „TW Spieler“ (Update je Spieler, damit der 4:30-Spiegel nichts zurückdreht) → kader_audit
  (status 'kader-abgleich') → Morgenreport per Mail an laurenzrath@gmx.de (Anzahl + Liste).
- Spalten players.team_source/team_updated_at angelegt; Spiegel-SQL sichert sie wie die TM-Spalten (tm_keep).
- Nachtkette jetzt: 2:30 Performance-Analyst → 2:40 TM-Import → 3:30 Kader-Sync (Rotation) → 4:30 Spiegel → 5:00 Kader-Abgleich (korrigiert).
- Erstlauf: 1.022 Korrekturen (995 Kader, 27 Spiel) – u. a. Lee → Club Brugge KV / Jupiler Pro League; Profil-API zeigt Club Brugge.
  Zweitlauf: 48 (Spiel-Evidenz, überwiegend Namensvarianten wie „Vitória SC“ ↔ „Guimaraes“ aus den Fixtures – gleicher Verein, andere
  API-Schreibweise; ab dem dritten Lauf stabil). Bekannte Grenze: API-Kader können bei kleinen Ligen einige Tage nachlaufen; Spiel-Evidenz
  greift dann, sobald der Spieler eingesetzt wird.
- Ideen (offen): bestätigte Transfermeldungen („fix“ mit Spieler + Zielverein) als dritte Evidenz innerhalb von Stunden; Hinweis
  „Verein geprüft am …“ im Profil; Warnung an den Boss, wenn Kader und Spiele >7 Tage widersprechen; Vereins-Aliasliste für die API-Namen.

## 26.08. 05:55–06:20 – QUELLEN-AUSBAU + SYSTEMKONTROLLE + KOSTEN (Boss-Auftrag)
### Quellen (Datentabelle „Transfernews Quellen“ IQk1uY59LjYaOsyi, RSS-Zweig 18462puK0GA3Azyu liest typ='rss')
- Bestand vorher 558 Quellen (davon ~126 RSS; Rest web/offiziell/spezialportal für Voll-Leser/Scouts). 69 + 62 Kandidaten per Server-curl
  geprüft (echtes RSS/Atom mit Items); 54 neue RSS-Quellen eingefügt (INSERT mit NOT-EXISTS auf quelle_url, hinweis „Quellen-Ausbau 26.08.2026“):
  DE Unterhaus: Google-News-Suchen je Regionalliga West/Nord/Nordost/Südwest/Bayern (Transfer/Wechsel/Zugang/Abgang/Probetraining/vereinslos),
  3. Liga (Probetraining/vereinslos/Testspieler/Kaderplanung), 2. Bundesliga (Kaderplanung/Leihe/vertragslos/Vertragsverlängerung), kicker
  Regionalliga, Liga Drei, Sportschau, Bundesliga.com, t-online; Insider (GN-Namenssuchen): Kerry Hau, Patrick Berger, Max Bielefeld, Tobias
  Altschäffl, Christian Falk, Georg Holzner, Ekrem Konur, Mike Verweij, Rik Elfrink, Pedro Sepúlveda, Sébastien Denis, Hugo Guillemet;
  Europa: Mundo Deportivo, SPORT.es, AS (Portada/Primera), Marca (Segunda, Fichajes), RMC Sport, Le Parisien, Ouest-France, Maisfutebol, Zerozero,
  HLN, Voetbalkrant, Walfoot, VI, NOS, AD, Blick, Sky Sport Austria, Kurier, derStandard, Sabah, Hürriyet, Football League World, Football Insider,
  TEAMtalk, 90min, Mirror, Telegraph, Independent. Jetzt 612 Quellen, 180 RSS.
- Ohne RSS (404/403/Bot-Schutz, nur als Web-Quelle möglich): Transfermarkt-News, Sport1, Sky DE, Reviersport, FuPa, Sportbuzzer, Ligainsider,
  FussballTransfers, Foot Mercato, Calciomercato, Corriere/Tuttosport, A Bola, O Jogo, Sporza, Voetbalzone, Tipsbladet, bold.dk, Laola1, Krone,
  Fanatik, TRT, Sporx, Relevo, Fichajes.com – dafür decken die Google-News-Suchen dieselben Häuser ab.
- Vorfilter des RSS-Zweigs erweitert (publiziert): Unterhaus-Signalwörter probetraining, testspieler, trainingsgast, gastspieler, vereinslos,
  vertragslos, kaderplanung, vertragsauflösung, aufgelöst, freigestellt, ausgeliehen, rückkehr, free agent, released, trial, svincolato, libre,
  agente libre; MAX_GESAMT 220→300, MAX_JE_QUELLE 6→5 (Round-Robin über alle Quellen bleibt). Kosten je Lauf gpt-4o ≈ 2–3 Cent.
### Systemkontrolle – KRITISCH
- OpenAI antwortet seit 25.08. 05:20 (lokal) mit „Your organization has reached its configured enforced spend limit“. Betroffen (alle Fehler seit
  dem): EN-Übersetzer (alle 30 Min), TW Analyst Signale→Meldungen (stündlich), Performance-Analyst (2:30, 25.+26.08. fehlgeschlagen – letzte
  Analyse 23.08.), Kaderstärken-Analyst, Verletzungs-Scout, Quellen-Voll-Leser (25.08.), Talent-Scouts, RSS-Zweig (Agent-Knoten fällt still aus,
  Lauf „success“ mit 0 Meldungen). Nicht betroffen: Kader-Sync/Spiegel/Abgleich, TM-Import, API-Football-Syncs, Website-APIs, Mails.
- Nur der Boss kann das lösen: platform.openai.com → Settings → Organization → Limits → Enforced limit erhöhen/entfernen (Empfehlung 200 $ mit
  Warnschwelle 100 $). Danach holen die Stundenläufe automatisch auf; Performance-Analyst/Voll-Leser ggf. manuell nachstarten.
- NEU: „TW Wächter: OpenAI-Limit (alle 6 h)“ (gh8Y00Av9djWPm3o, aktiv): zählt Fehler mit „spend limit“ in execution_data (n8n-DB) der letzten
  6 h; bei >0 Alarm-Mail an laurenzrath@gmx.de mit Ursache, betroffenen Workflows und Anleitung. Testlauf: 21 Fehler seit 02:20 → Mail zugestellt.
### Kosten
- Kosten-Wächter 25.08. 23:50: 0,18 € (24 h) – nur weil OpenAI blockiert; normaler Betrieb (24.08. nach Kalibrierung) ≈ 3 $/Tag ≈ 2,8 €, damit
  unter dem Ziel 5–6 €/Tag. Auffällig: „TW Analyst: Signale → Meldungen“ läuft auf gpt-5.6-terra (0,17 $ für 5 Läufe) – im Rahmen, aber teuerstes
  Modell im Stundentakt; bei Bedarf auf mini umstellen (≈ 0,02 $/Tag).

## 26.08. 14:30 – 27.08. 02:30 – KOSTEN-ERKLÄRUNG, KI-BREMSE, IDEEN-UMSETZUNG (Boss-Auftrag, Screenshots OpenAI Limits/Billing)
### Befund Kosten
- OpenAI-Zähler August 845,75 $ bei hartem Limit 500 $ (Reset 1.9.); Guthaben 47,51 $; Boss lässt das Limit bis Monatsende stehen.
  Tageskosten aus n8n-Daten (Listenpreis-Schätzung): 20.08. 1,20 € · 21.08. 2,80 € · 22.08. 4,55 € · 23.08. 8,70 € · 24.08. 12,70 € (Bedarfs-
  Scout 466 Vereine, abends behoben) · 25.08. 0,18 € (ab 05:20 blockiert). Der Großteil der 845 $ stammt aus 1.–19.08. (Bedarfs-Scout/
  Vertrags-Scout auf gpt-5.5, bis 14.08. zusätzlich n8n-Cloud). n8n-Cloud geprüft: seit 14.08. kein erfolgreicher Lauf (4.080 Fehlläufe seit
  24.08., alle ~40 ms) → verbraucht nichts; Kündigung vor 29.08. bleibt To-do des Boss.
### KI-Bremse (automatisch, ohne OpenAI-Eingriff)
- Tabelle transferwire.tw_status (key/value): ki_bremse (true/false, manuell setzbar) + kosten_24h_eur (vom Kosten-Wächter). Rechte: PUBLIC.
- Kosten-Wächter NZzqmm9gWrQWu4N1 → „TW Kosten-Wächter (4× täglich, KI-Bremse)“: Cron 50 5,11,17,23; schreibt kosten_24h_eur; Mail nur
  um 23:50 oder bei Alarm (>6 €). Testlauf 02:14: sauber (nach GRANT).
- Budget-Gate (Postgres-Read + IF „KI frei?“ direkt nach dem Trigger, fail-open bei DB-Fehler) in: Bedarfs-Scout DE 4BjusAxYNt1uvLue,
  Analyst Signale→Meldungen ifOFnqTVjThmiFEJ, Radar-Agent qoJpIltSvfTGt3Iw, Quellen-Voll-Leser BG4HJKnw43iKL55d, Vertrags-Scout
  3MzOmjVwt8GaLvAs, Frühstarter-Scout TKgRH6vrY51HAgqt (alle publiziert). Scharftest: ki_bremse=true → Frühstarter-Scout stoppte am Gate
  (Ausgabe false-Zweig, keine weiteren Knoten); danach zurück auf false.
### Kader-Abgleich 7cz9uum6cWPGK8Sm erweitert (publiziert)
- Neuer Knoten „Meldungen laden“ (n8n-DB, Transfernews type='fix', reliability ≥ 4, 14 Tage). Vergleich: Alias-Erkennung Spiel-Name ↔ Kader-Name
  (≥4 Spieler und ≥40 % je Spiel-Team), Evidenz Spiel > Kader > Meldung; Meldungs-Verein bleibt 21 Tage vor Kader-Überschreibung geschützt;
  Widersprüche (Spiel vs. Kader, Spiel >7 Tage alt) als Liste; Filter „Nur Aenderungen“ vor Datentabellen-Update; Report mit Quellen,
  Aliasen, Widersprüchen. Erstlauf mit Meldungs-Evidenz: 30 Korrekturen (u. a. Goretzka→Aston Villa, Nkunku→Leipzig, Veerman→BVB).
### Website (Commits 7b7238e, a374ed0; Marker bg/bh)
- VereinGeprueft: liest /db/players?player_id=eq.X&select=team,team_source,team_updated_at → „✓ Verein geprüft am 26.08.2026 · Quelle:
  Kaderliste/letztes Spiel/bestätigte Transfermeldung“ in Vollprofil (plDetail.pid gesetzt) und Schnellansicht (rt67: Schnellansicht ✓;
  Vollprofil-Anzeige im Test nicht erfasst – bei Gelegenheit nachprüfen).
- ProbetrainingRadar (Vertragsradar, unter den drei unveränderten Kategorien): Feed-Meldungen mit Probetraining/Testspieler/Trainingsgast/
  vereinslos/vertragslos/free agent…, bis 12 Karten, Klick öffnet Meldung; Leerzustand. rt66: 12 Karten.
### Quellen
- 13 offizielle Unterhaus-Quellen (typ web, gruppe offiziell) nach Server-Prüfung: Dynamo Dresden, Waldhof, 1860, Osnabrück, Ingolstadt,
  VfB II, Ulm, DFB 3. Liga, Verbände WDFV/NFV/NOFV/BFV, Regionalliga Südwest. Jetzt 625 Quellen (180 RSS, 336 web). 15 Vereinsseiten ohne
  brauchbare News-URL (404/Bot-Schutz/Umleitung auf Nachwuchs) ausgelassen – Google-News-Suchen decken sie ab.
- Zurückgestellt (kostet KI-Geld): Telegram-Kanäle von Regionalliga-Vereinen, Pressekonferenz-Transkripte.

## 27.08. 02:40–03:30 – QUELLEN-MASTERLISTE (Boss-Datei), QUELLEN-CRAWLER, TRANSFERREGISTER
### Master-Liste (docs/quellen/TransferWire_Source_Intelligence_Master.xlsx, Import-SQL docs/quellen/master_2026-08-27.sql)
- Blätter: 01 Länderquellen (181), 02 DE 3./4. Liga (32), 03 APIs, 04 Monitoring, 05 Insider-Netzwerk, 06 Register, 07 Tagesworkflow,
  08 Club-Template, 09 Suchbegriffe, 10 Source-Scoring. Importiert: 174 URL-Quellen aus 01/02 (+ KAP Börsenregister TR) → 123 neu
  (51 bereits vorhanden; Abgleich über normalisierte URL). Bestand jetzt 748 Quellen: web 454, rss 180, spezialportal 46, news 26,
  datenbank 17, offiziell 17, social 6, journalist 2. Vertrauen A1/A2/B → prioritaet 1/2/3, Hinweis „Master-Liste 01/02 · Typ · Stufe“.
- Nicht importierbar (keine URL/Methoden): Club-Websites/Socials je Verein, regionale Zeitungen, Insider-Netzwerk, Register (06, außer KAP),
  Enterprise-APIs (Opta, Sportradar, Wyscout, StatsBomb, SkillCorner, TransferRoom – Lizenz nötig, Boss-Entscheidung).
- Blatt 09 Suchbegriffe (10 Sprachen) in den RSS-Vorfilter übernommen (publiziert).
### Prüfung „wird jede Quelle von einer KI gelesen?“
- RSS (180): ja – RSS-Zweig stündlich, KI-Strukturierung. Web-Quellen (≈560): bisher nur indirekt über den Voll-Leser (Websuche-Agent mit
  15er-Paketen) – nicht nachweisbar. APIs: API-Football (Kader/Verletzungen/Spiele), Sportmonks (Gerüchte 2 h, Ausfälle), football-data,
  Transfermarkt-Import, Google-News-Ligen (30 Min → Signale → Analyst), Telegram (15 Min), Quoten: alle aktiv und ausgewertet.
  Lücke: API-Football-Transfers-Endpunkt war unbenutzt (alter Transfer-Radar inaktiv).
### NEU „TW Quellen-Crawler (4× täglich, KI-Leser)“ AjYML5ljn0U18vMi (aktiv; SDK docs/n8n-quellen-crawler.sdk.js)
- Cron 6:05/11:05/15:05/20:05 → Budget-Gate → Quellen laden → Auswahl (70 fällige, typ web/offiziell/news/spezialportal/journalist/datenbank;
  Takt Prio 1 = 20 h, Prio 2 = 44 h, Prio 3 = 68 h, längst überfällige zuerst) → Seite laden (HTTP, UA, 20 s, 4 parallel) → Text extrahieren
  (Skripte/Styles raus, Überschriften/Teaser 24–220 Zeichen, max 70 Zeilen/6000 Zeichen, Hash) → nur veränderte Seiten → KI-Leser
  (Agent gpt-5-mini, reasoning low, max 1200 Tokens, Parser items[]; Regeln: Typen, Verlässlichkeit nach Quellenstufe A1/A2/B, eigene Worte,
  max 15 je Seite) → Ergebnisse splitten → Transfernews-Upsert (dedup_key wie RSS) + Quellen-Update (zuletzt_gelesen, lese_status,
  inhalt_hash, funde_gesamt). Unveränderte/nicht abrufbare Seiten: nur Status-Update, kein KI-Aufruf. KI-Fehler → Status ki_fehler, alter
  Hash bleibt (Seite wird erneut gelesen). Error-Ausgang des Agenten angebunden. Neue Datentabellen-Spalten: zuletzt_gelesen, lese_status,
  inhalt_hash, funde_gesamt.
- Testläufe: kompletter Durchlauf grün; erste 70 Seiten: 52 lesbar (ki_fehler wegen OpenAI-Sperre), 13 nicht abrufbar (kicker, AS,
  Telegraaf, Sky DE/AT Akamai, 2× 404), 5 leer (JS-Seiten: Transfermarkt-Gerüchte, Ligue1, beIN). Kosten: Abrufe kostenlos, KI ≈ 0,002 $/Seite
  → ≈ 0,3–0,5 €/Tag; hängt an der KI-Bremse.
- Voll-Leser BG4HJKnw43iKL55d (publiziert): liest nur noch typ social und Quellen mit lese_status nicht_abrufbar/leer (max 12 Pakete).
### NEU „TW Quelle: API-Football Transferregister (täglich 6:40)“ mZ1U4AuDr6IArMLe (aktiv; SDK docs/n8n-apifootball-transferregister.sdk.js)
- teams je Liga → transfers?team (372 Aufrufe) → Transfers der letzten 4 Tage → fix/leihe, Abgang ohne neuen Verein = verfuegbar; Dubletten
  je Spieler/Ziel (frühestes Datum); Anreicherung Position/Alter/Nationalität aus players → Transfernews (reliability 5, Quelle
  „API-Football (Transferregister)“, news_id af-<pid>-<datum>). Kein KI-Aufruf. Test: Di Gregorio (Leihe Juventus→Bournemouth), Delap
  (Chelsea→Nottingham Forest) korrekt angelegt.

## 27.08. 03:30–07:35 – PUNKTE 1–5 AUS DEM QUELLEN-KONZEPT (Boss: „Go, 1–5“)
### 1 Vertrauensregister (Quellentabelle, Spalten vertrauen + trefferquote)
- Alle 1.112 Quellen eingestuft (Heuristik aus Master-Liste-Stufe, Typ, Gruppe, Name): A1 98 offizielle Quellen, A2 156 Qualitäts-/
  Fachredaktionen (inkl. benannte Reporter auf X: Romano, Ornstein, Bogert, Falk, Süzgün, Manav, Sabuncuoğlu, Merlo), B 434 Fachmedien
  (Transfermarkt-Seiten B, Gerüchteseiten C), C 43 Aggregatoren/Boulevard, D 17 Social/anonym (Club-Weibo, MLS-Transfers-X, bold.dk-X …).
- KI-Leser des Crawlers: Vertrauensstufe im Prompt, reliability strikt A1 5/4, A2 4/3, B 3/2, C 2, D 1. RSS-Zweig: Vorfilter hängt je Zeile
  „| Vertrauen: X“ an (Host- und Namensabgleich mit der Quellentabelle), System-Prompt mit denselben Regeln; „fix“ aus C/D bleibt geruecht.
  RSS-Modell auf gpt-5-mini (reasoning low) umgestellt, Takt 2 h (544 Feeds), Deadline-Day-Crons bleiben.
- Befund nebenbei: Im n8n-Code-Knoten ist die URL-Klasse nicht verfügbar → Host-Extraktion per Regex; dadurch war im Vorfilter bislang jede
  Direkt-Feed-Quelle als „unbekannt“ gruppiert (Fairness-Rotation lief nur über Google-News-Publisher) – behoben.
- Spiegel „TW Quellen-Spiegel: Vertrauen & Trefferquote (täglich 5:40)“ N0TZDpClMkxQlHJb → transferwire.quellen_vertrauen (id, quelle_name,
  host, vertrauen, trefferquote, typ, land; PostgREST-lesbar, 1.112 Zeilen, 633 echte Hosts).
- Website (Marker bi–bl): TW_QV lädt das Register (5 Seiten à 200), quellenStufen()/besteStufe() ordnen Meldungen über Host (Basis-Domain)
  oder Namen (exakt vor Teilstring, best-eingestuft) zu; generische Social-Hosts (x.com, t.me, weibo, facebook, youtube) werden nicht auf
  Meldungen übertragen. Signalstärke: A1 +6, A2 +3, C −6, D −12, Trefferquote ±5 um Basis 20 %. Label „Quellenvertrauen: hoch (A2 ·
  Qualitätsmedium)“.
### 2 Bestätigungsregel
- istBestaetigt(): reliability 5 ODER eine A1-Quelle ODER ≥2 unabhängige A1/A2-Hosts. Fix-Karten ohne Bestätigung zeigen orange „Als fix
  gemeldet · noch nicht offiziell bestätigt · NN/100“, bestätigte „✓ Bestätigt · offizielle Vereinsmeldung/zwei unabhängige Quellen“.
  Filter/Zähler unverändert. rt68 live: Newsfeed 60 Karten, 9 bestätigt, 3 unbestätigte Fix; FIXER-DEAL-Ansicht 60 Karten: 15 bestätigt,
  45 „als fix gemeldet, noch nicht offiziell bestätigt“.
### 3 Vereinsgenaue Abdeckung
- 364 Google-News-Vereinsfeeds (docs/quellen/vereinsfeeds_2026-08-27.sql) für alle Vereine der 20 Ligen (Landessprache, Signalwörter je
  Liga, Aliase z. B. FC Bayern, PSG, Inter Mailand, LASK, Vitória Guimarães, chinesische Vereinsnamen); 38 DE-Klubs hatten bereits Feeds.
  Bestand: 1.112 Quellen, 544 RSS, 364 Vereinsfeeds (gruppe verein, prioritaet 2, vertrauen B).
### 4 Wöchentlicher Abdeckungs-Check „TW Wächter: Vereins-Abdeckung (Mo 8:30)“ J6PJYwujKjnSR6qr (aktiv)
- Vereine aus players (≥12 Spieler) × Meldungen 7 Tage (to/from/headline, normalisierter Kern) × Quellen (Name enthält Kern, Lesestatus);
  Mail mit Zahlen je Liga und Lückenliste. Erstlauf: 405 Vereine, 75 ohne Meldung, 11 ohne Quelle (Woche mit OpenAI-Sperre).
### 5 Quellen-Trefferquote „TW Wächter: Quellen-Trefferquote (Mo 8:45)“ EaHE49hWsOAeOE1X (aktiv)
- Gerüchte (30 Tage, ≥10 Tage alt) je Quelle vs. spätere Bestätigungen (fix/leihe, reliability ≥4 oder API-Register; Name sortiert +
  Vereinskern). Schreibt Quote nur bei Freigabe (≥20 bestätigte Gerüchte und ≥40 Bestätigungen im Fenster, min. 10 Gerüchte je Quelle),
  sonst Report ohne Schreiben. Erstlauf zeigte 0–5 % (OpenAI-Sperre, kaum Bestätigungen) → vorläufige Quoten zurückgesetzt (NULL).

## 27.08. 07:45–08:20 – GDELT-FRÜHWARNSYSTEM (Boss: „Setze GDELT um“)
- NEU „TW Quelle: GDELT Lokalmedien (alle 2 h)“ CQkmqmoN0VJvyunK (aktiv, Cron 35 */2; SDK docs/n8n-gdelt-lokalmedien.sdk.js):
  Budget-Gate → Vereine laden (players, ≥12 Spieler) → 10 sprachspezifische GDELT-DOC-Abfragen (german, english, spanish, italian, french,
  dutch, portuguese, turkish, danish, chinese; Transfer-Signalwörter + sourcelang:<Sprache>, timespan 3 h, max 250, 15 s Abstand, 90 s
  Timeout, 2 Versuche – GDELT antwortet 20–40 s und drosselt bei schnellen Folgeaufrufen mit 429) → Vereinsfilter (Titel muss vollen
  Vereinsnamen ODER Vereinskern ≥5 Zeichen + Transfer-Signalwort enthalten; Stoppliste generischer Wörter wie berlin/standard/young/city)
  → Neu? (transferwire.gdelt_seen, INSERT … ON CONFLICT DO NOTHING RETURNING, 7-Tage-Bereinigung) → Zeilen (max 150) → KI (gpt-5-mini,
  reasoning low; Lokalmedien = Stufe B, reliability max 3, fix nur bei klarem Vollzug) → Einzelmeldungen → Transfernews-Upsert
  (news_id gd-…, reliability zusätzlich auf ≤3 gedeckelt, source_name = Domain). KI-Fehler enden im NoOp „KI nicht verfuegbar“.
- GDELT-Syntax: Sprachfilter braucht den vollen Namen (sourcelang:german, nicht ger); OR-Klauseln mit CJK-Termen werden abgelehnt →
  chinesisch als UND-Abfrage „足球 转会“.
- Testlauf 08:03: 9 Kandidaten nach Filter (u. a. fnp.de „Eintracht Frankfurt plant Last-Minute-Transfers“, blueprint.ng Arsenal/Álvarez,
  Sounders-Brief) – vor der Verschärfung noch Politik-/Regionaltreffer (trend.at „Berlin“, „Standard“ als Zeitung); danach strenger Filter.
  KI-Schritt blockiert bis 1.9. (OpenAI-Limit). Kosten ab dann ≈ 12 Läufe × ≤150 Zeilen gpt-5-mini ≈ 5–10 Cent/Tag.

## 27.08. 08:25–10:50 – SPIELERDATEN AKTUELL HALTEN (Boss: Marktwerte für alle, Änderungen sofort, spezialisierter Agent)
### Marktwerte
- Befund 08:25: 2.389 von 15.338 Spielern (15,6 %) mit Marktwert – nur die 6 großen Ligen (Handnachzug 26.08.), 14 Ligen bei 0 %, weil der
  Transfermarkt-Import (xZDGcMSlCMFeofXw, Zeiger tm_state.liga_index) nur EINE Liga je Nacht rotiert.
- Backfill: Trigger vorübergehend auf */5 Minuten → 27 Läufe (je ≈45 s), alle 20 Ligen einmal durch. Stand 10:44: 8.074 Spieler (52,6 %)
  mit Marktwert, 8.360 mit TM-Vertragsende. Je Liga: Bundesliga 83 %, Premier League 73 %, 2. Bundesliga 73 %, Schweiz 61 %, Serie B 60 %,
  Serie A 57 %, Ligue 1/LaLiga 55 %, Eredivisie 54 %, Jupiler/Ligue 2 52 %, Championship 51 %, 3. Liga/Süper Lig 50 %, Superligaen 49 %,
  Liga Portugal 46 %, Österreich 45 %, MLS 44 %, LaLiga 2 40 %, CSL 27 %. Rest: Namens-Mismatch (Transliteration, Kurznamen) oder Spieler
  ohne TM-Eintrag (Nachwuchs/Reserve) → nächster Schritt „Matching-Verbesserung“ (TM-ID/fuzzy), wenn gewünscht.
- Trigger zurückgestellt (publiziert): 2:40 + 3:10 → zwei Ligen je Nacht, jede Liga alle 10 Tage frisch.
### NEU „TW Spieler-Aktualisierer (alle 30 Min, aus Meldungen)“ C1ydwWyabs7oba1I (aktiv, Cron 10,40; SDK docs/n8n-spieler-aktualisierer*.js)
- Ohne KI. Wasserzeichen tw_status.aktualisierer_bis → neue Transfernews (createdAt > Wasserzeichen, type fix/leihe/vertrag/verfuegbar) →
  Verletzungen (injuries, 10 Tage) → players → Entscheiden: Spieler-Zuordnung über normalisierten Namen (Tokenreihenfolge egal), bei
  Initialen („L. Delap“) Nachname + Anfangsbuchstabe, bei Mehrdeutigkeit Vereinskontext (from/to_club); Regeln: fix/leihe ab reliability 4 und
  Zielverein in players bekannt → team/league/letzter_verein/team_source 'Meldung'; verfuegbar ab 3 → team 'Vereinslos'; vertrag ab 3 mit
  Jahr im Text („bis 2028“, „verlängert … 2028“) → contract_until YYYY-06-30, contract_source 'Meldung'; Verletzungen → fitness_note
  „Verletzt: <Grund> · seit DD.MM.“ (Grund-Filter: keine Sperren, Trainerentscheidungen, Inactive, Transferverhandlungen, Leihvereinbarungen),
  Genesene zurück auf leer. Schreibt players (UPDATE via unnest), Datentabelle „TW Spieler“ (team/league, damit der Spiegel nichts zurückdreht),
  Historie spieler_aenderungen (player_id, feld, alt, neu, quelle, news_id, reliability) und das Wasserzeichen.
- Erstläufe: 90 Meldungen → 4 Vereinswechsel (Jensen→Lorient via Foot Mercato/offiziell, Di Gregorio→Bournemouth, Kellyman→Strasbourg,
  Hadjam→Brighton via Transferregister); Verletzungen: 512 Profile mit Ausfall versehen (Witsel, Nkunku, Reus, Trippier, Musiala, de Ligt …).
  Vorher: injuries hatte 815 Zeilen, aber kein einziges Profil einen fitness_note – Lücke geschlossen.
- Website (Marker bm): VereinGeprueft zeigt zusätzlich die letzten 3 Änderungen (Datum · Feld: alt → neu (Quelle)) aus
  /db/spieler_aenderungen; PostgREST-Lesezugriff für web_anon.
### Aktualisierungs-Takte jetzt
- Verein/Liga: ≤30 Min nach bestätigter Meldung (Aktualisierer) + täglich 5:00 Kader-Abgleich (API-Kader/Spiele) + 6:40 Transferregister.
- Verletzungen: 6:45/13:00 API-Football + 6:50 Sportmonks → ≤30 Min später im Profil. Vertragsende: aus Meldungen ≤30 Min, TM alle 10 Tage.
- Marktwerte: TM alle 10 Tage je Liga (Quelle aktualisiert selbst nur schubweise). Kosten: 0 € KI.

## 28.08. 04:20–05:00 – TM-MATCHING-VERBESSERUNG (Stufen 7–10) + SELBSTBEENDENDER BACKFILL
### Befund (aus kader_audit, ~2.900 protokollierte Unmatched mit MW ≥ 100 Tsd.)
- Muster: (a) Nordische Sonderzeichen – ø/æ/ß/ł/đ werden von NFD nicht zerlegt und wurden bisher ersatzlos gestrichen
  („Gytkjaer" ↔ „Gytkjær", „Søndergaard"/„Sondergaard"); (b) Zusatz-/Spitznamen („Fiete Arp" ↔ „Jann-Fiete Arp",
  „Marlon Mena Martinez", Mononyme wie „Suso", „Giulio", „Everson Jr"); (c) Spieler bei uns unter anderem Verein;
  (d) echte Datenlücken (Neuzugänge ohne players-Eintrag) – nicht per Matching lösbar.
- Geblockte Kaderseiten: 5× Süper Lig (257-Byte-Antworten), je 1× VfB II / leer – Rotation holt sie nach.
### Import xZDGcMSlCMFeofXw erweitert (publiziert, aktive Version 1ea659a5 gegengeprüft)
- SPEC-Transliteration vor NFD: ß→ss, æ→ae, ø→oe, œ→oe, đ/ð→d, þ→th, ł→l (zusätzlich zu ı/ş/ğ/ç).
  Suffixe jr/junior/ii–iv aus normWorte gefiltert (nur bei mehrteiligen Namen).
- Neue Matching-Stufen (alle nur bei Eindeutigkeit): 7 Digraph-Kollaps (ae/oe/ue/aa → Grundbuchstabe, beidseitig,
  Team-Index); 8 Token-Teilmenge im Team (kürzerer Name vollständig im längeren, ≥ 2 Tokens); 9 Mononym (≥ 4 Zeichen)
  gegen eindeutigen Nachnamen ODER Mononym im Team; 10 ligaweit Erster+Letzter-Wort eindeutig (Spieler unter anderem
  Verein bei uns). Stufen-Zähler s1–s10 im Node-Output und im kader_audit-Feld korrigiert.stufen.
- Testlauf Bundesliga (Österreich): 218/241 gematcht (90 %), 18 unmatched = fast nur echte Datenlücken, 8 Kurznamen geheilt.
### Selbstbeendender Backfill (kein „Trigger vergessen" mehr möglich)
- tw_status-Schlüssel tm_backfill_bis (Timestamp). Liga-Zeiger rückt nur vor, wenn Minute nicht durch 6 teilbar
  (= Nachtläufe 2:40/3:10) ODER now() < tm_backfill_bis. Dritter Cron */6 * * * * im Trigger; nach Ablauf des Fensters
  liefert der Zeiger keine Zeile, „Liga vorbereiten" endet leer – kein TM-Abruf, kein Audit-Eintrag.
- Fenster gesetzt: bis 05:05 UTC (≈ 25 Läufe = kompletter 20-Ligen-Durchlauf). Erster */6-Lauf 02:30 UTC grün (31 s).
- Für künftige Backfills: nur tm_backfill_bis neu setzen (INSERT … ON CONFLICT), kein Trigger-Umbau nötig.
  Der */6-Cron kann dauerhaft stehen bleiben (No-Op außerhalb des Fensters, nur ein DB-Read alle 6 Min).
### Systemcheck
- Fehlläufe seit 27.08. mittags ausschließlich bekannte OpenAI-Sperre-Opfer (EN-Übersetzer :25/:55, Analyst :20,
  vereinzelt Frühstarter-Scout/Voll-Leser) – erwartbar bis Limit-Reset 1.9. Nicht-KI-Strecken sauber.
- OFFEN: Doku-Push ins Repo ausstehend (kein Klon auf dem Server, GitHub-Token lag der Session nicht vor) –
  dieser Nachtrag als Datei übergeben, bitte in docs/FORTSCHRITT.md anhängen und committen.

## 28.08. 05:55–06:10 – TM-VOLLPARSER (Boss: alle Infos auslesen, Luecken fuellen, dauerhaft aktuell)
### Befund vorab
- Formate in players: Groesse "187", Nationalitaet englisch, Geburtsdatum ISO; Position deutsche Buckets, aber 264x "Forward" + 7x "?" inkonsistent.
- Luecken: 3.369 Groesse, 1.543 Geburtsdatum, 1.488 Nationalitaet. Fuss/Im-Team-seit/TM-Verein gab es gar nicht.
- KRITISCH entdeckt: "TW DB: Spieler-Spiegel (4:30)" macht TRUNCATE players + Neuaufbau aus der n8n-Datentabelle und rettet nur eine
  feste Spaltenliste. Dadurch wurden letzter_verein/contract_source (Spieler-Aktualisierer vom 27.08.) und der Meldungs-Vertrag
  TAEGLICH GELOESCHT – stiller Datenverlust seit gestern.
### Umsetzung (alles ohne KI, 0 EUR)
- ALTER players: + foot (text), tm_joined (date), tm_team (text, in unserem Team-Vokabular = Verein laut TM-Kaderseite).
- /opt/transferwire/tw_players_sync.sql neu (Backup .bak-2026-08-28): tm_keep-Rettungsliste erweitert um foot, tm_joined, tm_team,
  letzter_verein, contract_source; Meldungs-Vertrag bleibt erhalten (contract_until aus keep, wenn contract_source='Meldung').
  Syntax im Rollback-Trockenlauf geprueft. Naechster Spiegel-Lauf 29.08. 02:30 UTC nutzt die neue Datei.
- Import xZDGcMSlCMFeofXw (publiziert, aktive Version f675d8a3): Kaderseite /plus/1 vollstaendig geparst je Zeile –
  Position (TM-Detail -> Torwart/Abwehr/Mittelfeld/Sturm; Suche nur im Zeilenkopf, damit "Sturm Graz" in Abgebender-Verein nicht
  faelscht), Geburtsdatum+Alter (Datum mit Klammer-Alter), Nationalitaet (erste Flagge, DE->EN-Woerterbuch ~95 Laender),
  Groesse ("1,87 m" -> "187"), Fuss (kleingeschriebene Zelle rechts/links/beidfuessig), Im-Team-seit (mittleres von 3 Daten),
  tm_team = zugeordneter Verein.
- Schreiblogik: TM-eigene Felder (tm_*, foot) immer aktualisieren; Bio-Felder NUR fuellen, wenn leer – Ausnahme Position auch bei
  "?"/"Forward" (Normalisierung). Kein Ueberschreiben gepflegter API-Werte.
- Dual-Write: Bio-Fuellungen zusaetzlich in die n8n-Datentabelle (erweiterter Heilen-Node), damit der 4:30-Spiegel nichts zurueckdreht.
- Vereins-Konflikte: je Lauf Liste "DB-Verein != TM-Kader-Verein" mit Beispielen im kader_audit (korrigiert.konflikte). Der Import
  schreibt team NICHT selbst – Verein bleibt Sache von Kader-Abgleich (5:00, Evidenz Spiel>Kader>Meldung) und Spieler-Aktualisierer.
- Test Serie B: 535/603 gematcht, Fuellgrade posi/nat/geb 100 %, gr 93 %, fuss 97 %, joined 96 %; 12 Konflikte erkannt
  (u. a. Bonfanti Mantova->Pisa). players + Datentabelle verifiziert (Insigne 163/Sturm/rechts/Sampdoria).
- Backfill-Fenster bis 06:34 UTC verlaengert -> kompletter 20-Ligen-Durchlauf mit Vollparser laeuft automatisch, danach Nachtbetrieb
  (2 Ligen/Nacht, jede Liga alle 10 Tage frisch inkl. aller neuen Felder).
### OFFEN / naechste Schritte
- tm_team als vierte Evidenz in den Kader-Abgleich 7cz9uum6cWPGK8Sm einspeisen (eigene Session, laeuft gegen Live-Team-Daten mit
  21-Tage-Schutzlogik – nicht im Schnellverfahren aendern).
- Website-Anzeige der neuen Felder (Fuss, im Verein seit, TM-Verein-Vergleich im VereinGeprueft-Block): braucht index.html-Commit ->
  GitHub-Zugang noetig. Bereits sichtbare Felder (Position/Alter/Nationalitaet/Groesse/Geburtsdatum) erscheinen sofort in den
  Profilen, da die Seite sie aus /db/players liest.
- "Forward"-Restbestand (260) bereinigt sich im laufenden Durchlauf, sobald MLS/die betroffenen Ligen drankommen.

## 28.08. 06:30-06:45 - SCOUTING-VERTIEFUNG (Boss: bessere Quellen, Jugend-Fokus DE/EN/FR/ES, Agent auf Scout-Attribute trainieren)
### Jugend-Datenlage (API-Football-Discovery, Draft-Sandbox im Jugend-Kader-Sync)
- England reich: 695/696 U18 PL North/South, 702 PL2 Div One, 703 Professional Development League, 987 U18 PL Championship, 1068 FA Youth Cup.
- Deutschland: nur 488 U19 Bundesliga (im Katalog, /players liefert 0) + 715 DFB Junioren Pokal. Frankreich/Spanien: KEINE Jugendligen in der API.
- Jugend-Kader-Sync vCN7P6mcC9yf7kvw um alle EN-Wettbewerbe + 715 + UYL 2026 erweitert (publiziert, aktiv 3300fa5b). Produktionslauf zeigt:
  die NEUEN Liga-IDs liefern derzeit results:0 (Coverage fehlt API-seitig) - Konfiguration bleibt, greift automatisch sobald API pflegt.
  players_youth bleibt vorerst PL2 2025 (355) + UYL 2025 (211); DE/FR/ES-Jugend laeuft bewusst ueber Meldungsquellen + Maennerfussball-Block.
### Quellen (25er-Jugend-Paket, gruppe='jugend', 24 neu eingespielt, Bestand 1.136)
- 23 Google-News-RSS sprachspezifisch: DE (DFB-Nachwuchsliga, U19/U17 Talent, NLZ, A-Junioren, Profidebuet, DFB-U-Teams),
  EN (PL2, U18 PL, FA Youth Cup, Academy Debut, Wonderkid, Professional Contract), FR (Gambardella, Centre de formation, U19 Nationaux,
  Premier contrat pro), ES (Division de Honor Juvenil, Cantera Debut, Juvenil A, La Masia, Canterano), INT (UEFA Youth League)
  + 2 offizielle Webquellen (dfb.de/dfb-nachwuchsliga, premierleague.com/academy; eine davon Dublette).
### RSS-Zweig 18462puK0GA3Azyu (publiziert, aktiv a2151011)
- Vorfilter-Schluesselwoerter um Jugend-Signale erweitert (Profivertrag/Profidebuet, hochgezogen/aufgerueckt/promoted, Jugendwettbewerbe
  DE/EN/FR/ES, NLZ/Academy/Cantera/La Masia, U-Berufungen, Wonderkid, Talent).
- KI-Systemprompt TALENT-REGEL: Karriereschritte von U16-U21 (erster Profivertrag, Aufruecken/Profidebuet -> type vertrag, Akademie-Wechsel
  wie ueblich) sind Meldungen; reine Spielberichte weiter ignorieren; Jugendligen als league zulaessig.
- Mapping: neues Feld talent (boolean, deterministisch: player_age 15-20 ODER Jugend-Signalwort in headline/summary/league) - davon liest
  der Scout-Agent (WHERE talent=true). Talent-Pipeline nachweislich aktiv (Meldungen u.a. von Romano, TMW, Chelsea offiziell, Jugend-Feeds).
### Scout-Agent Profil-Bau iVt2oygA1gPIMf0Y (publiziert, aktiv f9c32f37) - "Antrainierung" auf Scout-Attribute
- Stats-Input komplett neu: Top 150 Jugendliga (season>=2025, minutes>0) + Top 130 MAENNERFUSSBALL-FRUEHSTARTER (players, Alter 15-19,
  minutes>0) als zweiter Block; je Spieler zusaetzlich p90 (ab 180 Min), Groesse, starker Fuss, TM-Marktwert, Nationalitaet, Vertragsende
  via LATERAL-Join auf players (Name + Alter +-1, Vereinskern-Praeferenz gegen Namensdoppler). Test: 145 Zeilen, 104x Groesse, 89x MW.
- KI-Bremse nachgeruestet (einziger KI-Workflow ohne Gate): SQL-Gate in Stats laden - 0 Zeilen bei ki_bremse=true, fail-open.
- Prompt: Chef-Kriterien unveraendert + neuer Attribute-Block: Alter-RELATIV lesen (16/17 mit Maennerminuten staerkstes Signal),
  Groesse im POSITIONSKONTEXT (TW/IV ~188+ Plus, nie alleiniges K.o.), starker Fuss aus Datenfeld belegt uebernehmbar (Linksfuss/
  beidfuessig als Marktplus in strengths), MW/Vertrag als Unentdeckt-Signal, DATENLAGE-Hinweis (EN-Jugendstats vs. DE/FR/ES via
  Meldungen), LAENDERFOKUS DE/EN/FR/ES. Neues Ausgabefeld groesse (nur belegt, 150-210) bis in talent_profiles (Spalte ergaenzt).
- Aktiv ab 1.9. (OpenAI-Limit); Draft-Test bestaetigt Datenfluss bis zum KI-Node (dort erwartungsgemaess 429).
### Kosten
- Alles Non-KI sofort aktiv, 0 EUR. Ab 1.9.: Jugend-Feeds erhoehen RSS-Volumen marginal (Cap 320 Zeilen bleibt), Scout-Agent weiterhin
  1x taeglich gpt-5-mini (~77k Zeichen Input, Cent-Bereich). API-Football: +~15 Leerabfragen/Tag fuer Jugendligen.

## 28.08.2026 (Vormittag): TM-Vollausbau Teil 2 - TM-ID-Matching, TM korrigiert API-Werte, Kader-Abgleich mit TM-Evidenz, Profilfelder live

### Transfermarkt-Import (xZDGcMSlCMFeofXw, aktive Version d34769fc)
- Stufe 0: Direktabgleich ueber gespeicherte tm_id VOR den Namensstufen 1-10 ("Unsere Spieler laden" inkl. tm_id, tmIdMap nur eindeutige
  IDs). Wirkung nach Backfill: Liga Portugal 401/536 mit s0=401, Serie B 535 s0=535, Jupiler 440 s0=440, Schweiz 325 s0=317.
- TM korrigiert jetzt DAUERHAFT falsche API-Werte bei Geburtsdatum und Groesse (COALESCE TM-first) - in players UND in der Datentabelle
  TW Spieler (Heilen-Node), damit der 4:30-Spiegel nichts zurueckdreht. Nationalitaet/Position bewusst weiter fuell-/reparatur-only.
- Vereins-Zuordnung zweistufig repariert: (a) Kandidaten-Sammlung statt Erster-Substring-gewinnt, (b) Token-Vergleich mit
  Praefix-Toleranz ab 5 Zeichen + Disambiguierung ueber Erste-Token-GLEICHHEIT, sonst ueberspringen. Behobene Fehlmuster inkl.
  Datenreparatur per gezieltem Neulauf (Zeiger setzen, manueller Lauf): Espanyol->Barcelona (LaLiga), Club Brugge->Cercle Brugge 21x
  (Jupiler), Grasshoppers->FC Zurich 23x (Schweiz). Danach 0 Mehrfach-Muster, 60 echte Einzelfall-Konflikte.
- Achtung Zeiger-Semantik: tm_state.liga_index zeigt auf die NAECHSTE Liga (Zeiger=2 -> Lauf macht Index 2 = PL). Nach Fensterende
  liefert der Liga-Zeiger bei minute%6==0 nichts (Leerlauf) - dann 1 Min spaeter erneut ausfuehren.

### Kader-Abgleich (7cz9uum6cWPGK8Sm, aktive Version 06e678e3)
- TM-Kader als VIERTE Evidenz nach Spiel > API-Kader > Meldung. Guards: tm_updated_at <= 12 Tage, tm_team via findeKaderTeam aufloesbar,
  kein Spiel fuer den bisherigen Verein in den letzten 7 Tagen, API-Kader widerspricht nicht (fehlt oder = DB-Team), 21-Tage-
  Meldungsschutz. Quelle 'TM-Kader' in team_source; Zaehler tmTreffer im Meta; Audit-Quellen + Morgenreport-Text ergaenzt.
- Testlauf 06:16 (nach Datenreparatur): 58 Korrekturen (55 TM-Kader, 3 Meldung), 15 Widersprueche nur geloggt. Beispiele: Bazunu
  Stoke->Southampton, Asllani Torino->Inter, Ilic Torino->Lecce, Pinnock Brentford->Coventry, Marmoush ManCity->Tottenham, Skhiri
  Frankfurt->1.FC Koeln. Kein einziger Fehlmove aus den reparierten Mustern. Konflikte DB<->TM danach: 5 (Guards halten sie korrekt).

### Website (Commit 1a41281, Marker 2026-08-28-bn tmfelder)
- VereinGeprueft-Block (DB-Karte + Spielerprofil) zeigt jetzt: Fuss (rechts/links/beidfuessig), "Im Verein seit" (tm_joined) und bei
  Abweichung den Amber-Hinweis "TM-Kader fuehrt: X (Stand ...)"; Quellen-Mapping um 'TM-Kader' ergaenzt; DE/EN inline im
  Komponentenmuster (keine EN_MAP-Eintraege noetig). PostgREST-Select um foot,tm_joined,tm_team,tm_updated_at erweitert.
- Livetest rt69 (docs/tests/rt69.py, laeuft im tm-fetcher): Inacio "Fuss: links - Im Verein seit 01.07.2020", Bazunu-Hinweis
  "TM-Kader fuehrt: Southampton", 0 pageerrors. Fuer kuenftige Tests: Nav-Tab heisst exakt "Spieler" (Klick am besten ueber Nachbarschaft
  zum "Performance"-Button), DB-Suchfeld-Placeholder ist "Spielername oder Verein (mind. 2 Zeichen) ..." (NICHT "Spieler oder Verein").

### Betrieb / Zahlen
- Backfill-Fenster 06:03 geschlossen, Liga-Zeiger steht auf 18 -> heute Nacht MLS + CSL, Rotation normal (jede Liga ~alle 10 Tage).
- Fuellstaende (15.433 Spieler): tm_id 8.578, MW 8.286, Fuss 7.924, Im-Verein-seit 7.997, tm_team 8.400; Geburtsdatum leer 1.221->1.018,
  Groesse leer 2.718->2.256. KI-Kosten: 0 EUR.
- Offen (Boss-Entscheidung): TM-Neuanlage komplett fehlender Spieler (z. B. Porto-Neuzugaenge Nehuen Perez, Alberto Costa, Seko Fofana,
  Gabri Veiga; braucht Dual-Write + synthetische IDs wegen Spiegel-TRUNCATE) und Profilseiten-/Berater-Scraping (Stufe 2, rechtliche
  Abwaegung; nicht angefasst).

## 28.08.2026 (Vormittag, Teil 2): Scouting-Vertiefung - neue Quellen DE/EN/FR/ES + Scout-Agent mit Formkurve und Performance-Analyse

### Neue Quellen (Register data_table_user_IQk1uY59LjYaOsyi, alle vor Eintrag live per curl getestet)
- 10 neue Zeilen (ids 1137-1146), gruppe jugend/unterhaus/medien, prio 2, vertrauen B, hinweis 'Scouting-Vertiefung 28.08.2026':
  DE: kicker Amateure & Nachwuchs (newsfeed.kicker.de/news/amateure), GN Perspektivspieler, GN Regionalliga Talent Profivertrag.
  EN: The72 (EFL). FR: Jeunes Footeux /rss/ (Talent-Blog!), Top Mercato, But! Football Club. ES: AS Segunda Division
  (as.com/rss/futbol/segunda.xml, 68 Items), GN Cantera Perla, GN Primera Federacion Filial.
  Football League World + Football Insider waren bereits im Register (Dubletten-Schutz via NOT EXISTS auf quelle_url).
- Der RSS-Zweig (18462puK0GA3Azyu) nimmt automatisch ALLE aktiven typ=rss-Zeilen - kein Workflow-Edit noetig. Getestete
  Fehlschlaege (NICHT eingetragen): transfermarkt.de/rss/news (202 Cloudflare), fussballtransfers.com (404), reviersport (403),
  footballtalentscout.net (404/leer), teamtalk (404), footmercato (404 alle Pfade), as fichajes/mercado.xml (404), fichajes.net (404),
  vavel (404), eldesmarque (403), relevo (404), uefa youthleague rss (timeout), estadiodeportivo (404).

### Scout-Agent (iVt2oygA1gPIMf0Y, aktive Version 885bc13d)
- Neuer Knoten 'Form laden' (Postgres n8n-DB PGn8nDB00000001, onError continue): f5 = gerundeter Durchschnitts-TW-Score der
  letzten bis zu 5 Pflichtspiele (45-Tage-Fenster, Vortest 4.611 Spieler) + m5 = Minuten darin, aus TW Performance
  (data_table_user_zqzCsKh0H0VlVlpX); dazu 'verletzt'-Liste aus TW Sidelined (fetched_at::text-Vergleich, items_json > leer).
  Kette: Kalibrierung laden -> Form laden -> Agent-Auftrag.
- 'Stats laden' liefert jetzt pid (player_id im Maennerfussball-Block, NULL bei Jugendliga); 'Agent-Auftrag' mappt f5/m5/verletzt
  per pid in die Leistungsdaten und entfernt pid vor dem Prompt (Tokens).
- Prompt: neuer Block PERFORMANCE-ANALYSE zwischen Scout-Attributen und Aufgabe - Wettbewerbsgewichtung (Top-5-Erstligen >
  grosse Zweitligen > 3. Liga > UEFA Youth League > Jugendligen), p90-Richtwerte je Positionsgruppe (Stuermer 0,5/0,8;
  Fluegel/Zehner 0,35; Achter 0,2; Verteidiger/TW nie ueber p90), Form-Lesart f5 vs r*10, Belastbarkeit 270/900 Minuten,
  Verletzt-Malus nach Chef-Kriterium 7, Widerspruchs-Regel Zahlen > Meldungstext. CHEF-KRITERIEN und Ausgabeschema UNVERAENDERT.
- Draft-Test 12830: Form laden success, Agent-Auftrag success, Abbruch erwartungsgemaess erst am KI-Knoten (OpenAI Spend-Limit
  bis 1.9.). Erster Echtlauf mit KI: 1.9. um 21:15.
- Offen fuer Boss: (a) er wollte 'folgende Quellen' schicken - Liste kam nicht an, bitte nachreichen, dann ergaenzen;
  (b) API-Key-Quellen als Extra-Schritt (football-data.org kostenloser Key, Sportmonks-Planerweiterung, kommerziell
  Wyscout/Opta/StatsBomb); (c) Fruehstarter-Scout 21:40 koennte dieselbe Formkurve bekommen (kleiner Folge-Edit).

### Nachtrag: Boss-Quellenliste eingearbeitet (28.08., ids 1147-1206)
- 60 weitere Register-Eintraege, hinweis 'Scouting-Vertiefung 28.08.2026 (Boss-Quellenliste)'. Gesamt jetzt 70 neue Quellen:
  DE 14, EN 15, FR 14, ES 22, INT 5. Davon 3 zusaetzliche live getestete RSS (kicker Junioren newsfeed.kicker.de/news/junioren,
  Training Ground Guru /feed/, Golsmedia /feed/), 1 social (YouthHawk auf X), Rest typ=web fuer den KI-Quellen-Crawler:
  UEFA Youth League + U17/U19/U21-Statistiken, CIES Reports, DFB U17/U19-Nachwuchsliga + U17/U19-Nationalteams + 3. Liga,
  FUSSBALL.DE, FuPa U17/U19, kicker U17-Wettbewerbe, RevierSport Junioren/B-Jugend, Sofascore-Jugendligen (DE/FR/ES),
  PL Youth/U18/PL2 (Spiele+Tabellen), FA Youth Cup, EFL Youth Development, England Football Youth, YouthHawk, TGG Academy
  Rankings, NFYL, EFL + National League, FFF Epreuves, FFFTV U17/U19/Gambardella/National, FFF U17/U19-Auswahlen,
  FFF-Ligenverzeichnis, Actufoot, Foot-National, RFEF DH Juvenil + Copa Juvenil + Sub-17/19/21 + Primera/Segunda/Tercera
  Federacion, Futbolme DH + Liga Nacional Juvenil, Golsmedia Juvenil/Cadete, AS DH-Juvenil-Tag, Relevo, Verbaende FCF/RFFM/FFCV/RFAF.
- Kostenlogik Crawler: Deckel 70 faellige Quellen je Lauf (4x taeglich); prio 1 ~alle 20h, prio 2 ~44h, prio 3 ~68h -> neue
  Quellen verlaengern nur den Umlauf, KEINE Mehrkosten je Tag. curl-403 bei 4 Hosts (epreuves.fff.fr, ffftv.fff.fr, rfef.es,
  actufoot.com) - eingetragen gelassen, Crawler-Fetcher hat eigene Methode; Quellen-Spiegel ueberwacht lese_status/vertrauen.
- NICHT eingebaut (kostenpflichtig, Extra-Schritt mit Boss): Wyscout Youth, Eyeball, SkillCorner. FFF-YouTube-Kanal als
  Video-Quelle notiert, kein Text-Crawling.

## 28.08.2026 (Nachmittag): Vollstaendigkeits-Pruefung + TM-Neuanlage fehlender Spieler (Boss-Frage 'haben wir alle?')

### Befund
- Antwort: NEIN. TM listete in den aktuellsten Liga-Audits 762 Spieler MIT Marktwert, die in players fehlten (mehrere Ligen am
  60er-Anzeige-Cap der fehlend-Liste -> real ~850+). Beispiele: Vini Souza + Vranckx (Wolfsburg), Neuzugangswellen Nuernberg/
  Lautern/Kiel/Hannover. Ursache: API-Football-Kader hinken hinterher oder listen Spieler gar nicht.
- Dazu 9 'Geister-Teams' mit 1-9 Spielern (Namensvarianten/Altbestaende, z.B. 'West Ham' neben 'West Ham United') und Team-
  Zahlen > Ligagroesse (Karteileichen mit altem team-Wert). Dubletten-Waechter 5:50 beobachtet; separates Aufraeumthema.
- 'Alle Laender': bewusst 20 Ligen abgedeckt, nicht alle Ligen weltweit (Erweiterungsoptionen siehe Bericht an Boss).

### Loesung: TM-Neuanlage im Import (xZDGcMSlCMFeofXw, aktive Version 4099cb5c)
- Parse-Knoten sammelt Neuanlage-Kandidaten: unmatched MIT tmPid und Marktwert >= 100k, Cap 80 je Lauf, samt aller geparsten
  Stammdaten (Pos/Alter/Nat/Groesse/Geb/Fuss/MW/Vertrag/Joined). Arrays nPids..nJoined + neuKandidaten im Output.
- Knoten 'Fehlende anlegen' (Postgres TransferWire): INSERT players mit player_id = 900000000 + TM-ID; Guards: tm_id existiert
  nicht, ID-Kollision nicht, kein gleicher Name (lower) in derselben Liga. team_source='TM-Kader', season 2026.
  WICHTIG: search_name/search_team sind GENERATED COLUMNS -> NIE setzen (erster Testfehler).
- Knoten 'Fehlende in Datentabelle' (Postgres n8n-DB): Dual-Write derselben Spieler in TW Spieler (id = MAX+rn, player_id double),
  damit der 4:30-Spiegel (TRUNCATE) sie behaelt. Quelle: neu_liste aus 'Fehlende anlegen' via json_to_recordset.
- Beide Knoten onError=continue + alwaysOutputData (Kette zum Audit reisst nie ab); Audit korrigiert-JSON um neu_angelegt ergaenzt.
- Test: China-Lauf 13288 -> 14 neu angelegt (Karzev, Saulo Mineiro, Jussa, Xadas ...), 14 in players UND Datentabelle verifiziert.
- Backfill-Fenster bis 17:54 UTC geoeffnet, Zeiger 0 -> alle 20 Ligen schliessen die Luecken noch heute; Rest + Zukunft via
  Nachtrotation (der Fueller laeuft jetzt in jedem Import-Lauf mit).
- Folgethema (beobachten, nicht dringend): Wenn API-Football einen TM-angelegten Spieler spaeter selbst listet, kann eine
  API-Dublette entstehen -> Dubletten-Waechter beobachten; bei Bedarf Merge-Regel ueber tm_id nachruesten.

## 28.08.2026 (Abend): Primaerquellen-Ebene + neuer Agent 'TW Marktanalyst' (Boss-Auftrag, Dokument 'besondere Transfer- und Primaerquellen')

### Quellen (Register, gruppe='primaer', hinweis 'Primaerquellen 28.08.2026', 25 neue Eintraege ids 1207-1231)
- Offizielle Web-Quellen (typ=web, laufen im KI-Quellen-Crawler UND im neuen Analyst): FIFA Legal/Football Regulatory, VDV
  Spielergewerkschaft, Bundesanzeiger, EFL Squad Lists + EFL Embargo Reporting, RFEF Circulares + Normativa, BORME, Lega Serie B,
  AIC News, LFP, Voetbal.nl, Liga Portugal, CMVM, RBFA, Bundesliga AT News, SFL, TFF, KAP (en), Scottish FA Governance, SPFL,
  DBU, Virk/CVR, MLSPA Salary Guide, MLS Roster Rules, CFA. Dublettenschutz liess 8 bereits vorhandene aus (Pro League u.a.).
- GN-Suchfeeds fuer saisonvariable Listen (typ=rss, laufen im 2h-RSS-Zweig): PL Retained/Released, DNCG, Bundesliga
  Transfercenter, KNVB Licentie, UNFP Joueurs Libres, MLS Transfer Tracker, Bundesliga AT Lizenz Senat 5.
- curl-Status beim Eintrag: 24x 200; 403 nur rfef.es (x2) und virk.dk (drin gelassen, Crawler-Fetcher + Quellen-Spiegel
  ueberwachen). Tote URLs (fifa registration-bans direkt, mlssoccer/transfers, knvb licentiezaken, unfp.org, bundesliga.com
  transfers) NICHT eingetragen - durch GN-Feeds bzw. Portal-Einstiege ersetzt.
- NICHT eingebaut (kostenpflichtig/Login, pausierter Extra-Schritt): TransferRoom (+API), Wyscout Data API, Opta, Sportradar,
  Event Registry, NewsWhip, Inoreader, Weibo/WeChat (brauchen eigene Anbindung/Accounts).

### Neue Tabelle markt_signale (transferwire-DB)
- kategorie (registrierung|free_agent|embargo|lizenz|finanzen|sperre|regel|kaderliste), land, club, player_name, richtung
  (kauft_nicht|muss_verkaufen|verfuegbar|fix|warnung|info), staerke 1-5, signal_text, quelle, url, published_at, gueltig_bis,
  dedupe_key UNIQUE, created_at. Zusatz-Ebene fuer Club-Signale (Embargo/Lizenz/Finanzen) - Anzeige im Vereinskontext = moeglicher
  Folgeschritt (Website-Freeze beachten).

### Neuer Workflow 'TW Agent: Primaerquellen-Analyst (taeglich 7:20)' (EWKWA7T0h2yqYKnR, aktiv 242be57a)
- Erstellt via Workflow-SDK (validate + create_workflow_from_code). Kette: Schedule 7:20 -> Bremse pruefen (tw_status ki_bremse)
  -> IF 'KI frei?' -> Quellen laden (gruppe=primaer, typ=web, LIMIT 26) -> Seite holen (httpRequest text, 15s, onError continue)
  -> Agent-Auftrag (HTML-Strip, 3200 Z./Quelle, 90k-Cap, gpt-5-mini json_object) -> Marktanalyst KI (openAiApi Yp2IJGZKyLBBjk7Z)
  -> Signale formen (Schema-Haertung, dedupe_key) -> Signale speichern (markt_signale, ON CONFLICT DO NOTHING)
  -> Meldungen ableiten (registrierung->type fix, free_agent->type verfuegbar, reliability 5, dedup_key 'primaer:'||key,
  source=Quellenname) in Transfernews Meldungen -> fliesst automatisch in Feed, Spieler-Aktualisierer (30min) und
  Kader-Abgleich-Meldungsevidenz. Der antrainierte Analyst-Prompt enthaelt Kategorien + Bedeutungslehre (DNCG/Embargo/KAP/
  Released-Lists) + strikte Nur-was-dasteht-Regeln.
- Draft-Test 13425: 12/26 Seiten mit Text (LFP-Kommissionsentscheidungen 28.08., AIC, Lega-B-Comunicati, SFL-Ticker, KAP,
  BORME ...), Auftrag korrekt gebaut, Credential greift, Abbruch erwartungsgemaess am OpenAI-Spend-Limit (429, bis 1.9.).
  Erster Echtlauf: 1.9. um 7:20. Bis dahin liefern die Fehl-Laeufe den bekannten 429 (wie alle KI-Workflows, Waechter aktiv).

## 2026-08-28 (Abend): KI-Header-Suche live, Scout-Chat repariert, FAB entfernt (Marker bo)
- Auftrag Boss: schwarzes TW-KI-Scout-FAB-Icon weg (Handy+PC), Scout im Transfers-Fenster behalten und reparieren,
  Header-Suchleiste als KI-Chat-Suche mit Google-artigem Treffer-Panel, Mobile-Suchleiste vergroessern.
- Diagnose Scout-Chat: Workflow sgfKNfoJTTGGwEuX war nie kaputt. Execution 13463 (iPhone, 18:29) zeigte: Konto,
  Limit und Datenabruf ok, beide KI-Knoten scheitern am OpenAI-Spend-Limit (429, gesperrt bis 1.9.). Frontend
  zeigte deshalb generischen Fehler.
- Fix Chat (publiziert 76244594): "Antwort bauen" liefert bei leerem KI-Text jetzt ok:true mit Wartungstext DE/EN
  (ab 1. September wieder voll da) statt err:ki. "Zaehler schreiben" als Inline-Expression neu gebaut (funktional
  identisch, RETURNING-Werte fliessen weiter in left-Anzeige). Live-curl: Wartungstext + left 29 ok.
- NEU Workflow "TransferWire - KI-Suche Header (Webhook)" mJ9VGLRi987YfAYm (aktiv bb5acdc1), Pfad /webhook/tw-suche
  (Frontend /api/tw-suche via Netlify-Redirect). 10 Knoten: Webhook POST -> Anfrage parsen (email/code/frage max 300,
  lang, verlauf max 4) -> Konto lesen (n8n-DB) -> Pruefen & Begriffe (Auth aktiv|test + gueltig_bis; Wortextraktion,
  Stopwoerter DE/EN, max 5, Umlaut-Normalisierung, SQL-ARRAY-Literale) -> Treffer laden (TW-DB: players ILIKE ANY
  LIMIT 6 + markt_signale LIMIT 5) -> Meldungen laden (n8n-DB LIMIT 6) -> KI-Auftrag (gpt-5-mini, max 450 Tokens,
  nur DATEN als Quelle, max 110 Woerter, reliability 5 = Fakt) -> Suche KI (onError continue) -> Antwort bauen
  (KI-Ausfall -> ok:true ki:false + Wartungstext, Treffer stehen trotzdem drunter) -> Respond. Antwort:
  {ok, ki, antwort, treffer:{spieler, meldungen, signale}}. Live-curl: "Murat Satin" -> 2 Meldungs-Treffer
  (WSG-Tirol-Fix rel. 5 + Murata-Geruecht), Auth-falsch -> err:auth. Kosten: gpt-5-mini, Cent-Bereich.
- Frontend Commit 62d7adb (Marker 2026-08-28-bo, Patchskript patch_kisuche.py, Delta +5006):
  1) FAB-CSS + kompletter FAB-JSX-Block (Sprechblase "Frag den TW Scout" + Maennchen) entfernt, 0 Rest-Vorkommen.
     Chat-Overlay (chatOpen) unveraendert erhalten.
  2) Neue Komponente ScoutLeiste (dunkle Karte, gruener Punkt, Button "Scout fragen" -> Chat) im Feed-View vor der
     eingefrorenen FeedSuche (React.Fragment-Wrap, Freeze-Bereich unangetastet).
  3) Header-Suche (#tw-gsuche) schreibt jetzt kiFrage, Enter -> sendeKi, onFocus mobil oeffnet Panel; neuer
     Placeholder "Frag die TW KI-Suche...". Feed-Filterung der Suchbox entfaellt (query-State bleibt ungenutzt).
  4) Neue Komponente KiSuchePanel: Desktop fixed top 62, min(720px, 100vw-24), Chat-Bubbles, Treffer-Sektionen
     SPIELER / MELDUNGEN (Fix gruen, Geruecht amber, Verlaesslichkeit x/5, Quelle-Link) / MARKTSIGNALE, sticky
     Eingabe. Mobile: Vollbild (inset 0, 100dvh), Input 16px (kein iOS-Zoom), Suchbox-Padding vergroessert.
- Livetest rt70 (docs/tests/rt70.py, Premium-Testkonto, Desktop 1280x900 + Mobile 390x844) KOMPLETT GRUEN:
  marker=bo, fab=0, bubble weg, ScoutLeiste da, Chat oeffnet + Wartungsantwort, Mobile-Suchfont 16px,
  KI-Panel oeffnet (720 Desktop / 390 Vollbild Mobile), Wartungsantwort + Satin-Treffer + WSG-Tirol-Fix sichtbar.
- Ab 1.9. antworten Chat und KI-Suche automatisch mit echten KI-Antworten (gleiche Workflows, kein Eingriff noetig).

## 2026-08-28 (spaet): Mobile-Suchfeld als eigene Zeile unter der Kopfzeile (Marker br)
- Auftrag Boss: Auf dem Handy soll das Suchfeld UNTER den Header, genauso lang wie der Header sein und den
  gleichen Placeholder-Text wie im Web zeigen.
- Umsetzung (nur CSS im 760er-Mobile-Block, kein JSX-Eingriff): .tw-headwrap height auto + flex-wrap wrap
  (Padding 9/10/11, row-gap 9); .tw-gsuche-box order 99 + flex 1 1 100% -> rutscht als volle zweite Zeile
  unter Logo/Buttons, exakt Header-Innenbreite. Header ist nicht fixed, nichts haengt an der 56px-Hoehe
  (KI-Panel mobil inset 0) - vorher geprueft.
- Bugfix dabei entdeckt: Das Input fuellte die Box nicht (nur 92px, width-100%-Basis griff im Flex-Kontext
  nicht) -> Input jetzt flex 1 1 0% + width auto + min-width 0, fuellt den Restplatz (320px auf 390er).
- Placeholder: identischer Wortlaut wie Web (ein gemeinsamer String im Code). Da 16px-Text (408px) physisch
  nicht in 390px passt: ::placeholder mobil 12px + letter-spacing -0.1 + text-overflow ellipsis als Netz;
  Stufe 11.5px unter 375px (verschachteltes @media, UND-verknuepft). Input-Schrift bleibt 16px (kein iOS-Zoom).
- Livetest rt71 (docs/tests/rt71.py, misst Geometrie + Placeholder-Textbreite in echter ::placeholder-Schrift,
  Login-Objekt wie rt70 inkl. plan/start/name - ohne diese Felder greift der localStorage-Login nicht!):
  DESKTOP 1280: Suchfeld bleibt IN der Kopfzeile, 560px, unveraendert, Panel 720. GRUEN.
  MOBILE 390: unter dem Header, Breite 364/364 (rechtsLuecke 0), voller Text passt (299/320), Panel 390. GRUEN.
  MOBIL36 360: Breite 334/334, voller Text passt (286/290), Panel 360. GRUEN.
- Commits 548d455 (bp), 4796ee7 (bq), a64fe39 (br).
