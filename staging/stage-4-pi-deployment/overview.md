# Stage 4 — Pi Deployment (= v1 complete)

## Goal
Move the working PC app onto the Raspberry Pi 5 with acceptable speed, boot straight into it,
and pass the v1 acceptance session at Cam's real table.

## Features
- [ ] `feature-pi-install.md` — NCNN model export + install + run on the Pi (perf measured)
- [ ] `feature-kiosk-boot.md` — Pi powers on → app fullscreen, no desktop interaction
- [ ] `feature-v1-acceptance.md` — the 20-hand live acceptance session

## Definition of done (testable checklist)
- [ ] App runs on the Pi 5 with the HDMI screen + webcam; inference via NCNN export.
- [ ] Advice latency ≤ 2 s from last card landing, measured on the Pi.
- [ ] Power-cycle test: unplug → replug → app is fullscreen and detecting without keyboard/mouse.
- [ ] **v1 acceptance (Cam's session):** 20 hands dealt at the real table — every correctly-
      detected hand gets the correct action ≤ 2 s; running/true count accurate all session
      (vs. Cam's manual count); misdetections noted honestly in the log.
- [ ] All three feature files `verified done` with log entries.

## Notes
Light detail by design — flesh out when Stage 3 nears completion. Known risks to plan around
then: NCNN FPS on Pi CPU (fallback: lower inference resolution → Pi AI Kit), pygame under
Wayland vs X11 on Pi OS Bookworm, webcam USB bandwidth on the Pi. Prereqs: help.md #2 (screen)
and #3 (SSH access).
