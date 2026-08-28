# TransferWire – Übergabe an einen neuen Chat

Diese Datei ist der Einstiegspunkt. Wer sie liest, hat alles, um sofort weiterzuarbeiten.
Ausführlich: `docs/START-HIER.md` (Umgebung) und `docs/FORTSCHRITT.md` (jeder Arbeitsschritt).

## Zugänge

**n8n (Agenten, Server, Datenbanken, Tests):** über die MCP-Verbindung `n8n-server`
(auto.transferwire.de). Zentraler Helfer: Workflow **„TW Admin: Server-Shell (manuell)"**,
ID `umhYeTVuKBNB2Z3u` – Befehl im Knoten „Befehl ausfuehren" setzen, Workflow ausführen,
Ergebnis mit `get_execution` lesen.

**GitHub-Token:** liegt auf dem Server unter `/opt/transferwire/deploy_token` (chmod 600).
Über die Server-Shell holen und damit klonen:

    TOKEN=$(cat /opt/transferwire/deploy_token)
    git clone https://$TOKEN@github.com/goldenpalmenterprise/transferwire-website.git /home/claude/site

Beim Ausgeben von Befehlen den Token maskieren: `| sed 's/github_pat[^@]*@/***@/'`.
Gültig bis 14.11.2026. **Niemals in ein Repo committen** – GitHub sperrt ihn dann automatisch.

**Netlify:** hängt an diesem Repo. **Jeder Push geht sofort live** auf transferwire.de
(Deploy ca. 80 s). Nie ungeprüft pushen.

**Datenbanken** (über die Server-Shell, `docker exec -i transferwire-postgres-1 psql -U n8n -d <db>`):
- `transferwire`: players, injuries, tw_status, spieler_aenderungen, quellen_vertrauen, gdelt_seen …
- `n8n`: Datentabellen – Transfernews `data_table_user_vxAKGr0ljM6q21KY`,
  Quellen `data_table_user_IQk1uY59LjYaOsyi`, TW Spieler `data_table_user_2LFW41SbOUtQ9lzR`

**Website:** eine Datei `index.html` im Repo. Test-Zugang: laurenzrath@gmx.de / TWT-2JCT3.
**Browser-Tests:** Playwright im Container `tm-fetcher`, Skript base64 über die Server-Shell
einspielen (Beispiele in `docs/tests/`).

## Arbeitsweise (bitte einhalten)

1. Änderung an `index.html`, Syntax prüfen (`node --check` je Script-Block).
2. Commit + Push → 80 s warten → live testen (Playwright).
3. Ergebnis in `docs/FORTSCHRITT.md` dokumentieren, Build-Marker in `index.html` hochzählen.
4. Keine ungetesteten Änderungen. Antworten auf Deutsch, Anrede „Boss" (Laurenz Rath).

## Rahmenbedingungen

- **Kostenrahmen 5–6 €/Tag.** KI-Bremse über `tw_status.ki_bremse` und `kosten_24h_eur` stoppt
  die sechs teuersten Workflows automatisch. Nicht aufweichen.
- **OpenAI war bis 1.9.2026 gesperrt** (Monatslimit 500 $ erreicht). Alle KI-Schritte pausierten;
  am 1.9. prüfen, ob wieder frei, dann Performance-Analyst und Quellen-Voll-Leser einmal manuell
  nachstarten und die echten Tageskosten melden.
- **Eingefrorene Bereiche** (nur nach ausdrücklicher Ansage ändern): Such-/Filterleisten von
  Transfers & Gerüchte, Vereinsbedarf, Performance, Spieler-Datenbank, Vertragsradar-Kategorien,
  Merkliste-Chips, Talent-Chips, Scouting-Formular. Details in `docs/FORTSCHRITT.md`.

## Stand 27./28.08.2026

Website mit Newsfeed, Transfers & Gerüchte, Vereinsbedarf, Performance, Spieler-Datenbank,
Vertragsenden (Filterleiste + Probetraining-Radar), Merkliste, Scouting-Listen, Talent-Rankings,
Community – Transferhinweise; Handy-Layout mit Burger-Menü.
1.112 Quellen (544 RSS, davon 364 Vereinsfeeds), Vertrauensstufen A1–D, Bestätigungsregel für „fix".
Aktive Agenten u. a.: RSS-Zweig (2 h), Quellen-Crawler mit KI-Leser (4×/Tag), GDELT-Lokalmedien (2 h),
API-Football-Transferregister (6:40), Kader-Abgleich (5:00), Spieler-Aktualisierer (alle 30 Min),
Transfermarkt-Import (2:40 + 3:10), Verletzungs-Syncs, Kosten-Wächter, OpenAI-Limit-Wächter,
Vereins-Abdeckung (Mo 8:30), Quellen-Trefferquote (Mo 8:45).
Marktwerte: 8.074 von 15.338 Spielern (52,6 %).

## Offene Punkte

1. Marktwert-Abgleich verbessern (47 % ohne Treffer: Transliteration, Kurznamen, Nachwuchs) –
   Abgleich über Verein + Geburtsdatum oder TM-ID, geschätzt +20–30 Prozentpunkte.
2. Kontakte-Modul (internes Netzwerk: Sportdirektoren, Berater, Reporter, mit Trefferquote).
3. TransferRoom – Geschäftsentscheidung des Boss, keine Technikfrage.
4. To-dos des Boss: n8n-Cloud kündigen, GitHub-Token rotieren, Stripe-Test.
