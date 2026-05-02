#!/bin/bash

cd "$(dirname "$0")/.."

echo "Updating dillykindle..."
git pull

echo "Update complete."
echo "Rebooting so the fullscreen app restarts..."
sudo reboot
