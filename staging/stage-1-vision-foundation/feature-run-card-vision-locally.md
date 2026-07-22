# Feature: Run card-vision locally
_Stage: stage-1-vision-foundation · Status: awaiting verification_

## Goal
Get the upstream cadyze/card-vision YOLOv8 detector running on Cam's Windows PC against his USB
webcam, inside this repo's own structure (venv, `requirements.txt`, `src/`), so every later
feature builds on a working detection loop we control.

## Success Criteria
- [x] A documented, repeatable setup exists: `python -m venv`, `pip install -r requirements.txt`,
      one script/command to download `best.pt` from the upstream repo into `models/`.
- [x] Running the app opens Cam's webcam and displays live video with YOLOv8 detection boxes
      and class labels (rank+suit) drawn on detected cards.
- [ ] A real card held in frame is detected with its correct class label, live.
      **← the only open item: needs Cam's webcam pointed at cards (help.md #1)**
- [x] Achieved FPS on the PC is measured and recorded in the Verification Log (baseline for
      the Stage 4 Pi comparison).

## How We'll Verify
1. Fresh terminal in the project root: create venv, `pip install -r requirements.txt`,
   run the model-download step. All three complete without error.
2. Run `python -m src.app`. Expect: window opens with live webcam feed.
3. Place 5 known cards in frame one at a time (e.g. A♠, K♥, 7♦, 10♣, 2♠). Expect: each gets a
   box + the correct label. Record which were right/wrong.
4. Note the FPS printed by the app over ~30 s of running.
5. Record all results (including misreads) in the Verification Log below.
   Needs Cam (or his webcam pointed at the table) — see help.md #1.

## Verification Log
**2026-07-21 (Claude, PC-side evidence — live card check still pending):**
- venv (Python 3.9.13) + `pip install -r requirements.txt` exit 0; `dill` added to
  requirements (checkpoint needs it to unpickle).
- `best.pt` downloaded via the documented URL: 6,270,489 bytes → it's YOLOv8-nano.
  Class names inspected: `10C…AS` compact format + `BACK`/`BLACK JOKER`/`RED JOKER`
  (all handled by `src/cards.py`, jokers/backs ignored).
- `python -m src.app --selftest` → exit 0 (model loads, blank-frame = 0 detections,
  engines + UI render headless).
- `python -m src.app --camera-test` → webcam opens 1280×720, 26 frames in 3.3 s
  (7.8 fps capture); frame saved to captures/camera_test.jpg (points at a room, no cards).
- Real-card imagery check: detector run on upstream validation mosaic
  (captures/val_batch0_labels.jpg) → QD conf 0.72, 8S 0.53, 8D 0.52 — correct labels.
- `python -m src.app --run-seconds 10` (real window, live camera) → ran and exited
  cleanly, UI loop ~10.1 fps on the PC. **PC baseline for Stage 4.**
- Live "card in frame reads correctly" NOT yet run — camera isn't at the table.

## Open Questions
- ~~Which exact ultralytics/torch versions?~~ Resolved: ultralytics 8.4.104,
  torch 2.8.0+cpu, ncnn 1.0.20260526, pnnx 20260526 work on the PC (Python 3.9).
- ~~Upstream main.py or own loop?~~ Resolved: own loop (src/detector.py + src/app.py);
  only the weights are reused.
- Webcam resolution/FPS sweet spot for detection vs. speed? (revisit at the live table test)

## Notes & Decisions
- Weights are downloaded, not committed (docs/decisions.md D12). Raw GitHub URL for the file:
  `https://github.com/cadyze/card-vision/raw/main/card-vision-model-output/weights/best.pt`
  (verify at implementation time).
