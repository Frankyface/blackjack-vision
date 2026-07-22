# help.md — things only Cam can do

Ordered checklist of human-only tasks. Each item: what, why, and which stage it blocks.
Sessions add items here whenever they hit a wall only Cam can clear.

- [x] **1. Point the webcam at your table.** DONE 2026-07-21 — desk mount works; Stage 1
  live-verified (32 distinct cards read correctly). Note for later sessions: cards read
  best when their corner index faces the camera; avoid parking cards exactly on the
  gold zone line.

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
