"""Basic strategy engine. Pure — (hand, dealer up-card, rules) -> action.

Charts are the published 4-8 deck basic strategy tables (source: Wizard of
Odds multi-deck charts), encoded as composite cell codes and resolved against
what's actually available (double only on 2 cards, DAS, surrender, etc.):

  H  hit                    S  stand
  Dh double, else hit       Ds double, else stand
  P  split                  Ph split if DAS, else hit
  Rh surrender, else hit    Rs surrender, else stand
  Rp surrender, else split
"""
from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Dict, Sequence, Tuple

from ..cards import Card
from ..game_state import dealer_up_key, hand_value, is_pair, pair_rank
from .rules import Rules

UPS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "A")


class Action(enum.Enum):
    HIT = "HIT"
    STAND = "STAND"
    DOUBLE = "DOUBLE"
    SPLIT = "SPLIT"
    SURRENDER = "SURRENDER"


@dataclass(frozen=True)
class Decision:
    action: Action
    cell: str  # the raw chart code, for UI/debugging ("Dh", "Rh", ...)


def _row(codes: str) -> Dict[str, str]:
    """Build a chart row: 10 space-separated codes for dealer 2..10,A."""
    parts = codes.split()
    assert len(parts) == 10, f"chart row needs 10 cells, got {len(parts)}: {codes}"
    return dict(zip(UPS, parts))


# --- Hard totals (no usable ace). Rows for 5..17; <=4 impossible as 2 cards
#     but handled via 5's row; 18+ is always Stand (handled in code).
_HARD_COMMON = {
    5:  _row("H  H  H  H  H  H  H  H  H  H"),
    6:  _row("H  H  H  H  H  H  H  H  H  H"),
    7:  _row("H  H  H  H  H  H  H  H  H  H"),
    8:  _row("H  H  H  H  H  H  H  H  H  H"),
    9:  _row("H  Dh Dh Dh Dh H  H  H  H  H"),
    10: _row("Dh Dh Dh Dh Dh Dh Dh Dh H  H"),
    12: _row("H  H  S  S  S  H  H  H  H  H"),
    13: _row("S  S  S  S  S  H  H  H  H  H"),
    14: _row("S  S  S  S  S  H  H  H  H  H"),
    16: _row("S  S  S  S  S  H  H  Rh Rh Rh"),
}
_HARD_H17 = dict(_HARD_COMMON)
_HARD_H17.update({
    11: _row("Dh Dh Dh Dh Dh Dh Dh Dh Dh Dh"),
    15: _row("S  S  S  S  S  H  H  H  Rh Rh"),
    17: _row("S  S  S  S  S  S  S  S  S  Rs"),
})
_HARD_S17 = dict(_HARD_COMMON)
_HARD_S17.update({
    11: _row("Dh Dh Dh Dh Dh Dh Dh Dh Dh H"),
    15: _row("S  S  S  S  S  H  H  H  Rh H"),
    17: _row("S  S  S  S  S  S  S  S  S  S"),
})

# --- Soft totals (A counted as 11). Rows for 13 (A,2) .. 20 (A,9).
_SOFT_COMMON = {
    13: _row("H  H  H  Dh Dh H  H  H  H  H"),
    14: _row("H  H  H  Dh Dh H  H  H  H  H"),
    15: _row("H  H  Dh Dh Dh H  H  H  H  H"),
    16: _row("H  H  Dh Dh Dh H  H  H  H  H"),
    17: _row("H  Dh Dh Dh Dh H  H  H  H  H"),
    20: _row("S  S  S  S  S  S  S  S  S  S"),
}
_SOFT_H17 = dict(_SOFT_COMMON)
_SOFT_H17.update({
    18: _row("Ds Ds Ds Ds Ds S  S  H  H  H"),
    19: _row("S  S  S  S  Ds S  S  S  S  S"),
})
_SOFT_S17 = dict(_SOFT_COMMON)
_SOFT_S17.update({
    18: _row("S  Ds Ds Ds Ds S  S  H  H  H"),
    19: _row("S  S  S  S  S  S  S  S  S  S"),
})

# --- Pairs (keyed by pair rank). Same table both S17/H17 except 8,8 vs A.
_PAIRS_COMMON = {
    "2":  _row("Ph Ph P  P  P  P  H  H  H  H"),
    "3":  _row("Ph Ph P  P  P  P  H  H  H  H"),
    "4":  _row("H  H  H  Ph Ph H  H  H  H  H"),
    "6":  _row("Ph P  P  P  P  H  H  H  H  H"),
    "7":  _row("P  P  P  P  P  P  H  H  H  H"),
    "9":  _row("P  P  P  P  P  S  P  P  S  S"),
    "10": _row("S  S  S  S  S  S  S  S  S  S"),
    "A":  _row("P  P  P  P  P  P  P  P  P  P"),
}
_PAIRS_H17 = dict(_PAIRS_COMMON)
_PAIRS_H17["8"] = _row("P  P  P  P  P  P  P  P  P  Rp")
_PAIRS_S17 = dict(_PAIRS_COMMON)
_PAIRS_S17["8"] = _row("P  P  P  P  P  P  P  P  P  P")
# 5,5 is deliberately absent: never split — play as hard 10.


def _double_allowed(cards: Sequence[Card], rules: Rules, is_post_split: bool) -> bool:
    if len(cards) != 2:
        return False
    if is_post_split and not rules.double_after_split:
        return False
    total = hand_value(cards).total
    if rules.double_restrictions == "9-11":
        return not hand_value(cards).is_soft and 9 <= total <= 11
    if rules.double_restrictions == "10-11":
        return not hand_value(cards).is_soft and 10 <= total <= 11
    return True  # any2


def _resolve(cell: str, *, can_double: bool, can_split: bool,
             can_surrender: bool, das: bool = True) -> Action:
    if cell == "H":
        return Action.HIT
    if cell == "S":
        return Action.STAND
    if cell == "Dh":
        return Action.DOUBLE if can_double else Action.HIT
    if cell == "Ds":
        return Action.DOUBLE if can_double else Action.STAND
    if cell == "P":
        return Action.SPLIT if can_split else _fallback_for_unsplittable(cell)
    if cell == "Ph":
        return Action.SPLIT if (can_split and das) else Action.HIT
    if cell == "Rh":
        return Action.SURRENDER if can_surrender else Action.HIT
    if cell == "Rs":
        return Action.SURRENDER if can_surrender else Action.STAND
    if cell == "Rp":
        if can_surrender:
            return Action.SURRENDER
        return Action.SPLIT if can_split else Action.HIT
    raise ValueError(f"unknown chart cell: {cell!r}")


def _fallback_for_unsplittable(cell: str) -> Action:
    # A plain "P" cell with splitting unavailable shouldn't occur through
    # decide() (pairs route through the pair table only when splittable), but
    # keep a sane fallback for direct calls.
    return Action.HIT


def decide(
    player_cards: Sequence[Card],
    dealer_up: Card,
    rules: Rules,
    *,
    is_post_split: bool = False,
    can_split: "bool | None" = None,
) -> Decision:
    """The correct basic-strategy action for this hand vs. this up-card.

    can_split override: pass False when the resplit limit is exhausted.
    """
    if len(player_cards) < 2:
        raise ValueError("a blackjack hand has at least 2 cards")
    up = dealer_up_key(dealer_up)
    hits17 = rules.dealer_hits_soft_17
    hard = _HARD_H17 if hits17 else _HARD_S17
    soft = _SOFT_H17 if hits17 else _SOFT_S17
    pairs = _PAIRS_H17 if hits17 else _PAIRS_S17

    value = hand_value(player_cards)
    two_cards = len(player_cards) == 2
    allow_double = _double_allowed(player_cards, rules, is_post_split)
    allow_surrender = rules.late_surrender and two_cards and not is_post_split
    splittable = (
        two_cards
        and is_pair(player_cards)
        and (can_split if can_split is not None else True)
    )

    # Pairs first (5,5 intentionally falls through to hard 10).
    if splittable:
        rank = pair_rank(player_cards)
        if rank == "A" and is_post_split and not rules.resplit_aces:
            pass  # re-split aces not allowed — fall through to soft/hard play
        elif rank in pairs:
            cell = pairs[rank][up]
            return Decision(
                _resolve(cell, can_double=allow_double, can_split=True,
                         can_surrender=allow_surrender,
                         das=rules.double_after_split),
                cell,
            )

    if value.is_soft:
        if value.total == 12:
            # soft 12 (unsplittable A,A): always hit — the A,2 row's double
            # cells don't apply to a 12
            cell = "H"
        else:
            cell = soft[min(value.total, 20)][up]
    elif value.total >= 18:
        cell = "S"
    else:
        cell = hard[max(value.total, 5)][up]

    return Decision(
        _resolve(cell, can_double=allow_double, can_split=False,
                 can_surrender=allow_surrender),
        cell,
    )
