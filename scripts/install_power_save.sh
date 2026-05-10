#!/bin/bash
set -euo pipefail

sudo tee /usr/local/bin/dillykindle-power-save.sh > /dev/null <<'EOF'
#!/bin/bash

/usr/bin/vcgencmd display_power 0 2>/dev/null || true
/usr/sbin/rfkill block bluetooth 2>/dev/null || true
/usr/bin/nmcli radio wifi off 2>/dev/null || true
EOF

sudo chmod +x /usr/local/bin/dillykindle-power-save.sh

sudo tee /etc/systemd/system/dillykindle-power-save.service > /dev/null <<'EOF'
[Unit]
Description=DillyKindle power saving setup
After=multi-user.target NetworkManager.service
Wants=NetworkManager.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/dillykindle-power-save.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable dillykindle-power-save.service

echo "DillyKindle power-save service installed."
echo "Wi-Fi will turn off automatically on next boot."
echo "Do not reboot unless you are ready for SSH over Wi-Fi to stop working."
