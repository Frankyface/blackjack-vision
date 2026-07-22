#!/usr/bin/env bash
# Install blackjack-vision on a Raspberry Pi 5 (Raspberry Pi OS Bookworm 64-bit).
# Run from the repo root on the Pi:  bash deploy/install_pi.sh
set -euo pipefail

echo "== blackjack-vision Pi install =="

# System packages: SDL for pygame, libgl for opencv, venv tooling.
sudo apt-get update
sudo apt-get install -y python3-venv python3-dev libgl1 libsdl2-2.0-0 \
  libsdl2-image-2.0-0 libsdl2-ttf-2.0-0 libatlas-base-dev

# Project venv.
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip
# CPU-only torch keeps the install small; ultralytics needs it to LOAD .pt.
# With the NCNN export, torch is only needed at export time — but installing it
# once keeps scripts/fetch_model.py + deploy/export_ncnn.py usable on the Pi.
./.venv/bin/pip install -r requirements.txt

# Model: fetch weights, export to NCNN for fast CPU inference.
./.venv/bin/python scripts/fetch_model.py
./.venv/bin/python deploy/export_ncnn.py

echo ""
echo "Now point config/app.yaml at the NCNN model:"
echo "  detection:"
echo "    model_path: models/best_ncnn_model"
echo ""
echo "Test run:        ./.venv/bin/python -m src.app --selftest"
echo "Live run:        ./.venv/bin/python -m src.app --fullscreen"
echo "Kiosk service:   see comments in deploy/blackjack-vision.service"
