"""Dealer/player zone mapping. Pure — no I/O."""
from __future__ import annotations

import enum


class Zone(enum.Enum):
    DEALER = "DEALER"
    PLAYER = "PLAYER"


def assign_zone(center_y: float, frame_height: float, split: float) -> Zone:
    """A detection whose box centre sits above the split line is the dealer's.

    split is a fraction of frame height (0..1). Exactly on the line counts as
    PLAYER (the line visually belongs to the player side).
    """
    if frame_height <= 0:
        raise ValueError(f"frame_height must be positive, got {frame_height}")
    if not 0.0 < split < 1.0:
        raise ValueError(f"zone split must be between 0 and 1, got {split}")
    return Zone.DEALER if center_y < split * frame_height else Zone.PLAYER
