# Feature: Pi install
_Stage: stage-4-pi-deployment · Status: awaiting verification_

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
**2026-07-21 (Claude, PC-side evidence — on-Pi run pending):**
- `deploy/export_ncnn.py` executed on the PC → `models/best_ncnn_model/` produced
  (model.ncnn.bin 12.2 MB); ultralytics auto-installed ncnn 1.0.20260526 + pnnx.
- NCNN model loaded through the same `CardDetector` API and run on the real-card
  validation mosaic: detections IDENTICAL to the .pt (QD 0.72, 8S 0.53, 8D 0.52);
  71 ms/frame steady-state on the PC (Ryzen 7 2700X). Pi 5 estimate ~200-350 ms/frame —
  comfortably inside the ≤2 s advice budget.
- `deploy/install_pi.sh` + kiosk service written; NOT yet executed on the Pi
  (blocked: help.md #2 screen, #3 SSH access).

## Open Questions
- Pi OS Wayland vs X11 for pygame fullscreen — resolve during the on-Pi install.
- Webcam USB behavior on the Pi (bandwidth, index) — resolve on-Pi.

## Notes & Decisions
- Fallbacks if too slow, in order: lower inference resolution → frame-skip (infer every Nth
  frame) → Pi AI Kit (Hailo ~$70, goes to help.md if needed).
