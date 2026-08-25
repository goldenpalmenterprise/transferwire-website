import sys, base64, subprocess
PW = "085de3ac26a319138d0586c18009f0d44a4c31764f9502f3"
def psql(sql):
    return subprocess.run(["docker", "exec", "-i", "-e", "PGPASSWORD=" + PW, "transferwire-postgres-1", "psql", "-U", "n8n", "-d", "n8n", "-At"], input=sql, capture_output=True, text=True)
r = psql("SELECT n->>'name' || '|' || translate(encode(convert_to(n->'parameters'->>'jsCode', 'UTF8'), 'base64'), E'\\n', '') FROM workflow_entity w JOIN workflow_history v ON v.\"versionId\"=w.\"activeVersionId\", jsonb_array_elements(v.nodes::jsonb) n WHERE w.id='4BjusAxYNt1uvLue' AND n->>'name' IN ('Vereins-Rotation','Anfrage bauen');")
codes = {}
for line in r.stdout.strip().splitlines():
    name, b64 = line.split("|", 1)
    txt = base64.b64decode(b64).decode("utf-8")
    if name == "Vereins-Rotation":
        i = txt.index("// Variante 1")
        txt = txt[:i] + ('// Variante 2 (24.08.2026, KOSTENBREMSE): Wochen-Rotation statt "alle Laender taeglich" (466 Recherchen/Tag = ca. 10 USD/Tag).\n'
            '// Deutschland: jeder Verein alle 3 Tage; Ausland: jeder Verein einmal pro Woche -> ca. 18 + 59 = ~77 Recherchen/Tag.\n'
            'const tag = Math.floor(Date.now() / 86400000);\nconst out = [];\n'
            'DE.klubs.forEach((k, i) => { if (i % 3 === tag % 3) out.push({ json: { verein: k, land: DE.land, ligen: DE.ligen } }); });\n'
            'let idx = 0;\nfor (const gr of INTL) { for (const k of gr.klubs) { if (idx % 7 === tag % 7) out.push({ json: { verein: k, land: gr.land, ligen: gr.ligen } }); idx++; } }\nreturn out;\n')
    else:
        alt = "bodyStr: JSON.stringify({ model: 'gpt-5-mini', tools: [{ type: 'web_search' }], input: prompt })"
        assert alt in txt, "Body-Muster fehlt"
        txt = txt.replace(alt, "bodyStr: JSON.stringify({ model: 'gpt-5-mini', tools: [{ type: 'web_search', search_context_size: 'low' }], input: prompt, reasoning: { effort: 'low' }, max_output_tokens: 900 })")
    codes[name] = txt
tag = "$twq$"
assert tag not in codes["Vereins-Rotation"] + codes["Anfrage bauen"]
sql = ("UPDATE workflow_entity SET nodes = (SELECT jsonb_agg(CASE WHEN n->>'name'='Vereins-Rotation' THEN jsonb_set(n, '{parameters,jsCode}', to_jsonb(" + tag + codes["Vereins-Rotation"] + tag + "::text)) WHEN n->>'name'='Anfrage bauen' THEN jsonb_set(n, '{parameters,jsCode}', to_jsonb(" + tag + codes["Anfrage bauen"] + tag + "::text)) ELSE n END ORDER BY o) FROM jsonb_array_elements(nodes::jsonb) WITH ORDINALITY AS t(n, o))::json WHERE id='4BjusAxYNt1uvLue';")
r2 = psql(sql)
print("UPDATE:", r2.stdout.strip(), r2.stderr.strip()[:200])
r3 = psql("SELECT n->>'name' || ': ' || (n->'parameters'->>'jsCode' LIKE '%KOSTENBREMSE%' OR n->'parameters'->>'jsCode' LIKE '%search_context_size%') FROM workflow_entity w, jsonb_array_elements(w.nodes::jsonb) n WHERE w.id='4BjusAxYNt1uvLue' AND n->>'name' IN ('Vereins-Rotation','Anfrage bauen');")
print(r3.stdout.strip())
