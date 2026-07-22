"""Hand valuation. Pure — no I/O."""
from __future__ import annotations

from typing import NamedTuple, Sequence, Tuple

from .cards import Card


class HandValue(NamedTuple):
    total: int
    is_soft: bool  # an ace is currently counted as 11

    def __str__(self) -> str:
        return f"soft {self.total}" if self.is_soft else f"hard {self.total}"


def hand_value(cards: Sequence[Card]) -> HandValue:
    total = 0
    aces = 0
    for c in cards:
        total += c.blackjack_value
        if c.rank == "A":
            aces += 1
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return HandValue(total, aces > 0)


def is_bust(cards: Sequence[Card]) -> bool:
    return hand_value(cards).total > 21


def is_blackjack(cards: Sequence[Card]) -> bool:
    return len(cards) == 2 and hand_value(cards).total == 21


def is_pair(cards: Sequence[Card]) -> bool:
    """Splittable pair: same rank, or any two ten-valued cards (10/J/Q/K)."""
    if len(cards) != 2:
        return False
    a, b = cards
    return a.rank == b.rank or (a.is_ten_valued and b.is_ten_valued)


def pair_rank(cards: Sequence[Card]) -> str:
    """Chart rank of a pair; any ten-valued pair maps to "10"."""
    if not is_pair(cards):
        raise ValueError(f"not a pair: {[str(c) for c in cards]}")
    return "10" if cards[0].is_ten_valued else cards[0].rank


def dealer_up_key(card: Card) -> str:
    """Chart column key for the dealer up-card: "2".."10" or "A"."""
    return "A" if card.rank == "A" else ("10" if card.is_ten_valued else card.rank)
