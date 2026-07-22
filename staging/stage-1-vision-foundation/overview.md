# Stage 1 — Vision Foundation

## Goal
Prove the borrowed detector on Cam's actual hardware and table, and turn its raw, flickery,
per-frame output into a stable, zone-aware stream of "these cards are on the table" facts that
the blackjack engines (Stage 2+) can trust.

## Features
- [ ] `feature-run-card-vision-locally.md` — upstream YOLOv8 detector running on Cam's PC + webcam _(awaiting verification — live card check)_
- [ ] `feature-table-zones.md` — dealer/player zone mapping with visual overlay _(awaiting verification — live boundary check)_
- [ ] `feature-stable-card-reading.md` — corner dedupe + debounce → stable card set _(awaiting verification — live occlusion check)_

**Status 2026-07-21:** all code + unit tests done and green; every remaining checklist item
below needs Cam's webcam pointed at real cards on his table (help.md #1).

## Definition of done (testable checklist)
- [ ] `python -m src.app` opens a live window showing the webcam feed with detection boxes.
- [ ] Cards from Cam's actual deck, on his table, under his lighting, are identified with the
      correct rank+suit (spot-check ≥ 20 different cards; ≥ 18 read correctly on first placement).
- [ ] The frame shows a visible zone boundary; a card placed top-of-frame reports as DEALER,
      bottom-of-frame as PLAYER, verified live for ≥ 5 cards each.
- [ ] A dealt card appears in the stable card set exactly once (no corner duplicates, no
      flicker in/out across 10 seconds of observation), and disappears when removed.
- [ ] Unit tests exist and pass for the pure logic: corner dedupe, zone mapping, debounce
      state machine (`pytest` green).
- [ ] All three feature files are `verified done` with Verification Log entries.
