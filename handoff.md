# Handoff — blackjack-vision
_Last updated: 2026-07-21 · Current stage: stage-1-vision-foundation (live verification)_

## 🎯 Goals
All six stages are CODED and unit-tested (183 tests green). The project is now in
verification mode: prove the pipeline on Cam's real table, then deploy to the Pi.

## 📍 Current State
- Full app works on the PC: `python -m src.app` → camera + boxes + advice + count + EV
  + auto-round stats + TAB settings. 10 s live windowed run OK (~10 fps loop).
- Verified: engines (strategy chart 100% both rule sets, Hi-Lo, EV vs benchmarks),
  broken-config fail-fast, NCNN export produces IDENTICAL detections at 71 ms/frame (PC).
- Detector proven on real card imagery (upstream validation photos) — NOT yet on Cam's
  own cards/lighting.
- Pi untouched (blocked: help.md #2 screen, #3 SSH). Split hands not modeled (stage 6 gap).

## 📂 Files I'm Working On
- None mid-edit. Next work happens live at the table, then on the Pi.

## ✅ Things I've Changed
- 2026-07-21: Implemented ALL stages: vision pipeline, strategy+rules, counting+session,
  EV engine, tracker+stats+settings UI, Pi deploy artifacts; 183 tests; NCNN validated.
- 2026-07-21: Scaffolded full doc system, staged roadmap, slash commands; git + GitHub.

## ❌ Watch Out
- Upstream demo GIF is useless as a test asset → see docs/failed-approaches.md; use
  captures/val_batch0_labels.jpg for offline detector checks.
- Dev venv is Python 3.9 (system) — keep code 3.9-compatible; Pi runs 3.11.
- models/ is gitignored — fresh clones run scripts/fetch_model.py (+ deploy/export_ncnn.py).

## ➡️ Next Up
1. Cam: mount the webcam over the table (help.md #1) → run the Stage 1 live checks
   (20-card spot check, zone line, occlusion) and log results via /verify.
2. Then the Stage 2 exit demo: 10 hands vs a printed chart, < 2 s advice.
3. Then Pi install (help.md #2, #3) → `bash deploy/install_pi.sh` → kiosk → v1 acceptance.

## 🔗 Pointer
→ Current stage folder: `staging/stage-1-vision-foundation/` ·
Active feature file: `staging/stage-1-vision-foundation/feature-run-card-vision-locally.md`
