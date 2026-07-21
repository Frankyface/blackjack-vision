# Decision Log — blackjack-vision

Append-only. One entry per significant choice. Future sessions append; never rewrite history.

## 2026-07-21 — D1: Reuse cadyze/card-vision's pretrained YOLOv8 detector
**Chose:** Build on https://github.com/cadyze/card-vision — YOLOv8, 55 classes, pretrained
`best.pt` in-repo, MIT. · **Because:** ~90% mAP already achieved; zero training cost; corner-based
detection copes with overlap; MIT allows reuse with attribution. · **Rejected:** training our own
model (weeks of dataset work); classic CV template matching (fragile to lighting/rotation).
· **Revisit if:** real-table accuracy is poor after Stage 1 tuning → fine-tune on Cam's cards.

## 2026-07-21 — D2: Full feature vision, delivered in stages
**Chose:** Strategy advice → counting → EV/win% → full game tracker, as stages 2/3/5/6.
· **Because:** Cam wants all of it, but each layer depends on the previous being trusted.
· **Rejected:** building everything before first use (no feedback, high risk).
· **Revisit if:** never — staging is process, not scope reduction.

## 2026-07-21 — D3: Home practice trainer is the design target
**Chose:** Optimize for solo training at Cam's table; casino use is an explicit non-goal.
· **Because:** it's what Cam picked; also using such a device in a casino is illegal in many
jurisdictions. · **Rejected:** demo-gadget-first framing (polish over correctness).
· **Revisit if:** never for casino use; party-demo polish can ride along in stage 6.

## 2026-07-21 — D4: Camera = Cam's existing USB webcam
**Chose:** USB webcam (model TBC — help.md #1). · **Because:** already owned; upstream code
reads the first webcam via OpenCV unchanged. · **Rejected:** Pi Camera Module 3 (better mount,
but $35 + picamera2 code path). · **Revisit if:** webcam image quality caps detection accuracy.

## 2026-07-21 — D5: Display = small HDMI screen, keyboard controls
**Chose:** Cam's owned/soon-bought HDMI screen; controls via keyboard. · **Because:** on hand,
zero integration risk. · **Rejected:** Pi Touch Display 2 (cost, not owned); tiny OLED (can't
fit the advice panel). · **Revisit if:** hands-free control matters more later → GPIO buttons.

## 2026-07-21 — D6: Dealer/player attribution via fixed table zones
**Chose:** Top of frame = dealer, bottom = player; card centre decides. · **Because:** matches
real table layout; simple and reliable. · **Rejected:** dealing-order inference (fragile to
occlusion/misdeals); manual key-tagging (kills the hands-free magic).
· **Revisit if:** stage 6 multi-hand tracking needs more than two zones.

## 2026-07-21 — D7: Rules configurable from day one — via config file, not UI
**Chose:** `config/rules.yaml` (decks, S17/H17, DAS, resplit, surrender, payout) read by all
engines from the first commit; on-screen settings editor deferred to stage 6. · **Because:** Cam
wants configurability day one; a file delivers it without pre-building UI. Default shipped
config: 6-deck, H17, DAS, 3:2. · **Rejected:** hardcoding one rule set (Cam veto); settings UI
in v1 (delays the core). · **Revisit if:** Cam finds file-editing painful → pull UI forward.

## 2026-07-21 — D8: Develop on Windows PC, deploy to Pi via NCNN export
**Chose:** All dev/testing on Cam's PC (PyTorch); Stage 4 exports the model to NCNN for the
Pi 5. · **Because:** fast iteration; NCNN is Ultralytics' recommended fast path on Pi CPUs.
· **Rejected:** developing on the Pi over SSH (slow loop). · **Revisit if:** NCNN FPS is
unusable → Pi AI Kit (Hailo) or lower input resolution.

## 2026-07-21 — D9: UI = Pygame fullscreen
**Chose:** One Pygame app drawing camera feed + boxes (left) and advice panel (right), keyboard
input. · **Because:** identical on PC and Pi, trivial fullscreen kiosk, easy big typography;
camera-feed visibility builds trust and makes detection failures debuggable. · **Rejected:**
bare OpenCV window (ugly, poor text/layout); web kiosk in Chromium (more moving parts on Pi).
· **Revisit if:** stage 6 wants phone-viewable stats → add a tiny web export then.

## 2026-07-21 — D10: Verification = pytest for engines + live demo for CV/UI
**Chose:** Strategy/count/EV engines get real unit tests (80%+ coverage, charts as fixtures);
camera/UI features are proven by live webcam runs recorded in each feature's Verification Log.
· **Because:** engines are pure math (perfect for tests); CV needs real-world proof.
· **Rejected:** demo-only (regressions sneak in); test-only (CV can pass tests and fail live).
· **Revisit if:** never — this is the project's verification convention.

## 2026-07-21 — D11: Public GitHub repo `blackjack-vision`, MIT license
**Chose:** Public repo under Cam's account (Frankyface), MIT to match upstream, with
attribution to card-vision in README. · **Because:** Cam chose public (portfolio piece); MIT
keeps reuse clean. · **Rejected:** private repo. · **Revisit if:** never likely.

## 2026-07-21 — D12: Upstream model weights are downloaded, not committed
**Chose:** `models/*.pt` is gitignored; Stage 1 adds a documented download step/script that
fetches `best.pt` from the card-vision repo. · **Because:** keeps this repo lean; weights remain
canonical upstream; MIT permits use with attribution. · **Revisit if:** upstream repo
disappears → commit a copy (license allows) or mirror it.
