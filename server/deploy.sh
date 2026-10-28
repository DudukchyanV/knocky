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
PKGS="caddy python3-starlette python3-uvicorn python3-openpyxl python3-cryptography python3-multipart sqlite3 python3-pil python3-pip fonts-dejavu-core rsync"
MISSING=""
for p in $PKGS; do dpkg -s "$p" >/dev/null 2>&1 || MISSING="$MISSING $p"; done
if [ -n "$MISSING" ]; then apt-get update -q && apt-get install -yq $MISSING; fi

# headless browser for cover pictures (link previews, stories); if it fails, a simple card is used instead
PW=/opt/knocky/pw
python3 -c "import playwright" 2>/dev/null || pip3 install -q --break-system-packages "playwright==1.56.0" || echo "playwright: pip install failed"
if python3 -c "import playwright" 2>/dev/null && ! ls -d $PW/chromium_headless_shell-* >/dev/null 2>&1; then
  PLAYWRIGHT_BROWSERS_PATH=$PW timeout 900 python3 -m playwright install --with-deps chromium || echo "playwright: browser install failed"
  chmod -R a+rX $PW 2>/dev/null || true
fi

# public site knocky.ru (served by Caddy once DNS points here): only the site files, not the code
SITE=/opt/knocky/site
mkdir -p $SITE
rsync -a --delete --include='/*.html' --include='/*.txt' --include='/*.xml' --include='/CNAME' --exclude='*' "$REPO/" "$SITE/"

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
Environment=PLAYWRIGHT_BROWSERS_PATH=/opt/knocky/pw
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
# install only a config that Caddy accepts, so a mistake can't take the sites down
if caddy validate --config "$REPO/server/Caddyfile" --adapter caddyfile >/dev/null 2>&1; then
  install -m 644 "$REPO/server/Caddyfile" /etc/caddy/Caddyfile
  systemctl reload caddy || systemctl restart caddy
else
  echo "Caddyfile is not valid, keeping the old one"
fi

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
PICS=$( (python3 -c "import playwright" 2>/dev/null && ls -d $PW/chromium_headless_shell-* >/dev/null 2>&1) && echo "browser ok" || echo "simple cards (no browser)")
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
pictures: $PICS

--- deploy log
$LOG

--- app log
$APPLOG
</pre>
HTML
echo "deployed $COMMIT, app $APP"
