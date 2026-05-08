#!/bin/bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PICO_BOOT="$REPO_DIR/pico/boot.py"
PICO_CODE="$REPO_DIR/pico/code.py"
MOUNT_POINT="/mnt/circuitpy"

if [ ! -f "$PICO_BOOT" ] || [ ! -f "$PICO_CODE" ]; then
  echo "ERROR: Pico files not found in repo."
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

cp "$PICO_BOOT" "$MOUNT_POINT/boot.py"
cp "$PICO_CODE" "$MOUNT_POINT/code.py"

sync

echo "Pico serial controller setup complete."
echo "Mapping:"
echo "GP15 -> UP"
echo "GP11 -> DOWN"
echo "GP7  -> SELECT"
echo "GP3  -> BACK"
echo "GP16 -> POWER"
echo ""
echo "Reboot the Pi once after first setup so the Pico re-enumerates with serial data enabled."
