import { workflow, node, trigger, expr } from '@n8n/workflow-sdk';

const start = trigger({ type: 'n8n-nodes-base.scheduleTrigger', version: 1.3, config: { name: 'Taeglich 5:00', parameters: { rule: { interval: [{ field: 'days', daysInterval: 1, triggerAtHour: 5, triggerAtMinute: 0 }] } } } });

const ligen = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Ligen', parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: `const now = new Date(); const y = now.getFullYear(); const m = now.getMonth() + 1; const eu = m >= 7 ? y : y - 1;
const L = [['Bundesliga',78],['2. Bundesliga',79],['3. Liga',80],['Premier League',39],['Championship',40],['LaLiga',140],['LaLiga 2',141],['Serie A',135],['Serie B',136],['Ligue 1',61],['Ligue 2',62],['Eredivisie',88],['Jupiler Pro League',144],['Liga Portugal',94],['Süper Lig',203],['Superligaen',119],['Bundesliga (Österreich)',218],['Super League (Schweiz)',207],['MLS',253],['Chinese Super League',169]];
return L.map(([league, id]) => ({ json: { league, id, season: (id === 253 || id === 169) ? y : eu } }));` } } });

const teamsHolen = node({ type: 'n8n-nodes-base.httpRequest', version: 4.3, config: { name: 'Teams holen', onError: 'continueRegularOutput', parameters: { method: 'GET', url: expr('=https://v3.football.api-sports.io/teams?league={{ $json.id }}&season={{ $json.season }}'), authentication: 'genericCredentialType', genericAuthType: 'httpHeaderAuth', options: { batching: { batch: { batchInterval: 400, batchSize: 1 } }, timeout: 30000 } }, credentials: { httpHeaderAuth: { id: 'llXJtXkpKcY9Tn6z', name: 'API-Football Key' } } } });

const teamsListen = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Teams listen', parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: `const ligen = $('Ligen').all().map(i => i.json); const out = [];
$input.all().forEach((it, i) => { const liga = ligen[i] || {}; const arr = Array.isArray(it.json && it.json.response) ? it.json.response : []; for (const t of arr) { if (t && t.team && t.team.id) out.push({ json: { teamId: t.team.id, teamName: t.team.name, league: liga.league || '' } }); } });
return out;` } } });

const kaderHolen = node({ type: 'n8n-nodes-base.httpRequest', version: 4.3, config: { name: 'Kader holen', onError: 'continueRegularOutput', parameters: { method: 'GET', url: expr('=https://v3.football.api-sports.io/players/squads?team={{ $json.teamId }}'), authentication: 'genericCredentialType', genericAuthType: 'httpHeaderAuth', options: { batching: { batch: { batchInterval: 350, batchSize: 1 } }, timeout: 30000 } }, credentials: { httpHeaderAuth: { id: 'llXJtXkpKcY9Tn6z', name: 'API-Football Key' } } } });

const kaderKarte = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Kader-Karte', parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: `const teams = $('Teams listen').all().map(i => i.json); const kader = {}; let ok = 0;
$input.all().forEach((it, i) => { const t = teams[i] || {}; const r = it.json && Array.isArray(it.json.response) && it.json.response[0]; if (!r || !Array.isArray(r.players)) return; ok++; const teamName = (r.team && r.team.name) || t.teamName || ''; for (const p of r.players) { if (p && p.id) kader[p.id] = { team: teamName, league: t.league || '', name: p.name || '' }; } });
return [{ json: { kader, teams: teams.length, ok, spieler: Object.keys(kader).length } }];` } } });

const spieleHolen = node({ type: 'n8n-nodes-base.httpRequest', version: 4.3, config: { name: 'Spiele holen', executeOnce: true, onError: 'continueRegularOutput', parameters: { method: 'GET', url: 'https://transferwire.de/api/tw-performance', options: { timeout: 60000 } } } });

const spielerLaden = node({ type: 'n8n-nodes-base.postgres', version: 2.7, config: { name: 'Spieler laden', executeOnce: true, parameters: { operation: 'executeQuery', query: 'SELECT player_id, name, team, league FROM players', options: {} }, credentials: { postgres: { id: '5GYdciGwZ3GXZH0t', name: 'Postgres TransferWire' } } } });

const vergleich = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Vergleich', parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: `const kader = ($('Kader-Karte').first().json || {}).kader || {};
const perfRaw = $('Spiele holen').first().json; const perf = perfRaw && Array.isArray(perfRaw.items) ? perfRaw.items : [];
const spiel = {}; const grenze = Date.now() - 30 * 86400000;
for (const x of perf) { const t = Date.parse(x.date || ''); if (!x.pid || !x.team || isNaN(t) || t < grenze) continue; if (!spiel[x.pid] || t > spiel[x.pid].t) spiel[x.pid] = { team: x.team, league: x.league || '', t }; }
const norm = s => String(s || '').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
const out = [];
for (const it of $input.all()) { const p = it.json || {}; const pid = Number(p.player_id); if (!pid) continue; let neu = null, liga = null, quelle = '';
  const s = spiel[pid]; const k = kader[pid];
  if (s && norm(s.team) !== norm(p.team)) { neu = s.team; liga = s.league || (k && k.league) || p.league; quelle = 'Spiel'; }
  else if (!s && k && norm(k.team) !== norm(p.team)) { neu = k.team; liga = k.league || p.league; quelle = 'Kader'; }
  if (neu) out.push({ json: { player_id: pid, name: p.name, alt: p.team, neu, liga_neu: liga || p.league || '', quelle } });
}
return out;` } } });

const batchBauen = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Batch bauen', parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: `const a = $input.all().map(i => i.json); return [{ json: { pids: a.map(x => x.player_id), teams: a.map(x => x.neu), ligen: a.map(x => x.liga_neu), quellen: a.map(x => x.quelle), n: a.length, liste: JSON.stringify(a.slice(0, 300)), text: a.slice(0, 60).map(x => x.name + ': ' + x.alt + ' -> ' + x.neu + ' (' + x.quelle + ')').join('\\n') } }];` } } });

const playersUpdate = node({ type: 'n8n-nodes-base.postgres', version: 2.7, config: { name: 'Spieler aktualisieren', parameters: { operation: 'executeQuery', query: 'UPDATE players p SET team = v.team, league = v.league, team_source = v.quelle, team_updated_at = now() FROM (SELECT unnest($1::bigint[]) pid, unnest($2::text[]) team, unnest($3::text[]) league, unnest($4::text[]) quelle) v WHERE p.player_id = v.pid', options: { queryReplacement: expr('={{ [$json.pids, $json.teams, $json.ligen, $json.quellen] }}') } }, credentials: { postgres: { id: '5GYdciGwZ3GXZH0t', name: 'Postgres TransferWire' } } } });

const audit = node({ type: 'n8n-nodes-base.postgres', version: 2.7, config: { name: 'Audit protokollieren', parameters: { operation: 'executeQuery', query: "INSERT INTO kader_audit (liga, team, fehlend, korrigiert, quellen, status) VALUES ('alle', 'KADER-ABGLEICH', $1::jsonb, $2::jsonb, 'Spiele + API-Football-Kader', 'kader-abgleich')", options: { queryReplacement: expr("={{ [$('Batch bauen').first().json.liste, JSON.stringify({ geaendert: $('Batch bauen').first().json.n })] }}") } }, credentials: { postgres: { id: '5GYdciGwZ3GXZH0t', name: 'Postgres TransferWire' } } } });

const report = node({ type: 'n8n-nodes-base.emailSend', version: 2.1, config: { name: 'Morgenreport', onError: 'continueRegularOutput', parameters: { fromEmail: 'info@transferwire.de', toEmail: 'laurenzrath@gmx.de', subject: expr("=TransferWire Kader-Abgleich: {{ $('Batch bauen').first().json.n }} Vereinswechsel korrigiert"), emailFormat: 'text', text: expr("=Guten Morgen,\n\nder Kader-Abgleich hat {{ $('Batch bauen').first().json.n }} Spieler auf den aktuellen Verein gesetzt (Quelle: letztes Spiel oder API-Kader).\n\n{{ $('Batch bauen').first().json.text }}\n\nDie Spieler-Datenbank und alle Seiten zeigen ab jetzt den neuen Verein.\n\nTransferWire"), options: {} }, credentials: { smtp: { id: 'G1GH4Mzvf2nFI8kT', name: 'SMTP info@transferwire.de' } } } });

const dtUpdate = node({ type: 'n8n-nodes-base.dataTable', version: 1.1, config: { name: 'Datentabelle aktualisieren', onError: 'continueRegularOutput', parameters: { resource: 'row', operation: 'update', dataTableId: { __rl: true, mode: 'id', value: '2LFW41SbOUtQ9lzR', cachedResultName: 'TW Spieler' }, matchType: 'allConditions', filters: { conditions: [{ keyName: 'player_id', condition: 'eq', keyValue: expr('={{ $json.player_id }}') }] }, columns: { mappingMode: 'defineBelow', value: { team: expr('={{ $json.neu }}'), league: expr('={{ $json.liga_neu }}') }, matchingColumns: [], schema: [] }, options: {} } } });

export default workflow('tw-kader-abgleich', 'TW Kader-Abgleich (täglich 5:00)')
  .add(start)
  .to(ligen)
  .to(teamsHolen)
  .to(teamsListen)
  .to(kaderHolen)
  .to(kaderKarte)
  .to(spieleHolen)
  .to(spielerLaden)
  .to(vergleich)
  .to(batchBauen)
  .to(playersUpdate)
  .to(audit)
  .to(report)
  .add(vergleich)
  .to(dtUpdate);
