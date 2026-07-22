# Stage 6 — Full Game Tracker  (sketch)

## Goal
Whole-table awareness and zero-keyboard sessions: automatic round transitions, dealer draw-out
tracking, multiple player hands (splits done properly), session statistics (Cam's accuracy vs
correct play over time), and the on-screen settings editor (rules finally editable without a
file).

## Features
- [x] Auto round detection (`src/tracker.py` RoundTracker) — table empties → round scored,
      no SPACE needed _(test-verified; live pending)_
- [x] Dealer draw-out + outcome scoring — WIN/LOSE/PUSH/BLACKJACK/UNSCORED from the final
      table _(test-verified; live pending)_
- [ ] Split-hand handling as first-class multi-hand state _(NOT built — the one remaining
      gap; the player zone is treated as a single hand)_
- [x] Session stats — hands, W/L/P, approximate advice-followed % (HIT/STAND inference
      only, documented) _(test-verified; live pending)_
- [x] Settings UI (`src/ui/settings.py`) — TAB opens rules editor, S saves with .bak backup,
      app hot-reloads rules + starts a new shoe _(save/step logic test-verified; on-screen
      flow needs a live session)_

## Definition of done
- [ ] A full session is dealt, scored, and summarized with zero keyboard input — LIVE.
      (`pytest tests/test_tracker.py` proves the logic; the table proves the feature.)

**Status 2026-07-21:** implemented ahead of schedule except split-hand state. Live
verification pending Cam's table sessions.
