#!/bin/bash

cd "$(dirname "$0")/.."

echo "Setting up DillyPie..."

sudo apt update
sudo apt install -y python3 python3-venv python3-pip python3-tk

ARCH=$(uname -m)

if [[ "$ARCH" == "armv7l" || "$ARCH" == "aarch64" ]]; then
    echo "Raspberry Pi detected. Installing PyMuPDF through apt..."
    sudo apt install -y python3-pymupdf python3-fitz

    if [ -d ".venv" ]; then
        rm -rf .venv
    fi

    python3 -m venv .venv --system-site-packages
    source .venv/bin/activate

    pip install --upgrade pip
    pip install customtkinter pillow
else
    echo "Non-Pi system detected. Installing from requirements.txt..."

    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi

    source .venv/bin/activate

    pip install --upgrade pip
    pip install -r requirements.txt
fi

echo "DillyPie setup complete."
echo "Run with: ./scripts/dillypie.sh"
