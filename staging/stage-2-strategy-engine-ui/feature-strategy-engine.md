# Feature: Strategy engine
_Stage: stage-2-strategy-engine-ui · Status: verified done_

## Goal
Pure function: (player hand, dealer up-card, Rules) → correct action (HIT / STAND / DOUBLE /
SPLIT / SURRENDER, with fallback action when double/surrender isn't available). The single
source of blackjack truth in the app.

## Success Criteria
- [x] Handles hard totals, soft totals, and pairs, including multi-card hands (no double after
      3+ cards unless rules allow), soft-total degradation, and split availability.
- [x] Chart fixtures: the complete published basic-strategy chart for 6-deck H17 DAS and
      6-deck S17 DAS encoded as test fixtures; the engine matches every cell (~340 cases
      per chart, zero tolerance).
- [x] Rule sensitivity proven in tests: known divergent cells (e.g. A,7 v 2; 11 v A; 9,9 v 7)
      flip correctly between H17/S17 configs.
- [x] No I/O, no globals, no mutation — pure and fast (<1 ms per decision).

## How We'll Verify
`pytest tests/test_strategy_engine.py` — every chart cell asserted. This feature is test-proven;
its live behavior is verified as part of `feature-advice-ui`. Chart source to encode from:
a reputable published basic strategy reference (e.g. Wizard of Odds charts), cited in the
fixture file header.

## Verification Log
**2026-07-21 (Claude):** `src/engines/strategy.py` — composite-code chart tables
(H/S/Dh/Ds/P/Ph/Rh/Rs/Rp) for 4-8 deck H17 and S17, resolved against availability
(2-card double, DAS, LS, resplit-aces, double_restrictions). `pytest
tests/test_strategy_engine.py` → 44 tests green covering the FULL hard/soft/pair grids
for both rule sets (13+8+10 rows × 10 up-cards each), explicit H17/S17 divergent cells,
10 surrender cells, 3-card fallbacks, 10-J mixed pair, post-split DAS/aces, can_split
override. Fixture source: Wizard of Odds 4-8 deck charts (cited in the test header).
Measured 5.7 µs per decision (timeit, 30k calls) — well under 1 ms. One bug found and
fixed during RED→GREEN: `Ph` cells ignored the DAS flag (caught by the borderline-split
test). Live behavior rides with feature-advice-ui. → verified done

## Open Questions
- Surrender: default config has late_surrender off — chart fixtures must cover both settings
  or explicitly scope to the shipped configs.
- Deviations from basic strategy at extreme counts (Illustrious 18) — Stage 3+ question,
  out of scope here.

## Notes & Decisions
- none yet — revisit when starting.
