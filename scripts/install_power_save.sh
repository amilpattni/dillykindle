#!/bin/bash
set -euo pipefail

sudo tee /usr/local/bin/dillykindle-power-save.sh > /dev/null <<'SCRIPT'
#!/bin/bash

/usr/bin/vcgencmd display_power 0 2>/dev/null || true
/usr/sbin/rfkill block bluetooth 2>/dev/null || true
SCRIPT

sudo chmod +x /usr/local/bin/dillykindle-power-save.sh

sudo tee /etc/systemd/system/dillykindle-power-save.service > /dev/null <<'SERVICE'
[Unit]
Description=DillyKindle power saving setup
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/dillykindle-power-save.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable dillykindle-power-save.service

echo "DillyKindle power-save service installed."
echo "Boot behavior:"
echo "- HDMI off"
echo "- Bluetooth off"
echo "- Wi-Fi stays on"
