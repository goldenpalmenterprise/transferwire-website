set -u
echo "=== 0. Externe Passwort-Logins (nicht Docker-Netz) im Log? ==="
EXT=$(grep -h "Accepted password" /var/log/auth.log /var/log/auth.log.1 2>/dev/null | grep -v -E "from (172\.1[6-9]\.|172\.2[0-9]\.|172\.3[01]\.|127\.)" | wc -l)
echo "externe akzeptierte Passwort-Logins: $EXT"
grep -h "Accepted" /var/log/auth.log /var/log/auth.log.1 2>/dev/null | grep -v -E "from (172\.1[6-9]\.|172\.2[0-9]\.|172\.3[01]\.|127\.)" | tail -3 | cut -c1-120
echo "=== 1. fail2ban ==="
export DEBIAN_FRONTEND=noninteractive
apt-get install -y -qq fail2ban >/dev/null 2>&1 && echo "fail2ban installiert" || echo "fail2ban Installation FEHLGESCHLAGEN"
cat > /etc/fail2ban/jail.local <<'JAIL'
[DEFAULT]
bantime  = 2h
findtime = 10m
maxretry = 4
backend  = systemd
ignoreip = 127.0.0.1/8 172.16.0.0/12

[sshd]
enabled = true
mode    = aggressive
JAIL
systemctl enable --now fail2ban >/dev/null 2>&1; systemctl restart fail2ban; sleep 2
fail2ban-client status sshd 2>/dev/null | head -8
echo "=== 2. sshd-Haertung ==="
if [ "$EXT" = "0" ]; then
  cat > /etc/ssh/sshd_config.d/00-tw-hardening.conf <<'SSHD'
# TransferWire Haertung 24.08.2026: Passwort-Login nur aus dem Docker-Netz (n8n-Admin-Shell), sonst nur Schluessel.
PasswordAuthentication no
MaxAuthTries 3
LoginGraceTime 20
SSHD
  grep -q "TW-MATCH-DOCKER" /etc/ssh/sshd_config || cat >> /etc/ssh/sshd_config <<'SSHD'

# TW-MATCH-DOCKER: n8n-Admin-Shell (Docker-Netz) darf weiter per Passwort
Match Address 172.16.0.0/12,127.0.0.0/8
    PasswordAuthentication yes
SSHD
  if sshd -t 2>&1; then systemctl restart ssh 2>/dev/null || systemctl restart sshd; echo "sshd neu gestartet, Konfiguration gueltig"; else echo "sshd -t FEHLER -> Haertung zurueckgenommen"; rm -f /etc/ssh/sshd_config.d/00-tw-hardening.conf; sed -i '/# TW-MATCH-DOCKER/,$d' /etc/ssh/sshd_config; fi
else
  echo "UEBERSPRUNGEN: es gibt externe Passwort-Logins ($EXT) -> Boss muss zuerst einen SSH-Schluessel hinterlegen"
  cat > /etc/ssh/sshd_config.d/00-tw-hardening.conf <<'SSHD'
MaxAuthTries 3
LoginGraceTime 20
SSHD
  sshd -t && (systemctl restart ssh 2>/dev/null || systemctl restart sshd) && echo "nur MaxAuthTries/LoginGraceTime gesetzt"
fi
echo "--- effektiv ---"; sshd -T 2>/dev/null | grep -E "^(passwordauthentication|permitrootlogin|maxauthtries|logingracetime)"
echo "=== 3. Backups ==="
mkdir -p /opt/transferwire/backups
cat > /opt/transferwire/backup.sh <<'BK'
#!/bin/bash
# Taegliches Backup: beide Postgres-DBs (n8n + transferwire) + Konfiguration, 14 Tage Aufbewahrung
set -e
D=/opt/transferwire/backups; T=$(date +%F_%H%M)
docker exec transferwire-postgres-1 pg_dumpall -U n8n | gzip -6 > "$D/pg_all_$T.sql.gz"
tar czf "$D/config_$T.tgz" -C /opt/transferwire docker-compose.yml .env 2>/dev/null || true
find "$D" -name 'pg_all_*.sql.gz' -mtime +14 -delete; find "$D" -name 'config_*.tgz' -mtime +14 -delete
echo "$(date -Is) backup ok $(du -h "$D/pg_all_$T.sql.gz" | cut -f1)" >> "$D/backup.log"
BK
chmod 700 /opt/transferwire/backup.sh; chmod 700 /opt/transferwire/backups
( crontab -l 2>/dev/null | grep -v backup.sh; echo "30 3 * * * /opt/transferwire/backup.sh >> /opt/transferwire/backups/cron.log 2>&1" ) | crontab -
/opt/transferwire/backup.sh && tail -1 /opt/transferwire/backups/backup.log && ls -la /opt/transferwire/backups | tail -3
echo "=== 4. Docker-Images: n8n Update-Stand ==="
docker exec transferwire-n8n-1 n8n --version 2>/dev/null
