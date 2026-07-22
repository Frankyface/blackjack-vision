# Feature: Stable card reading
_Stage: stage-1-vision-foundation · Status: awaiting verification_

## Goal
Turn noisy per-frame YOLO detections into a trustworthy "cards currently on the table" set:
merge the two corner detections of a single card, ignore one-frame flickers, and only
add/remove cards from the game state when the evidence is persistent. This is the foundation
every engine depends on — a phantom card would corrupt advice AND the count.

## Success Criteria
- [ ] One physical card never appears twice in the stable set (its two detected corners are
      merged; two *different* physical cards of the same rank+suit in different zones still
      count separately).
- [ ] A card must persist for N consecutive frames (configurable, default ~5) before it enters
      the stable set; a detection gap shorter than M frames doesn't remove a known card.
- [ ] The stable set survives a hand being partially occluded for a moment (e.g. Cam's hand
      passing over the table) without dropping or re-adding cards.
- [ ] The debounce/dedupe state machine is pure logic with unit tests: appear, flicker,
      disappear, occlusion gap, two-corner merge, same-card-both-zones.
- [ ] The UI shows the *stable* set (not raw detections) as the card list per zone.

## How We'll Verify
1. `pytest tests/test_stable_reading.py` — green, covering the scenarios above with synthetic
   detection sequences.
2. Live: deal a 2-card hand + dealer card. Watch the on-screen stable list for 10 s: exactly
   3 entries, no flicker.
3. Wave a hand over the table for ~1 s: stable list unchanged.
4. Remove a card: it leaves the stable list within ~2 s.
5. Record all outcomes (with any failures) in the log.

## Open Questions
- Best corner-merge heuristic: IoU/distance between boxes of the same class within a zone?
  Two corners of one card are near each other; same class far apart = genuinely two cards.
  Tune with real footage.
- Does the model ever misread one corner as a different card than the other corner? If so,
  majority/confidence vote is needed. Check with real footage.

## Verification Log
**2026-07-21 (Claude):** Implemented `src/stable.py` — greedy single-link corner
clustering + per-instance debounce (confirm 5 / forget 15 frames, configurable). `pytest
tests/test_stable_reading.py` → 12 tests green: two-corner merge, transitive chains,
same card in both zones, two far-apart copies, flicker rejection, occlusion survival,
removal after forget, second-instance ADDED events, reset. UI shows the stable set (not
raw detections). Live steps 2-4 (real 3-card hand steady 10 s, hand-wave occlusion,
removal timing) pending Cam's table session. Behavior note: after a REMOVED, a re-add of
the same (card, zone, instance) within one hand does NOT recount — safer against double
counting; recorded for the live test to confirm it feels right.

## Notes & Decisions
- none yet — revisit when starting.
