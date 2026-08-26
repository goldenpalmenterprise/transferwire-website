# TransferWire – Einstieg für einen neuen Chat

1. `docs/FORTSCHRITT.md` lesen (chronologische Doku aller Arbeiten, Lektionen, offene Punkte).
2. Infrastruktur: Website = dieses Repo (`index.html`, eine Datei) → Netlify (ca. 80 s Deploy). Automationen = n8n unter
   https://auto.transferwire.de (MCP-Anbindung), Projekt KQeIN6MdqzXhCr3o. Datenbank = Postgres im Docker auf dem Hetzner-Server
   (Zugang nur intern; Admin-Shell-Workflow "TW Admin: Server-Shell (manuell)" umhYeTVuKBNB2Z3u führt Befehle als root aus).
3. Regeln, die uns Tage gekostet hätten:
   - Modelle/Code in n8n NIE per SQL setzen. Immer update_workflow (echte Node-Änderung nötig, sonst keine neue Version) + publish_workflow,
     danach in workflow_history (activeVersionId) gegenprüfen.
   - Vor jedem Push `git pull`. Vor Workflow-Änderungen aktive Version prüfen.
   - Kostenziel ≤ 6 €/Tag (Kosten-Wächter mailt täglich 23:50). Web-Suche-Workflows sind die Kostentreiber.
   - Englisch: Wörterbuch `docs/en_map.json` → als JSON-Block `const EN_MAP` in index.html; neue deutsche UI-Texte dort eintragen.
4. Tests: `docs/tests/` (Playwright-Skripte laufen im Container `tm-fetcher` auf dem Server, Aufruf über die Admin-Shell).
5. Offene Punkte stehen am Ende von `docs/FORTSCHRITT.md` (pausiert lt. Boss 26.08.: 1.4 Filterleiste, Vereinslogos, Boss-To-dos, Match-/Opportunity-Score, Vertragsfeld, Geruechte-Nachformulierung; Seiten Transfers, Vereinsbedarf, Performance nach Boss-Briefs umgebaut - deren Filter/Kriterien sind eingefroren).
