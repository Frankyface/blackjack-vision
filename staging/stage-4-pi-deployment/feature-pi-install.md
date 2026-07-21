# Feature: Pi install
_Stage: stage-4-pi-deployment · Status: not started_

## Goal
The app running on the Pi 5: NCNN-exported model, documented install (or script) over SSH,
webcam + HDMI working, performance measured against the ≤ 2 s advice budget.

## Success Criteria
- [ ] Model exported to NCNN; inference on the Pi uses it (PyTorch not required on the Pi).
- [ ] Repeatable install steps scripted/documented from a fresh clone on the Pi.
- [ ] Measured on the Pi: inference FPS and advice latency (target ≤ 2 s) recorded in the log.
- [ ] Detection accuracy sanity check on the Pi matches PC behavior (same 5-card spot check).

## How We'll Verify
Run the documented install on the Pi over SSH, then the same 5-card + 3-hand live check from
Stage 1/2, timing latency. Record numbers in the log. Prereqs: help.md #2, #3.

## Verification Log
_(empty)_

## Open Questions
- Light detail by design — flesh out at Stage 3 completion (NCNN export flags, Pi OS
  Wayland/X11 for pygame fullscreen, camera USB quirks).

## Notes & Decisions
- Fallbacks if too slow, in order: lower inference resolution → frame-skip (infer every Nth
  frame) → Pi AI Kit (Hailo ~$70, goes to help.md if needed).
