# Stage 3 — Card Counting

## Goal
Track every card that crosses the table across hands: Hi-Lo running count, true count (from
decks remaining), and a simple bet hint, with keyboard shoe control. At stage end the device
keeps an accurate count through a whole shoe.

## Features
- [x] `feature-hilo-engine.md` — pure counting engine (running/true count, decks remaining, bet hint) _(verified done)_
- [ ] `feature-shoe-session.md` — cards-seen ledger across hands, "new shoe" reset, count panel in the UI _(awaiting verification — live full-shoe count)_

## Definition of done (testable checklist)
- [ ] `pytest` green: Hi-Lo values, true-count division/rounding, decks-remaining estimate,
      bet ramp, reset behavior, and "same card seen twice in one hand isn't double-counted".
- [ ] Live full-shoe test (help.md #4): deal through 6 decks while keeping a manual count;
      device's running count matches the manual count at every ~1-deck checkpoint and at the end.
- [ ] N (new shoe) resets count and ledger; UI count panel shows running, true, decks left,
      and bet hint, updating within 2 s of a card landing.
- [ ] Both feature files `verified done` with log entries.

## Notes
Resolved design question: end-of-hand is BOTH manual (SPACE) and automatic (stage 6's
RoundTracker fires when the table stays empty). Double-count protection uses the
"returnable pool" ledger (docs/decisions.md D17): a card that left the felt this hand
absorbs the next identical ADDED as a return; leftovers at end-of-hand go stale and can
never recount. Chosen failure direction is undercounting — check for it in the live test.
