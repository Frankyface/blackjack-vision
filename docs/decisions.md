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

## 2026-07-21 — D13: Dev environment is the system Python 3.9
**Chose:** Build the PC venv on the machine's Python 3.9.13 and keep all code
3.9-compatible (string-quoted `str | Path` annotations, no match statements).
· **Because:** it's what's installed; every dependency (ultralytics 8.4, torch 2.8 CPU,
pygame 2.6) supports it; the Pi independently runs its own 3.11. · **Rejected:**
installing Python 3.11 on the PC (system change for zero functional gain).
· **Revisit if:** a dependency drops 3.9 support.

## 2026-07-21 — D14: EV engine = current-composition recursion with documented approximations
**Chose:** Per-action EV via exact recursion over dealer outcomes and player hit states,
with (a) draw probabilities FIXED at the current shoe composition, (b) no-dealer-BJ
conditioning for 10/A up-cards, (c) split EV = 2× one post-split hand (no resplits,
split aces get one card), (d) surrender = exactly −0.5. · **Because:** milliseconds-fast,
composition-aware (uses the ledger), reproduces published numbers (dealer distributions
in classic windows; EV-optimal matches the chart on all 30 tested clear cells; 16v10 ≈
−0.54/−0.54). · **Rejected:** Monte Carlo (noisy, slower, harder to test); full
without-replacement recursion (state space explodes, negligible accuracy gain for a
trainer). · **Revisit if:** EV numbers ever get used for real bet-sizing decisions beyond
the display.

## 2026-07-21 — D15: Auto-round detection + approximate advice-accuracy inference
**Chose:** A round ends when the table stays empty for N consecutive updates
(RoundTracker); outcome scored from the last full table seen. Advice-followed stats infer
only HIT/STAND decisions (card count grew / round ended), excluding double/split.
· **Because:** zero-keyboard sessions with honest, testable semantics; partial inference
beats pretending we can see chips. · **Rejected:** requiring SPACE every hand (still
works as a manual override); full action inference (can't distinguish double from hit
by card count alone). · **Revisit if:** stage-6 split handling lands — revisit both.

## 2026-07-21 — D16: Settings screen writes rules.yaml from a template with a .bak backup
**Chose:** TAB opens an on-device rules editor; S saves via a documented template
(comments preserved by regeneration), previous file kept as rules.yaml.bak, app
hot-reloads rules and starts a new shoe. · **Because:** Cam wanted rules configurable
without file editing eventually; regenerating from a template keeps the file readable
since PyYAML drops comments. · **Rejected:** ruamel.yaml round-tripping (extra dependency
for one file). · **Revisit if:** app.yaml wants the same treatment.

## 2026-07-21 — D17: Count ledger uses a "returnable pool", not instance keys
**Chose:** ShoeSession counts an ADDED card unless an identical card left the felt earlier
in the same hand (then it's a return/relocation, not counted); cards still on the felt at
end-of-hand become "stale" so their later removal can't open a recount window. Ambiguity
resolves toward NOT counting. StableTracker events carry permanent per-(card,zone)
instance ids (ADDED/REMOVED pair up; ids never reused). · **Because:** adversarial review
reproduced two count-corruption bugs in the key-based design (SPACE with cards on the
felt recounted them; zone-boundary flicker double-counted) and found instance renumbering
broke the event contract. The pool design fixes all three with one mechanism and
testable semantics. · **Rejected:** carrying (card,zone,instance) key-sets across hands
(fragile against renumbering); trusting instance identity across zones (tracker can't
provide it). · **Revisit if:** live shoe tests show systematic UNDERcounting — the
chosen failure direction.

## 2026-07-21 — D18: Keep cadyze/card-vision; fix misreads with imgsz 960 + hygiene
**Chose:** Stay on the current model. Raise inference resolution to 960 (measured A/B on
the live failing layout: 640 double-read the 8C and missed two cards; 960 read the exact
true table at 128 ms/frame PC). Layered detection hygiene added the same day: class-
agnostic NMS, phantom decay-healing, deck-count copy cap, zone-blind corner clustering.
· **Because:** an Opus research sweep (docs/model-research-2026-07.md) found no public
model verifiably better — the only drop-in nano publishes no metrics; better-documented
models are Pi-hostile mediums or unlicensed. · **Rejected:** unmeasured model swap;
immediate fine-tune (recipe documented for later). · **Revisit if:** misreads persist at
960 after the fanning convention (indexes visible) — then execute the fine-tune recipe
with frames from Cam's webcam.
