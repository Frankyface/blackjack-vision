# Feature: Advice UI
_Stage: stage-2-strategy-engine-ui · Status: awaiting verification_

## Goal
The Pygame fullscreen dashboard: live camera feed with detection boxes and zone line on the
left; a big, glanceable advice panel on the right (action word, player total, dealer up-card).
Keyboard: quit, pause, and a "clear hand / next deal" key until auto-round-detection exists
(Stage 6).

## Success Criteria
- [ ] Fullscreen at the display's native resolution; readable from across a table (action word
      is the largest element on screen).
- [ ] Advice updates within 2 s of the stable card set changing.
- [ ] Shows a distinct "waiting" state when no/partial hand is detected (no stale advice).
- [ ] Keyboard controls work: ESC quits cleanly, SPACE clears the current hand, P pauses.
- [ ] Runs windowed on the PC via a config/flag for development.

## How We'll Verify
Live PC demo (this is the Stage 2 exit demo): deal 10 hands, check each shown action against a
printed chart, time advice latency on a few hands, exercise every key. Record hands, actions,
timings, and any wrong/late advice in the log.

## Verification Log
**2026-07-21 (Claude):** `src/ui/dashboard.py` — camera feed + boxes + zone line left,
giant action word / hands / count / EV bars / stats right; keys ESC·SPACE·N(confirm)·
P·TAB; windowed via app.yaml `ui.fullscreen: false`. Rendered headless in `--selftest`
(3 frames, exit 0) and live windowed for 10 s with the real camera + detector
(`--run-seconds 10`, UI loop ~10.1 fps, exited cleanly). The 10-hand live chart-check
demo — the stage exit test — pending Cam at the table. "Waiting" state (…) shown when
no/partial hand; advice latency will be timed in the live demo.

## Open Questions
- Split hands display: two hands in the player zone after a split — how does v1 show which one
  is active? (Candidate: advise left hand first, SPACE advances. Decide at the live demo;
  currently the zone's cards are treated as ONE hand.)
- Camera feed at what resolution in the UI vs. inference resolution? (currently: native
  camera res for both; revisit if Pi FPS needs a smaller inference size)

## Notes & Decisions
- none yet — revisit when starting.
