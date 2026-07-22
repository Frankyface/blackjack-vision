# Card-detection model research — 2026-07-21

Deep search (GitHub / Hugging Face / Roboflow Universe, all claims verified against
actual files) for a pretrained replacement for cadyze/card-vision. **Verdict: keep the
current model; fix misreads with higher-resolution inference (done — imgsz 960) and,
if ever needed, a fine-tune with in-domain frames.**

## Why no swap
- **mustafakemal0146/playing-cards-yolov8** (HF, MIT, real 6 MB YOLOv8n,
  `resolve/main/playing_cards_model_0_playing-cards-colab.pt`): the only genuine
  drop-in candidate. Trained on the 10k-image Augmented Startups synthetic set — same
  paradigm as ours, but publishes ZERO metrics. Unmeasured lateral move; A/B before
  ever adopting.
- **TeogopK/Playing-Cards-Object-Detection**: best public dataset (20k synthetic, CC0)
  but only ~52 MB YOLOv8m weights (too slow for Pi 5) and the repo has NO license.
  Harvest the dataset, not the weights.
- **noorkhokhar99** (YOLOv8s, 22.5 MB): no license, no metrics — rejected.
- **RF100 poker-cards-cxcvz**: 1,285 REAL angled photos (CC BY 4.0) — too small to
  train alone; the best real-world supplement for a fine-tune. Odd class names (10T/1D)
  need remapping.
- **geaxgx/playing-card-detection** (MIT, 440★): the standard synthetic-scene
  generator — use it to manufacture angled/overlapping training data from OUR deck.

## The fine-tune recipe (if resolution + hygiene ever stop being enough)
Fresh YOLOv8n/YOLO11n on: TeogopK 20k (CC0) + Augmented Startups 10k + RF100 1.3k real
+ **a few hundred labeled frames from Cam's actual webcam** (the highest-leverage part —
our misreads are a train/serve domain gap). Normalize class names to "10C" style.

## What we did instead (measured, 2026-07-21, live table)
A/B on 30 identical frames of the failing layout (8C misread as 8C+9C, covered 5H):
| imgsz | result | ms/frame (PC) |
|---|---|---|
| 640 | 8C + phantom 9C, 5H missed, 7C missed | 72 |
| **960** | **exact true table: 5H, 7C, 8C** | 128 |
| 1280 | same, higher conf, nothing new | 212 |
→ `detection.imgsz: 960` is the default. Re-measure the cost on the Pi during Stage 4;
drop toward 800/640 there only if latency demands it.
