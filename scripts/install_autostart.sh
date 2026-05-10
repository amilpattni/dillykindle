#!/bin/bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
USER_NAME="$(whoami)"

sudo usermod -aG dialout "$USER_NAME"

sudo tee /etc/systemd/system/dillykindle.service > /dev/null <<EOF
[Unit]
Description=DillyKindle e-paper reader
After=multi-user.target
Wants=multi-user.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$REPO_DIR
ExecStart=$REPO_DIR/run_epaper.sh
Restart=on-failure
RestartSec=5
StandardInput=null
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable dillykindle.service

echo "DillyKindle autostart installed."
echo "Reboot to test:"
echo "sudo reboot"
