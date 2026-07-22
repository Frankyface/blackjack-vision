"""Stable card reading: corner dedupe + temporal debounce.

Turns noisy per-frame YOLO detections into a trustworthy "cards on the table"
set. The tracker itself is stateful (it must remember frames); everything it
returns is an immutable snapshot, and the clustering helpers are pure.

Pipeline per frame:
  1. Cluster same-(card, zone) boxes by distance — two nearby boxes are the two
     corners of ONE physical card; far-apart boxes are genuinely two cards
     (possible in a multi-deck shoe).
  2. Debounce over time — an instance must persist `confirm_frames` consecutive
     frames to be confirmed; a confirmed instance survives `forget_frames`
     missed frames (occlusion) before being dropped.
"""
from __future__ import annotations

import enum
import math
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Sequence, Tuple

from .cards import Card
from .zones import Zone

Box = Tuple[float, float, float, float]  # x1, y1, x2, y2


@dataclass(frozen=True)
class RawDetection:
    card: Card
    zone: Zone
    box: Box
    confidence: float


class EventKind(enum.Enum):
    ADDED = "ADDED"
    REMOVED = "REMOVED"


@dataclass(frozen=True)
class CardEvent:
    kind: EventKind
    card: Card
    zone: Zone
    instance: int  # permanent per-(card, zone) instance id; ADDED/REMOVED pair up


@dataclass(frozen=True)
class StableState:
    """Immutable snapshot: confirmed cards per zone + this update's events."""
    counts: Mapping[Tuple[Card, Zone], int]
    events: Tuple[CardEvent, ...]

    def cards(self, zone: Zone) -> Tuple[Card, ...]:
        out: List[Card] = []
        for (c, z), n in sorted(self.counts.items(), key=lambda kv: str(kv[0][0])):
            if z is zone:
                out.extend([c] * n)
        return tuple(out)

    @property
    def total_cards(self) -> int:
        return sum(self.counts.values())


def _center(box: Box) -> Tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def _dist(a: Box, b: Box) -> float:
    (ax, ay), (bx, by) = _center(a), _center(b)
    return math.hypot(ax - bx, ay - by)


def cluster_boxes(boxes: Sequence[Box], merge_dist: float) -> List[List[int]]:
    """Greedy single-link clustering of box indices by centre distance.

    Pure helper. Boxes closer than merge_dist end up in one cluster (corners of
    the same card); anything further apart stays separate.
    """
    clusters: List[List[int]] = []
    for i in range(len(boxes)):
        placed = False
        for cluster in clusters:
            if any(_dist(boxes[i], boxes[j]) <= merge_dist for j in cluster):
                cluster.append(i)
                placed = True
                break
        if not placed:
            clusters.append([i])
    # Single-link fixup: merge clusters that became connected transitively.
    merged = True
    while merged:
        merged = False
        for a in range(len(clusters)):
            for b in range(a + 1, len(clusters)):
                if any(
                    _dist(boxes[i], boxes[j]) <= merge_dist
                    for i in clusters[a]
                    for j in clusters[b]
                ):
                    clusters[a].extend(clusters[b])
                    del clusters[b]
                    merged = True
                    break
            if merged:
                break
    return clusters


def count_instances(
    detections: Sequence[RawDetection], merge_dist: float
) -> Dict[Tuple[Card, Zone], int]:
    """Pure: frame detections -> how many physical copies of each (card, zone)."""
    grouped: Dict[Tuple[Card, Zone], List[Box]] = {}
    for d in detections:
        grouped.setdefault((d.card, d.zone), []).append(d.box)
    return {
        key: len(cluster_boxes(boxes, merge_dist))
        for key, boxes in grouped.items()
    }


@dataclass
class _InstanceTrack:
    uid: int  # permanent per-(card, zone) instance id — never renumbered
    seen_streak: int = 0
    missed: int = 0
    confirmed: bool = False


class StableTracker:
    """Feed one frame's detections at a time; read back confirmed state."""

    def __init__(
        self,
        confirm_frames: int = 5,
        forget_frames: int = 15,
        merge_dist: float = 140.0,
    ) -> None:
        if confirm_frames < 1 or forget_frames < 1:
            raise ValueError("confirm_frames and forget_frames must be >= 1")
        self._confirm = confirm_frames
        self._forget = forget_frames
        self._merge_dist = merge_dist
        self._tracks: Dict[Tuple[Card, Zone], List[_InstanceTrack]] = {}
        self._next_uid: Dict[Tuple[Card, Zone], int] = {}

    def update(self, detections: Sequence[RawDetection]) -> StableState:
        observed = count_instances(detections, self._merge_dist)
        events: List[CardEvent] = []

        keys = set(self._tracks) | set(observed)
        for key in keys:
            tracks = self._tracks.setdefault(key, [])
            seen_n = observed.get(key, 0)
            # Grow track list to cover every observed instance.
            while len(tracks) < seen_n:
                uid = self._next_uid.get(key, 1)
                self._next_uid[key] = uid + 1
                tracks.append(_InstanceTrack(uid=uid))

            for idx, track in enumerate(tracks):
                if idx < seen_n:  # this instance was seen this frame
                    track.seen_streak += 1
                    track.missed = 0
                    if not track.confirmed and track.seen_streak >= self._confirm:
                        track.confirmed = True
                        events.append(
                            CardEvent(EventKind.ADDED, key[0], key[1], track.uid)
                        )
                else:  # not seen this frame
                    track.missed += 1
                    track.seen_streak = 0

            # Drop instances gone too long (confirmed) or never confirmed.
            kept: List[_InstanceTrack] = []
            for track in tracks:
                if track.confirmed and track.missed > self._forget:
                    events.append(
                        CardEvent(EventKind.REMOVED, key[0], key[1], track.uid)
                    )
                elif not track.confirmed and track.missed > 0:
                    continue  # unconfirmed flicker — silently forget
                else:
                    kept.append(track)
            if kept:
                self._tracks[key] = kept
            else:
                del self._tracks[key]

        counts = {
            key: sum(1 for t in tracks if t.confirmed)
            for key, tracks in self._tracks.items()
            if any(t.confirmed for t in tracks)
        }
        return StableState(counts=counts, events=tuple(events))

    def reset(self) -> None:
        """Forget the table (end of hand / new shoe). Count state lives elsewhere."""
        self._tracks.clear()
        self._next_uid.clear()
