# Feature: v1 acceptance session
_Stage: stage-4-pi-deployment · Status: not started_

## Goal
The v1 finish line, exactly as agreed at planning: a real 20-hand session at Cam's table on the
finished device, proving the whole promise end-to-end.

## Success Criteria
- [ ] Cam deals a 20-hand blackjack session at his table; only the device's keyboard keys
      (SPACE end-of-hand, N new shoe) are used — no other intervention.
- [ ] Every correctly-detected hand shows the correct basic-strategy action within 2 s
      (Cam checks against a printed chart during/after).
- [ ] Running/true count is accurate for the whole session vs. Cam's manual count.
- [ ] Detection failures (missed/misread cards) are tallied honestly; session notes name the
      conditions (lighting, angle) for future improvement. Target: ≥ 18/20 hands fully
      auto-detected.

## How We'll Verify
This feature IS a verification procedure — run the session with Cam, record per-hand results
(hand, dealer card, shown action, correct?, latency feel, count checkpoints) in the log.
It requires Cam at the table; Claude prepares a session checklist beforehand.

## Verification Log
_(empty)_

## Open Questions
- none yet — revisit when Stage 4 starts.

## Notes & Decisions
- Passing this feature = v1 shipped. Celebrate accordingly.
