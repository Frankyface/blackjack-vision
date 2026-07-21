# Handoff — blackjack-vision
_Last updated: 2026-07-21 · Current stage: stage-1-vision-foundation_

## 🎯 Goals
Get cadyze/card-vision's YOLOv8 detector running on Cam's Windows PC with his USB webcam,
then make its output zone-aware and stable enough to drive a blackjack engine.

## 📍 Current State
- Project scaffolded 2026-07-21; no application code exists yet.
- Upstream repo confirmed: pretrained weights at `card-vision-model-output/weights/best.pt`,
  MIT license, detects 55 classes via card corners (~90% mAP on author's setup).
- Hardware on hand: Pi 5 (set up), USB webcam (model TBC). HDMI screen owned/being bought.
- Nothing is verified working yet.

## 📂 Files I'm Working On
- None yet — first code lands with the active feature below.

## ✅ Things I've Changed
- 2026-07-21: Scaffolded full doc system, staged roadmap, slash commands; git + GitHub set up.

## ❌ Watch Out
- Upstream weights are NOT committed here (see .gitignore) — Stage 1 downloads them from
  the card-vision repo; keep attribution in README.

## ➡️ Next Up
1. Start `feature-run-card-vision-locally`: create venv, install deps (ultralytics, opencv-python),
   download `best.pt` from upstream, run live detection against Cam's webcam.
2. Ask Cam to point the webcam at cards on his table for the live check (see help.md #1).

## 🔗 Pointer
→ Current stage folder: `staging/stage-1-vision-foundation/` ·
Active feature file: `staging/stage-1-vision-foundation/feature-run-card-vision-locally.md`
