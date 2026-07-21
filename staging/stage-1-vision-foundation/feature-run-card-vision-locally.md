# Feature: Run card-vision locally
_Stage: stage-1-vision-foundation · Status: not started_

## Goal
Get the upstream cadyze/card-vision YOLOv8 detector running on Cam's Windows PC against his USB
webcam, inside this repo's own structure (venv, `requirements.txt`, `src/`), so every later
feature builds on a working detection loop we control.

## Success Criteria
- [ ] A documented, repeatable setup exists: `python -m venv`, `pip install -r requirements.txt`,
      one script/command to download `best.pt` from the upstream repo into `models/`.
- [ ] Running the app opens Cam's webcam and displays live video with YOLOv8 detection boxes
      and class labels (rank+suit) drawn on detected cards.
- [ ] A real card held in frame is detected with its correct class label, live.
- [ ] Achieved FPS on the PC is measured and recorded in the Verification Log (baseline for
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
_(empty — a feature with an empty log can never be `verified done`)_

## Open Questions
- Which exact ultralytics/torch versions? Pin what works on the PC; Pi compatibility gets its
  own pass in Stage 4.
- Does the upstream `main.py` logic transfer as-is, or do we only take the weights and write our
  own loop? (Leaning: own loop — it's ~30 lines with the ultralytics API and we need custom
  post-processing anyway.)
- Webcam resolution/FPS sweet spot for detection vs. speed?

## Notes & Decisions
- Weights are downloaded, not committed (docs/decisions.md D12). Raw GitHub URL for the file:
  `https://github.com/cadyze/card-vision/raw/main/card-vision-model-output/weights/best.pt`
  (verify at implementation time).
