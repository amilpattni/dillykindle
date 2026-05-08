#!/bin/bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PICO_CODE="$REPO_DIR/pico/code.py"
MOUNT_POINT="/mnt/circuitpy"

if [ ! -f "$PICO_CODE" ]; then
  echo "ERROR: Pico code not found at $PICO_CODE"
  exit 1
fi

if [ ! -e "/dev/disk/by-label/CIRCUITPY" ]; then
  echo "ERROR: CIRCUITPY drive not found."
  echo "Install CircuitPython on the Pico first, then plug it into this Pi."
  exit 1
fi

sudo umount "$MOUNT_POINT" 2>/dev/null || true
sudo mkdir -p "$MOUNT_POINT"
sudo mount -o uid=$(id -u),gid=$(id -g),umask=000 /dev/disk/by-label/CIRCUITPY "$MOUNT_POINT"

if [ ! -d "$HOME/pico-tools" ]; then
  python3 -m venv "$HOME/pico-tools"
fi

source "$HOME/pico-tools/bin/activate"
python -m pip install --upgrade pip
pip install --upgrade circup

circup --path "$MOUNT_POINT" install adafruit_hid

cp "$PICO_CODE" "$MOUNT_POINT/code.py"
sync

echo "Pico keyboard setup complete."
echo "Mapping:"
echo "GP15 -> w + Enter -> up"
echo "GP11 -> s + Enter -> down"
echo "GP7  -> e + Enter -> select"
echo "GP3  -> q + Enter -> back"
echo "GP16 -> x + Enter -> sleep/exit"
echo ""
echo "The Pico can stay plugged in. If it does not reload automatically, reboot the Pi."
