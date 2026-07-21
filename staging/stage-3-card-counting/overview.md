# Stage 3 — Card Counting

## Goal
Track every card that crosses the table across hands: Hi-Lo running count, true count (from
decks remaining), and a simple bet hint, with keyboard shoe control. At stage end the device
keeps an accurate count through a whole shoe.

## Features
- [ ] `feature-hilo-engine.md` — pure counting engine (running/true count, decks remaining, bet hint)
- [ ] `feature-shoe-session.md` — cards-seen ledger across hands, "new shoe" reset, count panel in the UI

## Definition of done (testable checklist)
- [ ] `pytest` green: Hi-Lo values, true-count division/rounding, decks-remaining estimate,
      bet ramp, reset behavior, and "same card seen twice in one hand isn't double-counted".
- [ ] Live full-shoe test (help.md #4): deal through 6 decks while keeping a manual count;
      device's running count matches the manual count at every ~1-deck checkpoint and at the end.
- [ ] N (new shoe) resets count and ledger; UI count panel shows running, true, decks left,
      and bet hint, updating within 2 s of a card landing.
- [ ] Both feature files `verified done` with log entries.

## Notes
Moderate detail by design (progressive elaboration) — flesh out the feature files when Stage 2
nears completion. Known design question to resolve then: how the ledger infers "this hand
ended" so cards leaving the table aren't re-counted next hand (likely: SPACE keypress from the
UI marks end-of-hand in v1; automatic in Stage 6).
