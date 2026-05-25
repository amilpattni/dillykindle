#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
source .venv/bin/activate

# Give the Pico/serial device a few seconds to appear on boot.
sleep 4

python -m app.epaper.main
