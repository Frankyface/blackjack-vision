# blackjack-vision

A blackjack trainer that watches real cards through a camera. A YOLOv8 model reads them;
the screen shows the mathematically correct play, the Hi-Lo running/true count, and live
win probabilities. Deal, glance, learn.

**▶ Try it in your browser: https://frankyface.github.io/blackjack-vision/** — detection
runs entirely client-side (ONNX Runtime Web); nothing leaves your machine. The full
version (EV panel, session stats, kiosk mode) runs on a PC or Raspberry Pi 5 below.

**Status:** fully implemented and unit-tested (183 tests); live table verification and the
Raspberry Pi install are in progress — see `handoff.md` for the current state.

## Quick start (PC)
```
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # (bin/ on Linux)
.venv/Scripts/python scripts/fetch_model.py     # downloads the card-vision weights
.venv/Scripts/python -m src.app                 # ESC quit · SPACE end hand · N new shoe · TAB rules
```
For the Raspberry Pi 5: `bash deploy/install_pi.sh`, then see `deploy/blackjack-vision.service`.

## How it works
Webcam frames → YOLOv8 card detection → zone mapping (dealer's card top of frame, player's hand
bottom) → debounced game state → strategy + counting engines → Pygame fullscreen dashboard
(live camera view with detection boxes + big advice panel). Game rules (decks, S17/H17, DAS,
payouts) are configurable in `config/rules.yaml`.

## Hardware
Raspberry Pi 5 · USB webcam on an overhead mount · any HDMI display · keyboard for the few
controls (new shoe, pause, quit). Development happens on a PC; the model runs via NCNN on the Pi.

## Credits
Card detection builds on [cadyze/card-vision](https://github.com/cadyze/card-vision) (MIT) —
a YOLOv8 playing-card detector (55 classes, corner-based detection). The pretrained weights
are downloaded from that repo rather than committed here.

## Legal note
This is a **home practice tool**. Using any device to aid play inside a real casino is illegal
in many jurisdictions. Don't.

## License
MIT — see `LICENSE`.
