# Feature: Advice UI
_Stage: stage-2-strategy-engine-ui · Status: not started_

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
_(empty)_

## Open Questions
- Split hands display: two hands in the player zone after a split — how does v1 show which one
  is active? (Candidate: advise left hand first, SPACE advances. Decide when building.)
- Camera feed at what resolution in the UI vs. inference resolution?

## Notes & Decisions
- none yet — revisit when starting.
