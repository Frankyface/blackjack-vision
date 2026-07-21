# Feature: Shoe session
_Stage: stage-3-card-counting · Status: not started_

## Goal
The ledger that connects hands into a shoe: every stable card that appears gets counted exactly
once, end-of-hand clears the table state without losing the count, N key starts a fresh shoe,
and the UI gains a count panel (running, true, decks left, bet hint).

## Success Criteria
- [ ] A card is counted once when it enters the stable set — never again during that hand
      (occlusion flicker, re-detection, etc.).
- [ ] End-of-hand (SPACE in v1) clears the table state; the ledger and count persist.
- [ ] N resets ledger + count with an on-screen confirmation moment (no accidental resets).
- [ ] Count panel visible alongside advice, updates within 2 s.
- [ ] Ledger logic unit-tested with synthetic multi-hand sequences.

## How We'll Verify
`pytest` for the ledger; then the Stage 3 exit test — a live full 6-deck shoe dealt on camera
against a manual count, matching at every ~1-deck checkpoint (procedure + card supply:
help.md #4). Record checkpoints in the log.

## Verification Log
_(empty)_

## Open Questions
- Cards mucked face-down (e.g. dealer's hole card never revealed in some flows): v1 assumption
  is all dealt cards end face-up on the table. Confirm with Cam's actual dealing style.

## Notes & Decisions
- none yet.
