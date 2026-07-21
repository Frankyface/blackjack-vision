# blackjack-vision

A Raspberry Pi 5 blackjack trainer. A webcam watches real cards on the table; a YOLOv8 model
reads them; an HDMI screen shows the mathematically correct play, the Hi-Lo running/true count,
and (eventually) live win probabilities. Deal, glance, learn.

**Status:** early development — see `handoff.md` for the current state.

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
