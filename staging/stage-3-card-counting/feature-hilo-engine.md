# Feature: Hi-Lo engine
_Stage: stage-3-card-counting · Status: not started_

## Goal
Pure counting engine: fold a stream of seen cards into running count, true count (running ÷
decks remaining, from `rules.yaml` deck count minus cards seen), and a bet hint from a simple
configurable ramp.

## Success Criteria
- [ ] Correct Hi-Lo values (2–6:+1 · 7–9:0 · 10/J/Q/K/A:−1); immutable fold (state in → new state out).
- [ ] True count uses decks remaining to the half-deck, with the standard floor rounding.
- [ ] Bet hint from a config ramp (e.g. TC ≤ 1: min bet … TC ≥ 5: max), edges tested.
- [ ] Full unit test suite; no I/O.

## How We'll Verify
`pytest tests/test_hilo.py` — including a scripted full-shoe sequence with known checkpoint
counts. Live proof happens in `feature-shoe-session`.

## Verification Log
_(empty)_

## Open Questions
- none yet — revisit when starting (Stage 3 details firm up at Stage 2 completion).

## Notes & Decisions
- none yet.
