# Feature: Table zones
_Stage: stage-1-vision-foundation · Status: awaiting verification_

## Goal
Split the camera frame into a DEALER zone (top) and PLAYER zone (bottom) so every detected card
is attributed to the right hand, with the boundary visible on screen so Cam can arrange his
table to match.

## Success Criteria
- [ ] The live view draws the zone boundary line and labels the two regions.
- [ ] Every detected card is tagged DEALER or PLAYER based on its box centre, shown in its label.
- [ ] The boundary position is configurable (e.g. `zone_split: 0.45` in a config file), not
      hardcoded, and a change to the config visibly moves the line.
- [ ] Pure zone-mapping logic (box → zone) has unit tests covering: clearly-top, clearly-bottom,
      straddling the line, and a moved boundary.

## How We'll Verify
1. `pytest tests/test_zones.py` — all green.
2. Run the app. Place one card top-of-frame, one bottom-of-frame: labels read DEALER / PLAYER
   respectively.
3. Slide a card slowly across the boundary: tag flips exactly when its centre crosses the line.
4. Edit the config value, restart, confirm the line moved. Record results in the log.

## Verification Log
**2026-07-21 (Claude):** Implemented `src/zones.py` (pure) + boundary/labels drawn in the
UI camera panel; split configurable as `zones.split` in config/app.yaml. `pytest
tests/test_zones.py` → 7 tests green (top/bottom/on-line/moved-boundary/validation).
Live steps 2-4 (cards straddling the line on camera, config change visibly moving the
line) pending Cam's table session.

## Open Questions
- Is a straight horizontal line enough, or does Cam's camera angle need a tilted/curved
  boundary? (Start straight; revisit after first live test.)

## Notes & Decisions
- Zone config lives beside the rules in `config/` (likely `config/app.yaml` — camera + zones +
  UI settings; `config/rules.yaml` stays purely game rules).
