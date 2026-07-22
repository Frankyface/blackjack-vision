"""Hi-Lo counting engine. Pure — immutable state, fold cards in, read counts out.

Hi-Lo values: 2-6 = +1 · 7-9 = 0 · 10/J/Q/K/A = -1.
True count = running count / decks remaining (estimated to the half deck,
never below half a deck). Bet hint comes from a configurable ramp.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Mapping, Sequence

from ..cards import Card

_PLUS = {"2", "3", "4", "5", "6"}
_MINUS = {"10", "J", "Q", "K", "A"}


def hilo_value(card: Card) -> int:
    if card.rank in _PLUS:
        return 1
    if card.rank in _MINUS:
        return -1
    return 0


@dataclass(frozen=True)
class CountState:
    decks: int
    running: int = 0
    cards_seen: int = 0

    def see(self, card: Card) -> "CountState":
        return replace(
            self,
            running=self.running + hilo_value(card),
            cards_seen=self.cards_seen + 1,
        )

    def see_all(self, cards: Sequence[Card]) -> "CountState":
        state = self
        for c in cards:
            state = state.see(c)
        return state

    @property
    def decks_remaining(self) -> float:
        """Floored to the half deck (counter convention), never below half.

        Flooring (not rounding) means the estimate never exceeds what is
        physically left, so the true count is never diluted by phantom decks.
        """
        exact = self.decks - self.cards_seen / 52.0
        half_decks = math.floor(exact * 2) / 2.0
        return max(0.5, half_decks)

    @property
    def true_count(self) -> float:
        return self.running / self.decks_remaining

    @property
    def true_count_floor(self) -> int:
        """Floored toward negative infinity — the conventional betting TC."""
        return math.floor(self.true_count)


def bet_units(true_count_floor: int, ramp: Mapping[int, int]) -> int:
    """Units to bet for a given floored true count.

    ramp maps TC thresholds to units, e.g. {1: 1, 2: 2, 3: 4, 4: 8, 5: 12}.
    Below the lowest threshold -> minimum ramp value (table minimum).
    At/above the highest -> its value.
    """
    if not ramp:
        raise ValueError("bet ramp must not be empty")
    best = min(ramp.values())  # below the ramp: minimum bet
    for threshold in sorted(ramp):
        if true_count_floor >= threshold:
            best = ramp[threshold]
    return best
