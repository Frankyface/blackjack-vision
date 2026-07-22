# Stage 5 — Win Probability / EV

## Goal
The "wow" math: live win % for the current hand and expected value per available action,
shown in the UI alongside the advice.

## Features
- [x] EV engine (`src/engines/ev.py`) — recursive dealer-outcome computation +
      stand/hit/double/split/surrender EVs, composition-aware via the Stage 3 ledger
      (`ShoeSession.remaining_composition()`); no-dealer-BJ conditioning for 10/A up-cards;
      split modeled as 2× one post-split hand. _(test-verified; live display pending)_
- [ ] Probability UI — EV bars + win % render in the dashboard panel (implemented; needs the
      live table demo to be called verified).

## Definition of done
- [x] EV outputs validated in tests: dealer distributions sum to 1 and land in the classic
      published windows for every up-card; EV-optimal action matches basic strategy on 15
      clear-cut cells under BOTH H17 and S17; 16v10 reproduces the razor-thin ≈−0.54 pair;
      composition shifts move EV the right way (`pytest tests/test_ev.py`, 66 tests green).
- [ ] Live on the Pi without breaking the ≤ 2 s advice budget (EV cached per table state;
      measure during Stage 4's on-Pi session).

**Status 2026-07-21:** implemented ahead of schedule alongside the core build (the engine is
pure math with no dependency on stages 1-4 hardware). Live verification rides with the
Stage 4 acceptance session.
