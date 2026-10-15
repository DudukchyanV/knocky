#!/bin/bash
# First-boot setup. Paste into the "Cloud-init" field as:
#   #!/bin/sh
#   curl -fsSL https://raw.githubusercontent.com/DudukchyanV/knocky/main/server/bootstrap.sh | bash
# The server then pulls github.com/DudukchyanV/knocky every minute
# and runs server/deploy.sh on each new commit. No SSH access needed.
set -e
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -y -q git curl ufw

cat > /usr/local/bin/knocky-pull <<'P'
#!/bin/bash
set -e
R=/opt/knocky/repo; S=/opt/knocky/deployed; mkdir -p /opt/knocky
[ -d $R/.git ] || git clone -q https://github.com/DudukchyanV/knocky.git $R
cd $R && git fetch -q origin main
NEW=$(git rev-parse origin/main)
[ "$NEW" = "$(cat $S 2>/dev/null)" ] && exit 0
git reset -q --hard origin/main
echo "== $(date) $NEW" >> /var/log/knocky-deploy.log
if [ -x server/deploy.sh ]; then
  server/deploy.sh >> /var/log/knocky-deploy.log 2>&1 && echo $NEW > $S
else echo $NEW > $S; fi
P
chmod 755 /usr/local/bin/knocky-pull

cat > /etc/systemd/system/knocky-pull.service <<'P'
[Unit]
Description=Pull Knocky repo and deploy
[Service]
Type=oneshot
ExecStart=/usr/local/bin/knocky-pull
P

cat > /etc/systemd/system/knocky-pull.timer <<'P'
[Unit]
Description=Pull Knocky repo every minute
[Timer]
OnBootSec=30
OnUnitActiveSec=60
[Install]
WantedBy=timers.target
P

ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
systemctl daemon-reload
systemctl enable --now knocky-pull.timer
