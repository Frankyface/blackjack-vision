"""Run the card detector on an image / GIF frame and print what it sees.

Usage: python scripts/detect_image.py <path> [frame_index]
Saves an annotated copy next to the input as <name>_detected.jpg.
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import load_app_config  # noqa: E402
from src.detector import CardDetector  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = Path(sys.argv[1])
    frame_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    if path.suffix.lower() == ".gif":
        cap = cv2.VideoCapture(str(path))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        cap.release()
        if not ok:
            print(f"could not read frame {frame_index} from {path}")
            return 1
    else:
        frame = cv2.imread(str(path))
        if frame is None:
            print(f"could not read image {path}")
            return 1

    cfg = load_app_config(ROOT / "config" / "app.yaml")
    detector = CardDetector(str(ROOT / cfg.model_path), cfg.confidence, cfg.zone_split)
    detections = detector.detect(frame)

    print(f"{path.name} frame {frame_index}: {len(detections)} detections")
    for d in sorted(detections, key=lambda d: -d.confidence):
        print(f"  {d.card}  conf={d.confidence:.2f}  zone={d.zone.value}  box={tuple(int(v) for v in d.box)}")

    for d in detections:
        x1, y1, x2, y2 = (int(v) for v in d.box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (80, 220, 120), 2)
        cv2.putText(frame, str(d.card), (x1, max(y1 - 6, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 220, 120), 2)
    out = path.with_name(path.stem + "_detected.jpg")
    cv2.imwrite(str(out), frame)
    print(f"annotated: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
