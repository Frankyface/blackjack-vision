# Failed Approaches — blackjack-vision

Append-only graveyard of dead ends. Every entry: what was tried, root cause of failure, and the
working direction if known. Never prune this file. `handoff.md`'s "Watch Out" section links here
instead of carrying full stories.

## 2026-07-21 — Upstream demo GIF as an offline detector test asset
**Why it failed:** `repo-images/header-vid.gif` in cadyze/card-vision is a 400×57 banner
strip, GIF-palette-compressed, with the author's detection labels baked in. Our model finds
nothing in it, even 5× upscaled at conf 0.3 — the source pixels are simply gone.
**Do instead:** use `card-vision-model-output/val_batch0_labels.jpg` (real validation
photos, downloaded to `captures/`) — our detector reads QD/8S/8D from it correctly. For
anything better, photograph Cam's actual cards.
