#!/bin/bash
set -euo pipefail

REPO_DIR="/home/amil/dillykindle"

sudo systemctl stop dillykindle.service 2>/dev/null || true
sudo nmcli radio wifi off 2>/dev/null || true

cd "$REPO_DIR"
source "$REPO_DIR/.venv/bin/activate"

python -m scripts.show_shutdown_screen || true

sleep 2

sudo /usr/sbin/shutdown now
