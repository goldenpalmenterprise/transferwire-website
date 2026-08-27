import { workflow, node, trigger, expr, ifElse } from '@n8n/workflow-sdk';

const start = trigger({ type: 'n8n-nodes-base.scheduleTrigger', version: 1.3, config: { name: 'Alle 2 Stunden :35', parameters: { rule: { interval: [{ field: 'cronExpression', expression: '35 */2 * * *' }] } } } });

const gate = node({ type: 'n8n-nodes-base.postgres', version: 2.7, config: { name: 'Budget-Gate', executeOnce: true, onError: 'continueRegularOutput', alwaysOutputData: true, parameters: { operation: 'executeQuery', query: "SELECT (SELECT value FROM tw_status WHERE key = 'ki_bremse') AS bremse, (SELECT value FROM tw_status WHERE key = 'kosten_24h_eur') AS eur", options: {} }, credentials: { postgres: { id: '5GYdciGwZ3GXZH0t', name: 'Postgres TransferWire' } } } });

const frei = ifElse({ version: 2.2, config: { name: 'KI frei?', parameters: { conditions: { options: { caseSensitive: true, leftValue: '', typeValidation: 'loose' }, conditions: [{ leftValue: expr("={{ String($json.bremse) !== 'true' && Number($json.eur || 0) <= 6 }}"), operator: { type: 'boolean', operation: 'true' }, rightValue: '' }], combinator: 'and' } } } });

const vereine = node({ type: 'n8n-nodes-base.postgres', version: 2.7, config: { name: 'Vereine laden', executeOnce: true, parameters: { operation: 'executeQuery', query: 'SELECT team, league FROM players WHERE team IS NOT NULL AND league IS NOT NULL GROUP BY 1,2 HAVING count(*) >= 12', options: {} }, credentials: { postgres: { id: '5GYdciGwZ3GXZH0t', name: 'Postgres TransferWire' } } } });

const abfragen = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Abfragen bauen', parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: `const Q = [
 ['german', '(Transfer OR Wechsel OR Probetraining OR vereinslos OR Leihe OR Kaderplanung)'],
 ['english', '(transfer OR signing OR loan OR "free agent" OR trial) (football OR soccer)'],
 ['spanish', '(fichaje OR traspaso OR cesión OR "agente libre" OR prueba) fútbol'],
 ['italian', '(calciomercato OR trattativa OR prestito OR svincolato OR ufficiale)'],
 ['french', '(mercato OR transfert OR prêt OR "joueur libre" OR essai) football'],
 ['dutch', '(transfer OR huurt OR versterking OR transfervrij OR proefspeler) voetbal'],
 ['portuguese', '(transferência OR reforço OR empréstimo OR mercado) futebol'],
 ['turkish', '(transfer OR imza OR kiralık OR bonservis) futbol'],
 ['danish', '(transfer OR skifte OR lejeaftale OR transferfri OR prøvetræning) fodbold'],
 ['chinese', '(转会 OR 签约 OR 租借 OR 加盟) 足球']
];
return Q.map(([lang, q]) => ({ json: { sprache: lang, url: 'https://api.gdeltproject.org/api/v2/doc/doc?query=' + encodeURIComponent(q + ' sourcelang:' + lang) + '&mode=artlist&maxrecords=250&format=json&timespan=3h&sort=datedesc' } }));` } } });

const holen = node({ type: 'n8n-nodes-base.httpRequest', version: 4.3, config: { name: 'GDELT holen', onError: 'continueRegularOutput', parameters: { method: 'GET', url: expr('={{ $json.url }}'), sendHeaders: true, headerParameters: { parameters: [{ name: 'User-Agent', value: 'TransferWireBot/1.0 (+https://transferwire.de)' }] }, options: { timeout: 75000, batching: { batch: { batchSize: 1, batchInterval: 8000 } }, response: { response: { responseFormat: 'json' } } } } } });

const filter = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Vereinsfilter', parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: `const abfr = $('Abfragen bauen').all().map(i => i.json);
const teams = $('Vereine laden').all().map(i => i.json);
const norm = s => String(s || '').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').replace(/[^a-z0-9\\u4e00-\\u9fff]+/g, ' ').trim();
const STOP = new Set(['united','city','real','sporting','athletic','club','sport','racing','deportivo','atletico','stade','paris','union','fortuna','eintracht','borussia','dynamo','energie','arminia','hertha','hansa','werder','bayern','olympique','inter','como','lens','nice','metz','pau','laval','bari','pisa','genoa','lazio','roma','milan','torino','parma','monza','lecce','ajax','twente','utrecht','gent','genk','antwerp','porto','braga','benfica','arouca','estoril','sevilla','valencia','villarreal','granada','girona','elche','levante','burgos','cadiz','eibar','oviedo','malaga','almeria','cordoba','huesca','sabadell','tenerife','zaragoza','albacete','leganes','mallorca','mirandes','valladolid','getafe','osasuna','espanyol','barcelona','celta','alaves','betis','sociedad','madrid','lille','lyon','marseille','monaco','rennes','strasbourg','toulouse','angers','auxerre','lorient','nantes','reims','rodez','rouen','dijon','amiens','annecy','bastia','boulogne','dunkerque','grenoble','guingamp','montpellier','nancy','sochaux','clermont','troyes','havre','mans','brest','red','star','fc','sc','sv','tsv','vfl','vfb']);
const kernListe = [];
for (const t of teams) { const worte = norm(t.team).split(' ').filter(w => w.length >= 5 && !STOP.has(w)); const kern = worte.sort((a, b) => b.length - a.length)[0] || norm(t.team); if (kern.length >= 5 || /[\\u4e00-\\u9fff]/.test(kern)) kernListe.push({ kern, team: t.team, league: t.league }); }
const out = []; const seen = new Set();
$input.all().forEach((it, i) => { const q = abfr[i] || {}; const j = it.json || {}; const arr = Array.isArray(j.articles) ? j.articles : [];
  for (const a of arr) { const title = String(a.title || '').trim(); const url = String(a.url || '').trim(); if (!title || !url || seen.has(url)) continue; const nt = ' ' + norm(title) + ' '; const hit = kernListe.find(k => nt.indexOf(' ' + k.kern + ' ') >= 0 || (k.kern.length >= 8 && nt.indexOf(k.kern) >= 0)); if (!hit) continue; seen.add(url);
    const d = String(a.seendate || ''); const iso = d.length >= 15 ? d.slice(0,4) + '-' + d.slice(4,6) + '-' + d.slice(6,8) + 'T' + d.slice(9,11) + ':' + d.slice(11,13) + ':00Z' : '';
    out.push({ json: { title, url, domain: String(a.domain || ''), sprache: q.sprache || a.language || '', datum: iso, club: hit.team, league: hit.league } }); } });
return out;` } } });

const neu = node({ type: 'n8n-nodes-base.postgres', version: 2.7, config: { name: 'Neu? (gdelt_seen)', executeOnce: true, alwaysOutputData: true, parameters: { operation: 'executeQuery', query: "DELETE FROM gdelt_seen WHERE seen_at < now() - interval '7 days'; INSERT INTO gdelt_seen (url) SELECT unnest($1::text[]) ON CONFLICT (url) DO NOTHING RETURNING url", options: { queryReplacement: expr('={{ [ $input.all().map(i => i.json.url) ] }}') } }, credentials: { postgres: { id: '5GYdciGwZ3GXZH0t', name: 'Postgres TransferWire' } } } });

const liste = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Zeilen bauen', parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: `const neu = new Set($input.all().map(i => i.json && i.json.url).filter(Boolean));
const alle = $('Vereinsfilter').all().map(i => i.json).filter(a => neu.has(a.url));
const zeilen = alle.slice(0, 150).map(a => '- ' + a.title + ' | Verein: ' + a.club + ' (' + a.league + ') | Quelle: ' + a.domain + ' | Sprache: ' + a.sprache + ' | ' + a.url + ' | ' + (a.datum || 'ohne Datum'));
return [{ json: { count: zeilen.length, gesamt: $('Vereinsfilter').all().length, list: zeilen.join('\\n') } }];` } } });

const hatZeilen = ifElse({ version: 2.2, config: { name: 'Neue Zeilen?', parameters: { conditions: { options: { caseSensitive: true, leftValue: '', typeValidation: 'loose' }, conditions: [{ leftValue: expr('={{ $json.count }}'), operator: { type: 'number', operation: 'gt' }, rightValue: 0 }], combinator: 'and' } } } });

const kiPlatz = node({ type: 'n8n-nodes-base.noOp', version: 1, config: { name: 'KI-Platzhalter' } });

const splitN = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Einzelmeldungen', parameters: { mode: 'runOnceForAllItems', language: 'javaScript', jsCode: `const out = [];
for (const it of $input.all()) { const j = it.json || {}; let arr = []; if (Array.isArray(j.items)) arr = j.items; else if (j.output && Array.isArray(j.output.items)) arr = j.output.items; else if (Array.isArray(j.output)) arr = j.output; for (const r of arr) { if (r && (r.headline || r.player_name || r.to_club)) out.push({ json: r }); } }
return out;` } } });

const mappen = node({ type: 'n8n-nodes-base.set', version: 3.4, config: { name: 'Auf Tabellenschema mappen', parameters: { mode: 'manual', includeOtherFields: false, assignments: { assignments: [
  { id: 'a1', name: 'news_id', value: expr("={{ 'gd-' + $now.toMillis() + '-' + Math.floor(Math.random()*100000) }}"), type: 'string' },
  { id: 'a2', name: 'dedup_key', value: expr("={{ (($json.player_name || '') + '|' + ($json.from_club || '') + '|' + ($json.to_club || '') + '|' + ($json.type || '')).toLowerCase() }}"), type: 'string' },
  { id: 'a3', name: 'sport', value: 'fussball', type: 'string' },
  { id: 'a4', name: 'league', value: expr('={{ $json.league || "" }}'), type: 'string' },
  { id: 'a5', name: 'type', value: expr('={{ $json.type || "geruecht" }}'), type: 'string' },
  { id: 'a6', name: 'headline', value: expr('={{ $json.headline }}'), type: 'string' },
  { id: 'a7', name: 'summary', value: expr('={{ $json.summary || "" }}'), type: 'string' },
  { id: 'a8', name: 'player_name', value: expr('={{ $json.player_name || "" }}'), type: 'string' },
  { id: 'a9', name: 'player_position', value: expr('={{ $json.player_position || "" }}'), type: 'string' },
  { id: 'a10', name: 'player_age', value: expr('={{ $json.player_age || 0 }}'), type: 'number' },
  { id: 'a11', name: 'player_nationality', value: expr('={{ $json.player_nationality || "" }}'), type: 'string' },
  { id: 'a12', name: 'from_club', value: expr('={{ $json.from_club || "" }}'), type: 'string' },
  { id: 'a13', name: 'to_club', value: expr('={{ $json.to_club || "" }}'), type: 'string' },
  { id: 'a14', name: 'fee', value: expr('={{ $json.fee || "" }}'), type: 'string' },
  { id: 'a15', name: 'reliability', value: expr('={{ Math.min(3, $json.reliability || 2) }}'), type: 'number' },
  { id: 'a16', name: 'position_needed', value: expr('={{ $json.position_needed || "" }}'), type: 'string' },
  { id: 'a17', name: 'source_name', value: expr('={{ $json.source_name || "Lokalmedium (GDELT)" }}'), type: 'string' },
  { id: 'a18', name: 'source_url', value: expr('={{ $json.source_url || "" }}'), type: 'string' },
  { id: 'a19', name: 'sources_json', value: expr("={{ JSON.stringify([{ name: ($json.source_name || 'Lokalmedium'), url: ($json.source_url || '') }]) }}"), type: 'string' },
  { id: 'a20', name: 'published_at', value: expr('={{ $json.published_at || $now.toISO() }}'), type: 'string' },
  { id: 'a21', name: 'created_at', value: expr('={{ $now.toISO() }}'), type: 'string' }
] } } } });

const upsert = node({ type: 'n8n-nodes-base.dataTable', version: 1.1, config: { name: 'Transfernews (Upsert)', onError: 'continueRegularOutput', parameters: { resource: 'row', operation: 'upsert', dataTableId: { __rl: true, mode: 'id', value: 'vxAKGr0ljM6q21KY', cachedResultName: 'Transfernews' }, matchType: 'allConditions', filters: { conditions: [{ keyName: 'dedup_key', condition: 'eq', keyValue: expr('={{ $json.dedup_key }}') }] }, columns: { mappingMode: 'autoMapInputData', matchingColumns: ['dedup_key'], value: null, schema: [] }, options: {} } } });

export default workflow('tw-gdelt-lokalmedien', 'TW Quelle: GDELT Lokalmedien (alle 2 h)')
  .add(start).to(gate).to(frei.onTrue(vereine))
  .add(vereine).to(abfragen).to(holen).to(filter).to(neu).to(liste).to(hatZeilen.onTrue(kiPlatz))
  .add(kiPlatz).to(splitN).to(mappen).to(upsert);
