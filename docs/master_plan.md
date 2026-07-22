# blackjack-vision — Master Plan

## Pitch
A Raspberry Pi 5 device that watches a home blackjack table through a webcam and coaches the
player in real time: the mathematically correct action for every hand, a live Hi-Lo running/true
count, and eventually win probabilities — all on an HDMI screen beside the table, hands-free.

## Problem & Why
Cam wants to genuinely learn correct blackjack play (basic strategy + counting). Practicing with
real cards is the fun way, but checking a paper strategy chart after every hand is slow and
breaks the flow — and it's easy to *think* you played correctly when you didn't. A device that
silently watches and instantly shows the right play turns every dealt hand into a feedback rep.

## Target users & use cases
- **Primary:** Cam, at home, dealing real cards to himself to train.
  Top jobs: (1) "tell me the correct play instantly, hands-free", (2) "keep the count for me so
  I can check mine", (3) "show me the odds so I build intuition".
- **Secondary:** friends at a home game watching the screen "magically" read the cards.
- **Explicit non-goal:** any use inside a real casino. Using a device to aid play there is
  illegal in many jurisdictions. This is a training tool.

## v1 scope
**In:**
- Card detection using card-vision's pretrained YOLOv8 weights (no retraining).
- Fixed table zones: dealer's card in the top of frame, player's hand in the bottom.
- Debounced, stable card reading (a card must persist across frames; corner duplicates merged).
- Game rules in `config/rules.yaml` from day one (decks, S17/H17, DAS, payout, etc.).
- Basic-strategy engine, unit-tested against published charts for the configured rules.
- Hi-Lo running count + true count + simple bet hint; keyboard "new shoe" reset.
- Pygame fullscreen UI: live camera feed with detection boxes + big advice panel.
- Deployed on the Pi 5 (NCNN-exported model), verified with a live 20-hand session.

**Out of v1 (later stages):** win probability / per-action EV, full multi-hand game tracking,
on-screen settings editor (v1 config is file-only), touch input, sound.

## Future roadmap (6–12 months)
- **v2:** live win % and EV per action (simulation-validated), nicer UI polish.
- **v3:** full game tracker — multi-hand rounds, dealer draw-out, auto round transitions,
  session stats (accuracy vs. correct play over time), on-screen settings.
- **Maybe-later ideas:** Pi AI Kit (Hailo) acceleration, fine-tuned model on Cam's own cards,
  practice drills mode ("count this shoe", flashcard hands), phone-viewable session reports.

## Tech stack & key decisions
(Each decision's full rationale: see `docs/decisions.md`.)
- **Python** — 3.9 on the dev PC (system install, all deps support it — see D13),
  3.11 on the Pi (OS default). Code stays 3.9-compatible.
- **Ultralytics YOLOv8 + upstream `best.pt`** — proven ~90% mAP, 55 classes, MIT. [D1]
- **OpenCV** — webcam capture and frame handling. [D1]
- **Pygame fullscreen UI** — camera panel + advice panel + keyboard input, same code on PC and Pi. [D9]
- **NCNN export** for Pi inference; PyTorch only on the dev PC. [D8]
- **pytest** — engines are pure math; tests are the primary proof for them. [D10]
- **Fixed table zones** for dealer/player attribution. [D6]
- **`config/rules.yaml`** — rules configurable from day one, settings UI deferred. [D7]

## Architecture sketch
```
USB webcam
   │  frames (OpenCV)
   ▼
YOLOv8 inference (PyTorch on PC · NCNN on Pi)
   │  raw detections (55 classes, per corner)
   ▼
Detection post-processing
   • merge duplicate corners → one card
   • map card centre → zone (dealer / player)
   • debounce: card is "real" after N consecutive frames
   ▼
GameState (immutable snapshots)
   ├─► Strategy engine ──► advice (HIT/STAND/DOUBLE/SPLIT/SURRENDER)
   ├─► Count engine ─────► running count, true count, bet hint
   └─► (v2) EV engine ───► win %, EV per action
   ▼
Pygame UI  ◄── keyboard (new shoe, quit, pause)
   • left: camera feed + boxes   • right: advice panel
   ▲
config/rules.yaml (decks, S17/H17, DAS, payouts …)
```

## Staged roadmap
| Stage | Goal | Headline feature | Definition of done |
|---|---|---|---|
| 1. vision-foundation | Detector runs on Cam's PC + webcam | Stable zone-aware card reading | Dealt cards correctly identified into dealer/player zones, live, no flicker |
| 2. strategy-engine-ui | The brain and the face | Correct advice on screen | Engine passes chart tests for configured rules; live demo shows right action < 2 s |
| 3. card-counting | Track the shoe | Running + true count + bet hint | Count matches a manual count across a full 6-deck shoe on camera |
| 4. pi-deployment (**= v1**) | Runs where it lives | Boots into the app on the Pi | Cam's 20-hand live Pi session: correct advice < 2 s per detected hand, count accurate throughout |
| 5. win-probability | The wow math | Live win % + EV per action | Probabilities match simulation in tests; rendered live |
| 6. game-tracker | Whole-table awareness | Auto rounds + session stats + settings UI | A full session scored with zero keyboard input |

## Open questions & risks
1. **Pi 5 inference speed** — largely retired 2026-07-21: the weights are YOLOv8-nano and
   the NCNN export runs 71 ms/frame on the dev PC with identical detections; Pi 5 estimate
   ~200-350 ms, inside the 2 s budget. Confirm on-device in Stage 4. Fallback: Pi AI Kit.
2. **Real-world detection accuracy** — 90% mAP was on the author's setup. Cam's lighting,
   webcam, card design, and overlapping dealt cards are the real test (Stage 1 exists to
   prove this). Fallback: fine-tune on photos of Cam's cards.
3. **Webcam model & mount** — unknown model; needs a stable overhead-ish view (help.md #1).
4. **Two-corner dedupe** — the model detects card *corners*; one card can yield two boxes.
   Merging them correctly (esp. with overlapping cards) is Stage 1's hardest part.
5. **Split hands UX** — after a split there are two player hands in one zone; v1 may
   need a keyboard toggle. Revisit when Stage 2 starts.

## Glossary
- **Basic strategy** — the mathematically optimal action for each hand vs. dealer up-card, given rules.
- **Hi-Lo** — counting system: 2–6 = +1, 7–9 = 0, 10–A = −1.
- **Running count** — sum of Hi-Lo values of all cards seen since shuffle.
- **True count** — running count ÷ decks remaining; drives bet sizing.
- **S17/H17** — dealer stands/hits on soft 17. **DAS** — double after split allowed.
- **Zone** — a fixed region of the camera frame assigned to dealer or player.
- **Debounce** — requiring a detection to persist N frames before trusting it.
