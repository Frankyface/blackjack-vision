# Feature: Strategy engine
_Stage: stage-2-strategy-engine-ui · Status: not started_

## Goal
Pure function: (player hand, dealer up-card, Rules) → correct action (HIT / STAND / DOUBLE /
SPLIT / SURRENDER, with fallback action when double/surrender isn't available). The single
source of blackjack truth in the app.

## Success Criteria
- [ ] Handles hard totals, soft totals, and pairs, including multi-card hands (no double after
      3+ cards unless rules allow), soft-total degradation, and split availability.
- [ ] Chart fixtures: the complete published basic-strategy chart for 6-deck H17 DAS and
      6-deck S17 DAS encoded as test fixtures; the engine matches every cell (~340 cases
      per chart, zero tolerance).
- [ ] Rule sensitivity proven in tests: known divergent cells (e.g. A,7 v 2; 11 v A; 9,9 v 7)
      flip correctly between H17/S17 configs.
- [ ] No I/O, no globals, no mutation — pure and fast (<1 ms per decision).

## How We'll Verify
`pytest tests/test_strategy_engine.py` — every chart cell asserted. This feature is test-proven;
its live behavior is verified as part of `feature-advice-ui`. Chart source to encode from:
a reputable published basic strategy reference (e.g. Wizard of Odds charts), cited in the
fixture file header.

## Verification Log
_(empty)_

## Open Questions
- Surrender: default config has late_surrender off — chart fixtures must cover both settings
  or explicitly scope to the shipped configs.
- Deviations from basic strategy at extreme counts (Illustrious 18) — Stage 3+ question,
  out of scope here.

## Notes & Decisions
- none yet — revisit when starting.
