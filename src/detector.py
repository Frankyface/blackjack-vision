"""YOLO detection wrapper: frame in -> RawDetection list out.

Ultralytics is imported lazily so the pure-logic test suite never pays the
torch import cost. Works with both the .pt weights (PC) and an exported
NCNN model directory (Pi) — ultralytics loads either from the same API.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Sequence

from .cards import parse_class_name
from .stable import RawDetection
from .zones import assign_zone


class CardDetector:
    def __init__(self, model_path: str, confidence: float, zone_split: float,
                 imgsz: int = 960) -> None:
        if not Path(model_path).exists():
            raise FileNotFoundError(
                f"model not found: {model_path} — run scripts/fetch_model.py first"
            )
        from ultralytics import YOLO  # lazy: heavy import

        self._model = YOLO(model_path)
        self._confidence = confidence
        self._zone_split = zone_split
        self._imgsz = imgsz
        self._names = self._model.names

    def detect(self, frame) -> List[RawDetection]:
        """Run inference on one BGR frame (numpy array)."""
        results = self._model.predict(
            frame, conf=self._confidence, verbose=False,
            agnostic_nms=True,  # one corner patch = one label, never two classes
            imgsz=self._imgsz,  # corner indexes are tiny — don't shrink them away
        )
        detections: List[RawDetection] = []
        frame_height = frame.shape[0]
        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                name = self._names[int(box.cls[0])]
                card = parse_class_name(name)
                if card is None:  # jokers, card backs, junk
                    continue
                x1, y1, x2, y2 = (float(v) for v in box.xyxy[0])
                center_y = (y1 + y2) / 2.0
                detections.append(
                    RawDetection(
                        card=card,
                        zone=assign_zone(center_y, frame_height, self._zone_split),
                        box=(x1, y1, x2, y2),
                        confidence=float(box.conf[0]),
                    )
                )
        return detections
