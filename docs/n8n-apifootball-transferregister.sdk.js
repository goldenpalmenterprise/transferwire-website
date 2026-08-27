import { workflow, node, trigger, expr } from '@n8n/workflow-sdk';

const start = trigger({ type: 'n8n-nodes-base.scheduleTrigger', version: 1.3, config: { name: 'Taeglich 6:40', parameters: { rule: { interval: [{ field: 'days', daysInterval: 1, triggerAtHour: 6, triggerAtMinute: 40 }] } } } });

const ligen = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Ligen', parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: `const now = new Date(); const y = now.getFullYear(); const m = now.getMonth() + 1; const eu = m >= 7 ? y : y - 1;
const L = [['Bundesliga',78],['2. Bundesliga',79],['3. Liga',80],['Premier League',39],['Championship',40],['LaLiga',140],['LaLiga 2',141],['Serie A',135],['Serie B',136],['Ligue 1',61],['Ligue 2',62],['Eredivisie',88],['Jupiler Pro League',144],['Liga Portugal',94],['Süper Lig',203],['Superligaen',119],['Bundesliga (Österreich)',218],['Super League (Schweiz)',207],['MLS',253],['Chinese Super League',169]];
return L.map(([league, id]) => ({ json: { league, id, season: (id === 253 || id === 169) ? y : eu } }));` } } });

const teamsHolen = node({ type: 'n8n-nodes-base.httpRequest', version: 4.3, config: { name: 'Teams holen', onError: 'continueRegularOutput', parameters: { method: 'GET', url: expr('=https://v3.football.api-sports.io/teams?league={{ $json.id }}&season={{ $json.season }}'), authentication: 'genericCredentialType', genericAuthType: 'httpHeaderAuth', options: { batching: { batch: { batchInterval: 400, batchSize: 1 } }, timeout: 30000 } }, credentials: { httpHeaderAuth: { id: 'llXJtXkpKcY9Tn6z', name: 'API-Football Key' } } } });

const teamsListen = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Teams listen', parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: `const ligen = $('Ligen').all().map(i => i.json); const out = [];
$input.all().forEach((it, i) => { const liga = ligen[i] || {}; const arr = Array.isArray(it.json && it.json.response) ? it.json.response : []; for (const t of arr) { if (t && t.team && t.team.id) out.push({ json: { teamId: t.team.id, teamName: t.team.name, league: liga.league || '' } }); } });
return out;` } } });

const transfersHolen = node({ type: 'n8n-nodes-base.httpRequest', version: 4.3, config: { name: 'Transfers holen', onError: 'continueRegularOutput', parameters: { method: 'GET', url: expr('=https://v3.football.api-sports.io/transfers?team={{ $json.teamId }}'), authentication: 'genericCredentialType', genericAuthType: 'httpHeaderAuth', options: { batching: { batch: { batchInterval: 350, batchSize: 1 } }, timeout: 30000 } }, credentials: { httpHeaderAuth: { id: 'llXJtXkpKcY9Tn6z', name: 'API-Football Key' } } } });

const bauen = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Meldungen bauen', parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: `const teams = $('Teams listen').all().map(i => i.json); const ligaVon = {}; for (const t of teams) ligaVon[t.teamId] = t.league;
const grenze = new Date(Date.now() - 4 * 86400000).toISOString().slice(0, 10); const heute = new Date().toISOString().slice(0, 10);
const seen = new Set(); const out = [];
const modal = t => { const s = String(t || '').trim(); if (!s || s === 'N/A') return ''; if (/loan/i.test(s)) return 'Leihe'; if (/free/i.test(s)) return 'abl\\u00f6sefrei'; if (/back from loan/i.test(s)) return 'R\\u00fcckkehr aus Leihe'; return s; };
$input.all().forEach((it, i) => { const t = teams[i] || {}; const arr = Array.isArray(it.json && it.json.response) ? it.json.response : [];
  for (const p of arr) { const spieler = p.player || {}; for (const tr of (p.transfers || [])) { const d = String(tr.date || ''); if (!d || d < grenze || d > heute) continue; const inT = (tr.teams && tr.teams.in) || {}; const outT = (tr.teams && tr.teams.out) || {}; if (!inT.name || !outT.name || !spieler.name) continue; const key = spieler.id + '|' + inT.id + '|' + d; if (seen.has(key)) continue; seen.add(key);
    const mod = modal(tr.type); const typ = /leihe/i.test(mod) && !/r\\u00fcckkehr/i.test(mod) ? 'leihe' : 'fix';
    out.push({ json: { player_id: spieler.id, player_name: spieler.name, from_club: outT.name, to_club: inT.name, datum: d, modalitaet: mod, typ, league: ligaVon[inT.id] || ligaVon[outT.id] || t.league || '' } }); } } });
return out;` } } });

const anreichern = node({ type: 'n8n-nodes-base.postgres', version: 2.7, config: { name: 'Spieler anreichern', onError: 'continueRegularOutput', alwaysOutputData: true, parameters: { operation: 'executeQuery', query: 'SELECT player_id, position, age, nationality FROM players WHERE player_id = ANY($1::bigint[])', options: { queryReplacement: expr("={{ [ $input.all().map(i => i.json.player_id) ] }}") } }, credentials: { postgres: { id: '5GYdciGwZ3GXZH0t', name: 'Postgres TransferWire' } } } });

const zusammen = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Zusammenfuehren', parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: `const info = {}; for (const it of $input.all()) { const j = it.json || {}; if (j.player_id) info[j.player_id] = j; }
const pos = p => ({ Goalkeeper: 'Torwart', Defender: 'Abwehr', Midfielder: 'Mittelfeld', Attacker: 'Sturm' })[p] || (p || '');
const fmt = d => { const [y, m, t] = String(d).split('-'); return t + '.' + m + '.' + y; };
return $('Meldungen bauen').all().map(i => { const m = i.json; const x = info[m.player_id] || {}; const modText = m.modalitaet ? ' (' + m.modalitaet + ')' : '';
  const headline = m.typ === 'leihe' ? m.player_name + ' per Leihe von ' + m.from_club + ' zu ' + m.to_club : m.player_name + ' wechselt von ' + m.from_club + ' zu ' + m.to_club;
  const summary = 'Offiziell registrierter Wechsel laut Datenanbieter (API-Football), Transferdatum ' + fmt(m.datum) + modText + '.' + (x.position ? ' Position: ' + pos(x.position) + '.' : '') + (x.age ? ' Alter: ' + x.age + '.' : '');
  return { json: Object.assign({}, m, { headline, summary, player_position: pos(x.position), player_age: Number(x.age) || 0, player_nationality: x.nationality || '', fee: m.modalitaet && !/leihe|frei|r\\u00fcckkehr/i.test(m.modalitaet) ? m.modalitaet : '' }) }; });` } } });

const mappen = node({ type: 'n8n-nodes-base.set', version: 3.4, config: { name: 'Auf Tabellenschema mappen', parameters: { mode: 'manual', includeOtherFields: false, assignments: { assignments: [
  { id: 'a1', name: 'news_id', value: expr("={{ 'af-' + $json.player_id + '-' + $json.datum }}"), type: 'string' },
  { id: 'a2', name: 'dedup_key', value: expr("={{ (($json.player_name || '') + '|' + ($json.from_club || '') + '|' + ($json.to_club || '') + '|' + ($json.typ || 'fix')).toLowerCase() }}"), type: 'string' },
  { id: 'a3', name: 'sport', value: 'fussball', type: 'string' },
  { id: 'a4', name: 'league', value: expr('={{ $json.league || "" }}'), type: 'string' },
  { id: 'a5', name: 'type', value: expr('={{ $json.typ || "fix" }}'), type: 'string' },
  { id: 'a6', name: 'headline', value: expr('={{ $json.headline }}'), type: 'string' },
  { id: 'a7', name: 'summary', value: expr('={{ $json.summary }}'), type: 'string' },
  { id: 'a8', name: 'player_name', value: expr('={{ $json.player_name }}'), type: 'string' },
  { id: 'a9', name: 'player_position', value: expr('={{ $json.player_position || "" }}'), type: 'string' },
  { id: 'a10', name: 'player_age', value: expr('={{ $json.player_age || 0 }}'), type: 'number' },
  { id: 'a11', name: 'player_nationality', value: expr('={{ $json.player_nationality || "" }}'), type: 'string' },
  { id: 'a12', name: 'from_club', value: expr('={{ $json.from_club }}'), type: 'string' },
  { id: 'a13', name: 'to_club', value: expr('={{ $json.to_club }}'), type: 'string' },
  { id: 'a14', name: 'fee', value: expr('={{ $json.fee || "" }}'), type: 'string' },
  { id: 'a15', name: 'reliability', value: 5, type: 'number' },
  { id: 'a16', name: 'position_needed', value: '', type: 'string' },
  { id: 'a17', name: 'source_name', value: 'API-Football (Transferregister)', type: 'string' },
  { id: 'a18', name: 'source_url', value: 'https://www.api-football.com/', type: 'string' },
  { id: 'a19', name: 'sources_json', value: expr("={{ JSON.stringify([{ name: 'API-Football (Transferregister)', url: 'https://www.api-football.com/' }]) }}"), type: 'string' },
  { id: 'a20', name: 'published_at', value: expr("={{ $json.datum + 'T09:00:00.000Z' }}"), type: 'string' },
  { id: 'a21', name: 'created_at', value: expr('={{ $now.toISO() }}'), type: 'string' }
] } } } });

const upsert = node({ type: 'n8n-nodes-base.dataTable', version: 1.1, config: { name: 'Transfernews (Upsert)', onError: 'continueRegularOutput', parameters: { resource: 'row', operation: 'upsert', dataTableId: { __rl: true, mode: 'id', value: 'vxAKGr0ljM6q21KY', cachedResultName: 'Transfernews' }, matchType: 'allConditions', filters: { conditions: [{ keyName: 'dedup_key', condition: 'eq', keyValue: expr('={{ $json.dedup_key }}') }] }, columns: { mappingMode: 'autoMapInputData', matchingColumns: ['dedup_key'], value: null, schema: [] }, options: {} } } });

export default workflow('tw-apifootball-transfers', 'TW Quelle: API-Football Transferregister (täglich 6:40)')
  .add(start).to(ligen).to(teamsHolen).to(teamsListen).to(transfersHolen).to(bauen).to(anreichern).to(zusammen).to(mappen).to(upsert);
