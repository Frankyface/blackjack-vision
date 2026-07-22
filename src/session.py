"""Shoe session ledger: counts every physical card exactly once.

Design (see docs/decisions.md D17): the ledger doesn't trust instance numbers.
- An ADDED card is counted UNLESS an identical card left the table earlier in
  this hand (then it's treated as that card returning — a pickup put back down,
  or a card that flickered across the zone boundary — and is not recounted).
- A REMOVED card that was counted THIS hand joins that "returnable" pool.
- Cards still on the felt when a hand ends stay known (`_stale`): their later
  removal does NOT make them returnable in the next hand, so a genuinely new
  identical card next hand still counts.
Ambiguous cases resolve toward NOT counting — undercounting one card is safer
for the count than double-counting one.
"""
from __future__ import annotations

from typing import Dict, Tuple

from .cards import Card
from .engines.ev import full_composition
from .engines.hilo import CountState
from .stable import CardEvent, EventKind


def _rank_bucket(card: Card) -> str:
    return "10" if card.is_ten_valued else card.rank


class ShoeSession:
    def __init__(self, decks: int) -> None:
        self._decks = decks
        self._count = CountState(decks=decks)
        self._seen_by_rank: Dict[str, int] = {}
        self._hands_played = 0
        self._counted_this_hand = 0
        self._returnable: Dict[Card, int] = {}  # counted, then left the felt, this hand
        self._stale: Dict[Card, int] = {}       # on the felt but counted in a PRIOR hand
        self._active: Dict[Card, int] = {}      # currently confirmed on the felt

    @property
    def count(self) -> CountState:
        return self._count

    @property
    def hands_played(self) -> int:
        return self._hands_played

    def apply_events(self, events: Tuple[CardEvent, ...]) -> None:
        for event in events:
            card = event.card
            if event.kind is EventKind.ADDED:
                if self._returnable.get(card, 0) > 0:
                    self._returnable[card] -= 1  # a counted card came back
                    self._track_active(card, +1)
                    continue
                self._track_active(card, +1)
                self._count = self._count.see(card)
                bucket = _rank_bucket(card)
                self._seen_by_rank[bucket] = self._seen_by_rank.get(bucket, 0) + 1
                self._counted_this_hand += 1
            elif event.kind is EventKind.REMOVED:
                self._track_active(card, -1)
                if self._stale.get(card, 0) > 0:
                    self._stale[card] -= 1  # a previous hand's leftover left — not returnable
                else:
                    self._returnable[card] = self._returnable.get(card, 0) + 1

    def _track_active(self, card: Card, delta: int) -> None:
        self._active[card] = max(0, self._active.get(card, 0) + delta)

    def end_hand(self) -> None:
        """Bank the hand: count persists; cards still on the felt become stale."""
        if self._counted_this_hand:
            self._hands_played += 1
        self._counted_this_hand = 0
        self._returnable.clear()
        self._stale = {c: n for c, n in self._active.items() if n > 0}

    def new_shoe(self) -> None:
        self._count = CountState(decks=self._decks)
        self._seen_by_rank.clear()
        self._hands_played = 0
        self._counted_this_hand = 0
        self._returnable.clear()
        self._stale.clear()
        self._active = {}

    def remaining_composition(self) -> Dict[str, int]:
        """Estimated cards left in the shoe per chart rank ("2".."10", "A").

        Floored at 0 per rank so a misdetection can't produce negatives.
        """
        comp = full_composition(self._decks)
        for rank, seen in self._seen_by_rank.items():
            comp[rank] = max(comp[rank] - seen, 0)
        return comp
