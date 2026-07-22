# help.md — things only Cam can do

Ordered checklist of human-only tasks. Each item: what, why, and which stage it blocks.
Sessions add items here whenever they hit a wall only Cam can clear.

- [ ] **1. Point the webcam at your table (stable overhead-ish mount).**
  Why: detection accuracy depends heavily on view angle, focus, and stability. A cheap clamp
  arm / gooseneck phone-holder style mount over the table works well.
  Status: your webcam WORKS (verified 2026-07-21: opens at 1280×720, ~8 fps) — it's
  currently pointed at the room. Once it faces cards, run `python -m src.app` and we do the
  Stage 1 live checks together (`/verify`).
  Blocks: Stage 1/2/3 live verification (all code is ready and waiting).

- [ ] **2. Confirm the HDMI screen for the Pi (own it? which size?).**
  Why: the UI layout (font sizes, panel split) should be designed for the real resolution.
  Blocks: Stage 4 (Pi deployment). Stage 2 UI can be built on the PC monitor meanwhile.

- [ ] **3. Make the Pi 5 reachable for deployment: power it on, connect it to your network,
  enable SSH, and note its IP / hostname.**
  Why: Stage 4 installs and tests over SSH from the PC.
  Blocks: Stage 4.

- [ ] **4. Have a real 6-deck shoe's worth of cards (or at least 2+ decks) for count testing.**
  Why: Stage 3's definition of done is a full-shoe count check against a manual count.
  Blocks: Stage 3 verification. (Single-deck testing works for development before then.)
