const news = $('Neue Meldungen').all().map(i => i.json);
const spieler = $input.all().map(i => i.json);
let verl = []; try { verl = $('Verletzungen laden').all().map(i => i.json); } catch (e) { verl = []; }
const norm = s => String(s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
const normSort = s => norm(s).split(' ').filter(Boolean).sort().join(' ');
// Vereins-Karte: bekannte Vereinsnamen (aus players) mit Liga
const teamLiga = {}; for (const p of spieler) { if (p.team && p.league && p.team !== 'Vereinslos') { const k = norm(p.team); if (!teamLiga[k]) teamLiga[k] = { team: p.team, league: p.league }; } }
const teamKeys = Object.keys(teamLiga);
const findeTeam = club => { const c = norm(club); if (!c || c.length < 3) return null; if (teamLiga[c]) return teamLiga[c]; const hits = teamKeys.filter(k => k.length >= 5 && c.length >= 5 && (c.indexOf(k) >= 0 || k.indexOf(c) >= 0)); return hits.length === 1 ? teamLiga[hits[0]] : null; };
// Namensindex
const byKey = {}; const byLast = {};
for (const p of spieler) { const n = norm(p.name); if (!n) continue; const key = normSort(n); (byKey[key] = byKey[key] || []).push(p); const toks = n.split(' '); const last = toks[toks.length - 1]; if (last && last.length >= 3) (byLast[last] = byLast[last] || []).push(p); }
const kandidaten = name => { const n = norm(name); if (!n) return []; const direkt = byKey[normSort(n)]; if (direkt && direkt.length) return direkt; const toks = n.split(' '); if (toks.length < 2) return []; const last = toks[toks.length - 1]; const first = toks[0]; const liste = byLast[last] || []; return liste.filter(p => { const pt = norm(p.name).split(' '); return pt[0] && (pt[0] === first || (first.length <= 2 && pt[0][0] === first[0])); }); };
const out = []; let maxCreated = '';
for (const n of news) {
  if (n.createdAt && String(n.createdAt) > maxCreated) maxCreated = String(n.createdAt);
  const rel = Number(n.reliability) || 0; const typ = n.type; if (!n.player_name) continue;
  let kand = kandidaten(n.player_name); if (!kand.length) continue;
  if (kand.length > 1) { const von = norm(n.from_club); const zu = norm(n.to_club); kand = kand.filter(p => { const t = norm(p.team); return (von && t && (t === von || (von.length >= 5 && (t.indexOf(von) >= 0 || von.indexOf(t) >= 0)))) || (zu && t && (t === zu || (zu.length >= 5 && (t.indexOf(zu) >= 0 || zu.indexOf(t) >= 0)))); }); if (kand.length !== 1) continue; }
  const p = kand[0]; const quelle = n.source_name || 'Meldung';
  if ((typ === 'fix' || typ === 'leihe') && rel >= 4 && n.to_club) { const T = findeTeam(n.to_club); if (!T) continue; if (norm(p.team) === norm(T.team)) continue; out.push({ json: { feld: 'team', player_id: Number(p.player_id), name: p.name, alt: p.team || '', neu: T.team, league: T.league, quelle, news_id: n.news_id || '', reliability: rel } }); p.team = T.team; p.league = T.league; }
  else if (typ === 'verfuegbar' && rel >= 3) { if (norm(p.team) === 'vereinslos') continue; out.push({ json: { feld: 'team', player_id: Number(p.player_id), name: p.name, alt: p.team || '', neu: 'Vereinslos', league: '', quelle, news_id: n.news_id || '', reliability: rel } }); p.team = 'Vereinslos'; p.league = ''; }
  else if (typ === 'vertrag' && rel >= 3) { const txt = String(n.headline || '') + ' ' + String(n.summary || ''); const m = txt.match(/bis\s+(?:zum\s+|ins?\s+jahr\s+|sommer\s+|juni\s+|ende\s+)?(20\d\d)/i) || txt.match(/(?:verl[äa]ngert|extends?|renew|prolong|rinnov|renov|verlengd|uzat)[^.]{0,60}?(20\d\d)/i); if (!m) continue; const neu = m[1] + '-06-30'; if (String(p.contract_until || '').slice(0, 4) === m[1]) continue; out.push({ json: { feld: 'contract_until', player_id: Number(p.player_id), name: p.name, alt: p.contract_until || '', neu, league: p.league || '', quelle, news_id: n.news_id || '', reliability: rel } }); p.contract_until = neu; }
}
// Verletzungen: aktuelle Ausfaelle (injuries, letzte 10 Tage) auf fitness_note spiegeln, Genesene zuruecksetzen
const fmtD = d => { const s = String(d || ''); const m = s.match(/(\d{4})-(\d{2})-(\d{2})/); return m ? m[3] + '.' + m[2] + '.' : ''; };
const verlMap = {}; const SKIP = /coach|red card|yellow|suspend|sperre|national team|international duty|rest|personal|inactive|transfer negotiations|loan agreement|not in squad|unregistered/i;
for (const v of verl) { if (SKIP.test(String(v.reason || ''))) continue; const kand = kandidaten(v.player); let p = null; if (kand.length === 1) p = kand[0]; else if (kand.length > 1) { const t = norm(v.team); const f = kand.filter(x => t && norm(x.team) && (norm(x.team).indexOf(t) >= 0 || t.indexOf(norm(x.team)) >= 0)); if (f.length === 1) p = f[0]; } if (!p) continue;
  const typ = String(v.itype || ''); const note = 'Verletzt: ' + (v.reason || 'unbekannt') + (typ && !/missing fixture|questionable/i.test(typ) ? ' (' + typ + ')' : '') + (v.first_seen ? ' \u00b7 seit ' + fmtD(v.first_seen) : ''); const alt = verlMap[p.player_id]; if (!alt || String(v.last_seen) > String(alt.last_seen)) verlMap[p.player_id] = { note, last_seen: v.last_seen }; }
for (const p of spieler) { const v = verlMap[p.player_id]; const soll = v ? v.note : ''; const ist = String(p.fitness_note || ''); if (soll === ist) continue; if (!soll && !/^Verletzt:/.test(ist)) continue; out.push({ json: { feld: 'fitness_note', player_id: Number(p.player_id), name: p.name, alt: ist, neu: soll, league: p.league || '', quelle: soll ? 'Verletzungs-Sync' : 'Verletzungs-Sync (genesen)', news_id: '', reliability: 4 } }); }
out.push({ json: { _meta: true, geprueft: news.length, aenderungen: out.length, bis: maxCreated } });
return out;
