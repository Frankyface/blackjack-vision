"""Stage 6: automatic round detection, outcome scoring, session stats.

Pure logic fed with StableState snapshots. A round "ends" when the table has
been empty for `empty_updates_to_end` consecutive updates after having held
cards — no SPACE key needed. The result is scored from the last full table
seen (dealer draw-out included, since the dealer's cards accumulate in the
dealer zone as they're dealt face-up).
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .cards import Card
from .game_state import hand_value, is_blackjack, is_bust
from .stable import StableState
from .zones import Zone


class Outcome(enum.Enum):
    WIN = "WIN"
    LOSE = "LOSE"
    PUSH = "PUSH"
    BLACKJACK = "BLACKJACK"      # player natural win (pays rules payout)
    UNSCORED = "UNSCORED"        # not enough seen to judge


@dataclass(frozen=True)
class RoundResult:
    player_cards: Tuple[Card, ...]
    dealer_cards: Tuple[Card, ...]
    outcome: Outcome
    player_total: int
    dealer_total: int


def score_round(
    player: Tuple[Card, ...], dealer: Tuple[Card, ...]
) -> RoundResult:
    """Judge a finished round from the final table state."""
    p_total = hand_value(player).total if player else 0
    d_total = hand_value(dealer).total if dealer else 0
    if len(player) >= 2 and is_bust(player):
        # A bust loses regardless of what the dealer showed — and the dealer
        # usually never reveals the hole card after a bust.
        return RoundResult(player, dealer, Outcome.LOSE, p_total, d_total)
    if len(player) < 2 or len(dealer) < 2:
        # Never saw a full showdown (dealer hole card unread, cards missed).
        return RoundResult(player, dealer, Outcome.UNSCORED, p_total, d_total)
    if is_blackjack(player) and not is_blackjack(dealer):
        outcome = Outcome.BLACKJACK
    elif is_blackjack(dealer) and not is_blackjack(player):
        outcome = Outcome.LOSE  # a natural beats any drawn 21
    elif is_bust(dealer):
        outcome = Outcome.WIN
    elif p_total > d_total:
        outcome = Outcome.WIN
    elif p_total < d_total:
        outcome = Outcome.LOSE
    else:
        outcome = Outcome.PUSH
    return RoundResult(player, dealer, outcome, p_total, d_total)


class RoundTracker:
    """Watches the table fill and empty; emits a RoundResult per round."""

    def __init__(self, empty_updates_to_end: int = 30) -> None:
        if empty_updates_to_end < 1:
            raise ValueError("empty_updates_to_end must be >= 1")
        self._empty_needed = empty_updates_to_end
        self._empty_streak = 0
        self._had_cards = False
        self._suppress_until_empty = False
        self._last_player: Tuple[Card, ...] = ()
        self._last_dealer: Tuple[Card, ...] = ()

    def update(self, state: StableState) -> Optional[RoundResult]:
        if self._suppress_until_empty:
            # A manual finish() already scored the cards on the felt; ignore
            # them until the table clears so they can't be scored twice.
            if state.total_cards == 0:
                self._suppress_until_empty = False
            return None
        if state.total_cards > 0:
            self._had_cards = True
            self._empty_streak = 0
            # Zones empty out at different moments during cleanup — never
            # overwrite a zone's snapshot with () or most rounds score UNSCORED.
            player = state.cards(Zone.PLAYER)
            dealer = state.cards(Zone.DEALER)
            if player:
                self._last_player = player
            if dealer:
                self._last_dealer = dealer
            return None
        if not self._had_cards:
            return None
        self._empty_streak += 1
        if self._empty_streak < self._empty_needed:
            return None
        result = score_round(self._last_player, self._last_dealer)
        self.reset()
        return result

    def finish(self) -> Optional[RoundResult]:
        """Manual end-of-hand (SPACE): score whatever was last seen, if anything."""
        if not self._had_cards:
            return None
        result = score_round(self._last_player, self._last_dealer)
        self.reset()
        # Cards may still be on the felt — don't score them a second time when
        # the dealer eventually collects them.
        self._suppress_until_empty = True
        return result

    def reset(self) -> None:
        self._had_cards = False
        self._empty_streak = 0
        self._suppress_until_empty = False
        self._last_player = ()
        self._last_dealer = ()


@dataclass
class SessionStats:
    """Rolling session statistics, including approximate decision accuracy.

    Decision accuracy is inferred: when the advice was STAND/HIT and the
    player's card count did / didn't grow before the round ended, we can tell
    whether the advice was followed. DOUBLE/SPLIT/SURRENDER are not inferable
    from card counts alone and are excluded from the accuracy figure.
    """
    wins: int = 0
    losses: int = 0
    pushes: int = 0
    blackjacks: int = 0
    unscored: int = 0
    decisions_followed: int = 0
    decisions_total: int = 0
    _pending_advice: Optional[str] = None
    _pending_at_count: int = 0
    _max_count_seen: int = 0

    def observe(self, advice: Optional[str], player_card_count: int) -> None:
        """Call EVERY frame with the current advice (may be None) and player
        card count. A pending HIT/STAND resolves when the count grows past the
        count it was issued at — even if the advice has since gone None (e.g.
        the dealer's hole card appeared before the hit card confirmed).
        Detection dropouts (count shrinking then recovering) never resolve
        anything: growth is measured against the maximum count seen.
        """
        if (
            self._pending_advice is not None
            and player_card_count > self._max_count_seen
            and player_card_count > self._pending_at_count
        ):
            self.decisions_total += 1
            if self._pending_advice == "HIT":
                self.decisions_followed += 1
            self._pending_advice = None
        self._max_count_seen = max(self._max_count_seen, player_card_count)
        if advice in ("HIT", "STAND") and advice != self._pending_advice:
            self._pending_advice = advice
            self._pending_at_count = self._max_count_seen
        elif advice is not None and advice not in ("HIT", "STAND"):
            self._pending_advice = None  # DOUBLE/SPLIT/BUST etc: not inferable

    def record_result(self, result: RoundResult) -> None:
        if result.outcome is Outcome.WIN:
            self.wins += 1
        elif result.outcome is Outcome.LOSE:
            self.losses += 1
        elif result.outcome is Outcome.PUSH:
            self.pushes += 1
        elif result.outcome is Outcome.BLACKJACK:
            self.blackjacks += 1
        else:
            self.unscored += 1
        # round ended: an open HIT/STAND decision resolves as "stood"
        if self._pending_advice == "STAND":
            self.decisions_total += 1
            self.decisions_followed += 1
        elif self._pending_advice == "HIT":
            self.decisions_total += 1
        self._pending_advice = None
        self._pending_at_count = 0
        self._max_count_seen = 0

    @property
    def hands(self) -> int:
        return self.wins + self.losses + self.pushes + self.blackjacks + self.unscored

    @property
    def accuracy(self) -> Optional[float]:
        if self.decisions_total == 0:
            return None
        return self.decisions_followed / self.decisions_total

    def summary_line(self) -> str:
        scored = self.wins + self.blackjacks
        parts = [f"{self.hands} hands", f"{scored}W {self.losses}L {self.pushes}P"]
        if self.blackjacks:
            parts.append(f"{self.blackjacks} BJ")
        if self.accuracy is not None:
            parts.append(f"advice followed {self.accuracy * 100:.0f}%")
        return " · ".join(parts)
