"""Card model and YOLO class-name parsing. Pure — no I/O."""
from __future__ import annotations

from typing import NamedTuple, Optional

RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
SUITS = ("S", "H", "D", "C")

_SUIT_WORDS = {
    "s": "S", "spade": "S", "spades": "S",
    "h": "H", "heart": "H", "hearts": "H",
    "d": "D", "diamond": "D", "diamonds": "D",
    "c": "C", "club": "C", "clubs": "C",
}
_RANK_WORDS = {
    "a": "A", "ace": "A", "j": "J", "jack": "J", "q": "Q", "queen": "Q",
    "k": "K", "king": "K", "t": "10", "ten": "10", "10": "10",
    "two": "2", "three": "3", "four": "4", "five": "5", "six": "6",
    "seven": "7", "eight": "8", "nine": "9",
    **{str(n): str(n) for n in range(2, 10)},
}
# Class names that are valid detections but not playing cards we track.
_NON_CARDS = {"joker", "jokers", "back", "card back", "cardback", "back of card"}


class Card(NamedTuple):
    rank: str  # one of RANKS
    suit: str  # one of SUITS

    @property
    def blackjack_value(self) -> int:
        """Ace counts as 11 here; soft-total handling lives in game_state."""
        if self.rank == "A":
            return 11
        if self.rank in ("J", "Q", "K", "10"):
            return 10
        return int(self.rank)

    @property
    def is_ten_valued(self) -> bool:
        return self.rank in ("10", "J", "Q", "K")

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"


def parse_class_name(name: str) -> Optional[Card]:
    """Parse a YOLO class name into a Card.

    Handles the common labelling formats: "10S", "As", "KH", "10 of clubs",
    "ace of spades", "10c". Returns None for jokers / card backs / anything
    unrecognized — callers must treat None as "ignore this detection".
    """
    if not name:
        return None
    cleaned = name.strip().lower()
    if cleaned in _NON_CARDS:
        return None

    words = cleaned.replace("_", " ").replace("-", " ").split()
    if "of" in words and len(words) >= 3:  # "ace of spades"
        rank = _RANK_WORDS.get(words[0])
        suit = _SUIT_WORDS.get(words[-1])
        if rank and suit:
            return Card(rank, suit)
        return None

    compact = "".join(words)  # "10s", "as", "kh"
    if len(compact) >= 2:
        rank = _RANK_WORDS.get(compact[:-1])
        suit = _SUIT_WORDS.get(compact[-1])
        if rank and suit:
            return Card(rank, suit)
    return None


def card(text: str) -> Card:
    """Test/config helper: card("AS") -> Card("A", "S"). Raises on junk."""
    parsed = parse_class_name(text)
    if parsed is None:
        raise ValueError(f"not a card: {text!r}")
    return parsed
