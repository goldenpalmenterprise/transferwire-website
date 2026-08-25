echo "=== 1. Docker-Container + veroeffentlichte Ports ==="
docker ps --format '{{.Names}} | {{.Image}} | {{.Ports}}' 2>/dev/null
echo; echo "=== 2. Host: Firewall / SSH / Updates / Backups (read-only via Host-Mount) ==="
docker run --rm --net=host --pid=host -v /:/host alpine:3.20 sh -c '
echo "-- ufw --"; chroot /host ufw status 2>/dev/null | head -12 || echo "ufw nicht verfuegbar";
echo "-- iptables INPUT (Kurz) --"; chroot /host iptables -S INPUT 2>/dev/null | head -8;
echo "-- Listening (host) --"; chroot /host ss -tlnp 2>/dev/null | awk "NR==1 || /LISTEN/" | sed "s/users:((\"//; s/\",pid.*//" | head -20;
echo "-- sshd --"; grep -Ei "^(PasswordAuthentication|PermitRootLogin|PubkeyAuthentication|Port )" /host/etc/ssh/sshd_config /host/etc/ssh/sshd_config.d/*.conf 2>/dev/null;
echo "-- fail2ban --"; ls /host/etc/fail2ban 2>/dev/null | head -3 || echo "kein fail2ban";
echo "-- unattended-upgrades --"; cat /host/etc/apt/apt.conf.d/20auto-upgrades 2>/dev/null || echo "keine auto-upgrades konfiguriert";
echo "-- Backups (cron) --"; cat /host/etc/crontab /host/etc/cron.d/* 2>/dev/null | grep -v "^#" | grep -Ei "backup|pg_dump|borg|restic" || echo "KEIN Backup-Cron gefunden"; ls /host/var/spool/cron/crontabs 2>/dev/null; for u in /host/var/spool/cron/crontabs/*; do echo "crontab $(basename $u):"; grep -v "^#" "$u" | head -5; done 2>/dev/null;
echo "-- OS --"; head -2 /host/etc/os-release; echo "kernel: $(cat /host/proc/version | cut -c1-60)";
echo "-- docker-compose (Ports/Volumes/Env-Keys) --"; f=$(ls /host/opt/transferwire/docker-compose.y*ml 2>/dev/null | head -1); [ -n "$f" ] && grep -En "^\s*(-\s*\"?[0-9.]*:?[0-9]+:[0-9]+|ports:|image:|N8N_[A-Z_]+=|EXECUTIONS_[A-Z_]+=|WEBHOOK_URL|DB_POSTGRESDB_PASSWORD|POSTGRES_PASSWORD)" "$f" | sed -E "s/(PASSWORD|KEY|SECRET|TOKEN)=.*/\1=***/" | head -40;
echo "-- .env Keys (nur Namen) --"; [ -f /host/opt/transferwire/.env ] && cut -d= -f1 /host/opt/transferwire/.env | tr "\n" " " ; echo;
'
echo; echo "=== 3. n8n: Version + Sicherheitsrelevante Umgebung ==="
docker exec $(docker ps -qf name=n8n | head -1) sh -c 'n8n --version 2>/dev/null; env | grep -E "^(N8N_SECURE_COOKIE|N8N_BLOCK_ENV_ACCESS_IN_NODE|N8N_RESTRICT_FILE_ACCESS_TO|N8N_BLOCK_FILE_ACCESS_TO_N8N_FILES|NODES_EXCLUDE|N8N_PUBLIC_API_DISABLED|N8N_USER_MANAGEMENT_DISABLED|N8N_DIAGNOSTICS_ENABLED|EXECUTIONS_DATA_MAX_AGE|EXECUTIONS_DATA_PRUNE|N8N_PROXY_HOPS|N8N_RUNNERS_ENABLED)=" | sort; echo "docker.sock im n8n-Container: $( [ -S /var/run/docker.sock ] && echo JA || echo nein )"'
echo; echo "=== 4. Postgres: Rollen/Rechte tw_app, Verbindungen von aussen? ==="
docker exec -e PGPASSWORD=085de3ac26a319138d0586c18009f0d44a4c31764f9502f3 transferwire-postgres-1 psql -U n8n -d n8n -At -c "SELECT rolname || ' super=' || rolsuper || ' login=' || rolcanlogin FROM pg_roles WHERE rolname NOT LIKE 'pg_%'" -c "SHOW listen_addresses" -c "SELECT count(*) || ' n8n-User, MFA aktiv: ' || count(*) FILTER (WHERE \"mfaEnabled\") FROM \"user\"" 2>&1 | head -8
echo; echo "=== 5. Oeffentliche Webhooks (aktiv) ==="
docker exec -e PGPASSWORD=085de3ac26a319138d0586c18009f0d44a4c31764f9502f3 transferwire-postgres-1 psql -U n8n -d n8n -At -c "SELECT w.name || ' :: ' || string_agg(n->'parameters'->>'httpMethod' || ' /' || (n->'parameters'->>'path'), ', ') FROM workflow_entity w JOIN workflow_history v ON v.\"versionId\"=w.\"activeVersionId\", jsonb_array_elements(v.nodes::jsonb) n WHERE w.active AND n->>'type'='n8n-nodes-base.webhook' GROUP BY w.name ORDER BY 1"
echo; echo "=== 6. SQL-Injection-Risiko: Postgres-Queries mit Expressions im SQL-Text (statt Parameter) ==="
docker exec -e PGPASSWORD=085de3ac26a319138d0586c18009f0d44a4c31764f9502f3 transferwire-postgres-1 psql -U n8n -d n8n -At -c "SELECT w.name || ' :: ' || n->>'name' || ' :: ' || left(regexp_replace(n->'parameters'->>'query', E'\\s+', ' ', 'g'), 160) FROM workflow_entity w JOIN workflow_history v ON v.\"versionId\"=w.\"activeVersionId\", jsonb_array_elements(v.nodes::jsonb) n WHERE w.active AND n->>'type' LIKE '%postgres%' AND n->'parameters'->>'query' LIKE '%{{%'" | head -20
echo "(leer = alle Queries parametrisiert)"
echo; echo "=== 7. Code-Nodes, die Nutzereingaben in SQL-Strings bauen ==="
docker exec -e PGPASSWORD=085de3ac26a319138d0586c18009f0d44a4c31764f9502f3 transferwire-postgres-1 psql -U n8n -d n8n -At -c "SELECT w.name || ' :: ' || n->>'name' FROM workflow_entity w JOIN workflow_history v ON v.\"versionId\"=w.\"activeVersionId\", jsonb_array_elements(v.nodes::jsonb) n WHERE w.active AND n->>'type'='n8n-nodes-base.code' AND n->'parameters'->>'jsCode' ~ '(SELECT|INSERT|UPDATE|DELETE) .*\\+ *(b|body|req|q|frage|email)\\.' " | head -10
echo "(leer = keine erkennbare String-Konkatenation von Body-Feldern in SQL)"
