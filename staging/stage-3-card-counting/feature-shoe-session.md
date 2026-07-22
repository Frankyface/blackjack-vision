# Feature: Shoe session
_Stage: stage-3-card-counting · Status: awaiting verification_

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
**2026-07-21 (Claude):** `src/session.py` — "returnable pool" ledger (docs/decisions.md
D17) over StableTracker events; SPACE end-of-hand, N-with-confirm new shoe, count panel
in the dashboard; also tracks per-rank composition for the EV engine. Redesigned after
adversarial review reproduced two count-corruption bugs in the first (instance-keyed)
design: SPACE with cards on the felt recounted them, and zone-boundary flicker counted
one card twice — both now covered by regression tests. `pytest tests/test_session.py` +
`tests/test_session_composition.py` → 18 tests green including a scripted full 312-card
/ 6-deck shoe ending at running count 0. The Stage 3 exit test — a LIVE full shoe on
camera vs Cam's manual count with ~1-deck checkpoints (help.md #4) — still pending.

## Open Questions
- Cards mucked face-down (e.g. dealer's hole card never revealed in some flows): v1 assumption
  is all dealt cards end face-up on the table. Confirm with Cam's actual dealing style.

## Notes & Decisions
- none yet.
