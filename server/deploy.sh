#!/bin/bash
# Runs on the server (as root) every time a new commit lands on main.
# Pulled by /usr/local/bin/knocky-pull (installed by cloud-init.yaml).
set -euo pipefail
REPO=/opt/knocky/repo
WWW=/opt/knocky/www
mkdir -p "$WWW"

# web server: Caddy from Ubuntu repo, config from this repo
if ! command -v caddy >/dev/null; then apt-get update -q && apt-get install -yq caddy; fi
install -m 644 "$REPO/server/Caddyfile" /etc/caddy/Caddyfile
systemctl reload caddy || systemctl restart caddy

# status page: lets us check the server without logging in
COMMIT=$(git -C "$REPO" log -1 --format='%h %s')
MEM=$(free -m | awk '/Mem/{print $3" / "$2" MB used"}')
DISK=$(df -h / | awk 'NR==2{print $3" / "$2" used"}')
cat > "$WWW/status.html" <<HTML
<!doctype html><meta charset="utf-8"><title>Knocky server</title>
<pre>
ok
commit:  $COMMIT
updated: $(date '+%Y-%m-%d %H:%M:%S %Z')
uptime: $(uptime -p)
memory: $MEM
disk:   $DISK
</pre>
HTML
echo "deployed $COMMIT"
