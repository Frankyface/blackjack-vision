# Feature: Kiosk boot
_Stage: stage-4-pi-deployment · Status: not started_

## Goal
Appliance behavior: plug the Pi in, the app comes up fullscreen and detecting — no desktop,
no mouse, no login interaction.

## Success Criteria
- [ ] Systemd service (or equivalent) starts the app on boot, fullscreen on the HDMI screen.
- [ ] Survives a hard power cycle: unplug → replug → app live within a measured boot time.
- [ ] App crash auto-restarts the service (test by killing the process).
- [ ] Clean shutdown path exists (ESC exits app; documented `sudo shutdown` habit noted for Cam).

## How We'll Verify
Live on the Pi: power-cycle test ×2 with boot-to-detecting time recorded; `kill` the app process
and watch it return. Record in the log.

## Verification Log
_(empty)_

## Open Questions
- Light detail by design — flesh out at Stage 3 completion (autologin + cage/labwc kiosk vs
  systemd user service on Pi OS Bookworm).

## Notes & Decisions
- none yet.
