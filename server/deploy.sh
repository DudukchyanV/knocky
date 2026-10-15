#!/bin/bash
# Runs on the server (as root) every time a new commit lands on main.
# Pulled by /usr/local/bin/knocky-pull (installed by bootstrap.sh / cloud-init.yaml).
set -euo pipefail
REPO=/opt/knocky/repo
WWW=/opt/knocky/www
DATA=/opt/knocky/data
mkdir -p "$WWW"
export DEBIAN_FRONTEND=noninteractive

# packages: web server + Python libraries for the app (from Ubuntu, no pip needed)
PKGS="caddy python3-starlette python3-uvicorn python3-openpyxl python3-cryptography python3-multipart sqlite3"
MISSING=""
for p in $PKGS; do dpkg -s "$p" >/dev/null 2>&1 || MISSING="$MISSING $p"; done
if [ -n "$MISSING" ]; then apt-get update -q && apt-get install -yq $MISSING; fi

# app user and folders: data and secrets belong to the app, code stays root-owned
id knocky >/dev/null 2>&1 || useradd --system --home /opt/knocky --shell /usr/sbin/nologin knocky
mkdir -p "$DATA" /etc/knocky
chown -R knocky:knocky "$DATA" /etc/knocky
chmod 700 /etc/knocky

# app service
cat > /etc/systemd/system/knocky-app.service <<UNIT
[Unit]
Description=Knocky app (cabinet, guest pages, RSVP)
After=network.target
[Service]
User=knocky
Group=knocky
WorkingDirectory=$REPO/server/app
Environment=KNOCKY_DATA=$DATA
Environment=KNOCKY_SECRETS=/etc/knocky/secrets.json
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 --proxy-headers --forwarded-allow-ips 127.0.0.1 --no-access-log
Restart=always
RestartSec=3
NoNewPrivileges=true
ProtectSystem=full
ProtectHome=true
PrivateTmp=true
ReadWritePaths=$DATA /etc/knocky
[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable knocky-app >/dev/null 2>&1 || true
systemctl restart knocky-app

# web server config from this repo
install -m 644 "$REPO/server/Caddyfile" /etc/caddy/Caddyfile
systemctl reload caddy || systemctl restart caddy

# daily copy of the database (Timeweb also backs up the whole server)
cat > /etc/cron.daily/knocky-db <<'CRON'
#!/bin/sh
mkdir -p /opt/knocky/backup
sqlite3 /opt/knocky/data/knocky.db ".backup '/opt/knocky/backup/knocky-$(date +%F).db'" 2>/dev/null
find /opt/knocky/backup -name 'knocky-*.db' -mtime +14 -delete
CRON
chmod 755 /etc/cron.daily/knocky-db

# status page: lets us check the server without logging in (no secrets here)
sleep 3
COMMIT=$(git -C "$REPO" log -1 --format='%h %s')
MEM=$(free -m | awk '/Mem/{print $3" / "$2" MB used"}')
DISK=$(df -h / | awk 'NR==2{print $3" / "$2" used"}')
APP=$(systemctl is-active knocky-app || true)
HEALTH=$(curl -s --max-time 5 http://127.0.0.1:8000/api/health || echo "no answer")
LOG=$(tail -n 25 /var/log/knocky-deploy.log 2>/dev/null | sed 's/&/\&amp;/g;s/</\&lt;/g' || true)
APPLOG=$(journalctl -u knocky-app -n 15 --no-pager 2>/dev/null | sed 's/&/\&amp;/g;s/</\&lt;/g' || true)
cat > "$WWW/status.html" <<HTML
<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><title>Knocky server</title>
<pre>
ok
commit:  $COMMIT
updated: $(date '+%Y-%m-%d %H:%M:%S %Z')
uptime: $(uptime -p)
memory: $MEM
disk:   $DISK
app:    $APP
health: $HEALTH

--- deploy log
$LOG

--- app log
$APPLOG
</pre>
HTML
echo "deployed $COMMIT, app $APP"
