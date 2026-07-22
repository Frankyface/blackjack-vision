"""App settings loader (config/app.yaml). Game rules load via engines/rules.py."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

import yaml


class AppConfigError(ValueError):
    pass


@dataclass(frozen=True)
class AppConfig:
    camera_index: int = 0
    camera_width: int = 1280
    camera_height: int = 720
    model_path: str = "models/best.pt"
    confidence: float = 0.5
    imgsz: int = 960
    merge_dist_px: float = 140.0
    merge_scale: float = 4.0
    confirm_frames: int = 5
    forget_frames: int = 15
    zone_split: float = 0.45
    fullscreen: bool = False
    show_fps: bool = True
    bet_unit: int = 10
    bet_ramp: Dict[int, int] = field(default_factory=lambda: {1: 1, 2: 2, 3: 4, 4: 8, 5: 12})

    def __post_init__(self) -> None:
        if not 0.0 < self.zone_split < 1.0:
            raise AppConfigError(f"zones.split: must be between 0 and 1, got {self.zone_split}")
        if not 0.0 < self.confidence <= 1.0:
            raise AppConfigError(f"detection.confidence: must be in (0, 1], got {self.confidence}")
        if self.confirm_frames < 1 or self.forget_frames < 1:
            raise AppConfigError("detection.confirm_frames/forget_frames must be >= 1")
        if self.merge_dist_px <= 0:
            raise AppConfigError(
                f"detection.merge_dist_px: must be > 0 (0 would double-count every "
                f"card's two corners), got {self.merge_dist_px}")
        if self.merge_scale < 0:
            raise AppConfigError(
                f"detection.merge_scale: must be >= 0, got {self.merge_scale}")
        if not 320 <= self.imgsz <= 1920:
            raise AppConfigError(
                f"detection.imgsz: must be 320-1920, got {self.imgsz}")
        if self.camera_index < 0:
            raise AppConfigError(f"camera.index: must be >= 0, got {self.camera_index}")
        if self.camera_width <= 0 or self.camera_height <= 0:
            raise AppConfigError("camera.width/height must be positive")
        if self.bet_unit < 1:
            raise AppConfigError(f"counting.bet_unit: must be >= 1, got {self.bet_unit}")
        if not self.bet_ramp:
            raise AppConfigError("counting.bet_ramp must not be empty")


def load_app_config(path: "str | Path") -> AppConfig:
    p = Path(path)
    if not p.exists():
        raise AppConfigError(f"app config not found: {p}")
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise AppConfigError("app.yaml must be a YAML mapping")
    cam = raw.get("camera", {})
    det = raw.get("detection", {})
    zones = raw.get("zones", {})
    ui = raw.get("ui", {})
    counting = raw.get("counting", {})
    try:
        return AppConfig(
            camera_index=int(cam.get("index", 0)),
            camera_width=int(cam.get("width", 1280)),
            camera_height=int(cam.get("height", 720)),
            model_path=str(det.get("model_path", "models/best.pt")),
            confidence=float(det.get("confidence", 0.5)),
            imgsz=int(det.get("imgsz", 960)),
            merge_dist_px=float(det.get("merge_dist_px", 140.0)),
            merge_scale=float(det.get("merge_scale", 4.0)),
            confirm_frames=int(det.get("confirm_frames", 5)),
            forget_frames=int(det.get("forget_frames", 15)),
            zone_split=float(zones.get("split", 0.45)),
            fullscreen=bool(ui.get("fullscreen", False)),
            show_fps=bool(ui.get("show_fps", True)),
            bet_unit=int(counting.get("bet_unit", 10)),
            bet_ramp={int(k): int(v) for k, v in (counting.get("bet_ramp") or {1: 1}).items()},
        )
    except (TypeError, ValueError) as exc:
        if isinstance(exc, AppConfigError):
            raise
        raise AppConfigError(f"invalid app.yaml value: {exc}") from exc
