#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

sudo apt update
sudo apt install -y \
  git \
  python3-full \
  python3-venv \
  python3-pip \
  python3-pil \
  python3-pil.imagetk \
  python3-numpy \
  python3-fitz \
  python3-spidev \
  python3-gpiozero \
  python3-lgpio

if [ ! -d "waveshare_epd" ]; then
  tmp_dir="$(mktemp -d)"
  git clone --depth 1 https://github.com/waveshareteam/e-Paper.git "$tmp_dir/e-Paper"
  cp -r "$tmp_dir/e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd" ./waveshare_epd
  rm -rf "$tmp_dir"
fi

rm -rf .venv
python3 -m venv --system-site-packages .venv
source .venv/bin/activate

python -m pip install --upgrade pip

if [ -s requirements-pi.txt ]; then
  pip install -r requirements-pi.txt
fi

python - <<'PY'
import fitz
from PIL import Image
from waveshare_epd import epd7in5_V2
print("Pi Lite setup good")
PY
