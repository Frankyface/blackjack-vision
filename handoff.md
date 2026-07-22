# Handoff — blackjack-vision
_Last updated: 2026-07-22 · Current stage: stage-2-strategy-engine-ui (live demo) + web app shipped_

## 🎯 Goals
Stage 1 DONE (live-verified). NEW: browser version live at
https://frankyface.github.io/blackjack-vision/ (D19 — same model in ONNX Runtime Web,
chart JSON generated from the Python engine). Next: Stage 2 exit demo (10 hands vs a
printed chart, desktop or web), Stage 3 live shoe count, Pi deployment.

## 📍 Current State
- STAGE 1 COMPLETE: 32 distinct cards read correctly live (4 sessions, ~5 min, ~10 fps);
  zones, overlap, occlusion all verified. Two live-found bugs fixed + regression-tested
  (close-range corner split → merge_scale; zone-line straddle → zone-blind clustering).
- Cam used the TAB settings screen live: rules.yaml now decks: 1 (his single physical
  deck) — settings save/hot-reload verified. Chart is still the 4-8 deck table (warned).
- 197 tests green. Engines + NCNN export verified earlier. Pi still untouched.
- Known imperfection: rare transient misread (one phantom QC, ~1 s, in 5 min) — debounce
  + ledger contained it to one stray count.

## 📂 Files I'm Working On
- None mid-edit.

## ✅ Things I've Changed
- 2026-07-22: Web app built + deployed to GitHub Pages (D19); overlay-alignment and
  resolution-scaled merge fixes from Cam's live browser test.
- 2026-07-21: Detection quality campaign (D18): imgsz 960 A/B, phantom decay, agnostic
  NMS, deck copy cap, model research (docs/model-research-2026-07.md); ow27d-nano
  downloaded but A/B vs best.pt NOT yet run (camera got moved).
- 2026-07-21: LIVE Stage 1 verification; merge_scale + straddle fixes; 201 tests.
- 2026-07-21: Implemented ALL stages; adversarial review, 15 findings fixed.

## ❌ Watch Out
- rules.yaml is USER STATE (settings screen rewrites it) — never assert its contents in
  tests; decks currently 1.
- Cards read best index-toward-camera; avoid parking a card exactly on the zone line.
- Dev venv Python 3.9; keep code 3.9-compatible (Pi runs 3.11).

## ➡️ Next Up
1. Stage 2 exit demo: deal 10 hands (1 dealer card up, 2+ player cards), Cam checks each
   on-screen action vs a printed chart, time-to-advice < 2 s → log in feature-advice-ui.
2. Unfinished: A/B models/ow27d-nano.pt vs best.pt on live frames (scratchpad ab_models.py
   pattern) — decide default; web/assets/best.onnx must match whatever wins.
3. Stage 3 exit: full-shoe live count vs manual count (needs multi-deck shoe, help.md #4).
4. Pi install (help.md #2/#3): `bash deploy/install_pi.sh` → kiosk → v1 acceptance.

## 🔗 Pointer
→ Current stage folder: `staging/stage-2-strategy-engine-ui/` ·
Active feature file: `staging/stage-2-strategy-engine-ui/feature-advice-ui.md`
