#!/bin/bash

cd "$(dirname "$0")/.."

echo "Setting up DillyPie..."

sudo apt update
sudo apt install -y python3 python3-venv python3-pip python3-tk

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

echo "DillyPie setup complete."
echo "Run with: ./scripts/dillypie.sh"
