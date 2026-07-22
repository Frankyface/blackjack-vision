"""Export models/best.pt to NCNN for fast CPU inference on the Raspberry Pi 5.

Run on the dev PC (or the Pi): python deploy/export_ncnn.py
Produces models/best_ncnn_model/ — copy the whole directory to the Pi and set
config/app.yaml detection.model_path to it. Ultralytics loads NCNN exports
through the same YOLO() API, so no code changes are needed.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = ROOT / "models" / "best.pt"


def main() -> int:
    if not WEIGHTS.exists():
        print(f"weights not found: {WEIGHTS} — run scripts/fetch_model.py first")
        return 1
    from ultralytics import YOLO

    model = YOLO(str(WEIGHTS))
    out = model.export(format="ncnn", imgsz=640)
    print(f"exported: {out}")
    print("point config/app.yaml detection.model_path at this directory on the Pi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
