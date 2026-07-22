# Stage 1 — Vision Foundation

## Goal
Prove the borrowed detector on Cam's actual hardware and table, and turn its raw, flickery,
per-frame output into a stable, zone-aware stream of "these cards are on the table" facts that
the blackjack engines (Stage 2+) can trust.

## Features
- [x] `feature-run-card-vision-locally.md` — upstream YOLOv8 detector running on Cam's PC + webcam _(verified done — 32 distinct cards live)_
- [x] `feature-table-zones.md` — dealer/player zone mapping with visual overlay _(verified done — live, incl. straddle fix)_
- [x] `feature-stable-card-reading.md` — corner dedupe + debounce → stable card set _(verified done — live, incl. merge_scale fix)_

**STAGE COMPLETE 2026-07-21** — live-verified at Cam's table (four sessions, ~5 min,
32 distinct cards, zero misreads on first placement; two live-found bugs fixed with
regression tests). Evidence: the feature Verification Logs + captures/live_*.jpg.

## Definition of done (testable checklist)
- [x] `python -m src.app` opens a live window showing the webcam feed with detection boxes.
- [x] Cards from Cam's actual deck, on his table, under his lighting, are identified with the
      correct rank+suit (spot-check ≥ 20 different cards; ≥ 18 read correctly on first placement).
      → 32 distinct cards, 32 correct (2026-07-21 live sessions).
- [x] The frame shows a visible zone boundary; a card placed top-of-frame reports as DEALER,
      bottom-of-frame as PLAYER, verified live for ≥ 5 cards each.
- [x] A dealt card appears in the stable card set exactly once (no corner duplicates, no
      flicker in/out across 10 seconds of observation), and disappears when removed.
      → verified live after the merge_scale fix; 18+ s flicker-free stretches observed.
- [x] Unit tests exist and pass for the pure logic: corner dedupe, zone mapping, debounce
      state machine (`pytest` green — 197 tests).
- [x] All three feature files are `verified done` with Verification Log entries.
