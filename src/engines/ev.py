"""Expected value / win probability engine. Pure math, no I/O.

Model notes (documented approximations, fine for a trainer):
- Draw probabilities are FIXED at the current shoe composition ("current-
  composition infinite deck"). With a full shoe this reproduces the classic
  infinite-deck numbers; as the count moves, the probabilities shift with it.
- For a 10/A up-card, EVs are conditional on the dealer NOT having blackjack
  (the US peek game: the hand wouldn't be played out otherwise).
- Split EV = 2 x EV of one post-split hand (no resplits); split aces get one
  card. Standard first-order approximation.
- Surrender EV is exactly -0.5.

Returned per action: EV in units of the initial bet, plus win/push
probabilities under the EV-optimal continuation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Sequence, Tuple

from ..cards import Card
from ..game_state import dealer_up_key, hand_value, is_pair
from .rules import Rules

RANK_KEYS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "A")
_RANK_VALUE = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
               "9": 9, "10": 10, "A": 11}


def full_composition(decks: int) -> Dict[str, int]:
    comp = {r: 4 * decks for r in RANK_KEYS}
    comp["10"] = 16 * decks  # 10, J, Q, K
    return comp


def probabilities(comp: Mapping[str, int]) -> Dict[str, float]:
    total = sum(comp.values())
    if total <= 0:
        raise ValueError("composition is empty — no cards remaining")
    return {r: comp[r] / total for r in RANK_KEYS}


@dataclass(frozen=True)
class Outcome:
    ev: float
    p_win: float
    p_push: float


@dataclass(frozen=True)
class HandEV:
    actions: Mapping[str, Outcome]   # action name -> Outcome
    best: str

    @property
    def best_outcome(self) -> Outcome:
        return self.actions[self.best]


def dealer_distribution(
    up: str, probs: Mapping[str, float], hits_soft_17: bool
) -> Dict[str, float]:
    """P(final dealer result | up-card): keys '17'..'21', 'bj', 'bust'.

    For up 10/A the distribution is conditional on no dealer blackjack.
    """
    memo: Dict[Tuple[int, bool], Dict[str, float]] = {}

    def draw(total: int, soft: bool) -> Dict[str, float]:
        must_hit = total < 17 or (total == 17 and soft and hits_soft_17)
        if not must_hit:
            if total > 21:
                return {"bust": 1.0}
            return {str(total): 1.0}
        key = (total, soft)
        if key in memo:
            return memo[key]
        out: Dict[str, float] = {}
        for rank, p in probs.items():
            if p == 0.0:
                continue
            # soft means an ace still counted as 11
            if rank == "A":
                if total + 11 <= 21:
                    new_total, new_soft = total + 11, True
                else:
                    new_total, new_soft = total + 1, soft
            else:
                new_total = total + _RANK_VALUE[rank]
                new_soft = soft
                if new_total > 21 and new_soft:
                    new_total -= 10
                    new_soft = False
            for result, q in draw(new_total, new_soft).items():
                out[result] = out.get(result, 0.0) + p * q
        memo[key] = out
        return out

    up_value = _RANK_VALUE[up]
    start_soft = up == "A"
    result = draw(up_value, start_soft)

    if up in ("10", "A"):
        # Split the 21s into blackjack (second card completes a natural) vs
        # drawn 21, then condition on no blackjack.
        p_bj = probs["A"] if up == "10" else probs["10"]
        dist = dict(result)
        if "21" in dist:
            dist["21"] = max(dist["21"] - p_bj, 0.0)
        remaining = 1.0 - p_bj
        if remaining > 0:
            dist = {k: v / remaining for k, v in dist.items() if v > 0}
        return dist
    return result


def _stand_outcome(total: int, dealer_dist: Mapping[str, float]) -> Outcome:
    if total > 21:
        return Outcome(-1.0, 0.0, 0.0)
    win = push = lose = 0.0
    for result, p in dealer_dist.items():
        if result == "bust":
            win += p
        elif result == "bj":
            lose += p
        else:
            d = int(result)
            if total > d:
                win += p
            elif total == d:
                push += p
            else:
                lose += p
    return Outcome(win - lose, win, push)


def _combine(branches: Sequence[Tuple[float, Outcome]]) -> Outcome:
    ev = sum(p * o.ev for p, o in branches)
    return Outcome(
        ev,
        sum(p * o.p_win for p, o in branches),
        sum(p * o.p_push for p, o in branches),
    )


def hand_ev(
    player_cards: Sequence[Card],
    dealer_up: Card,
    rules: Rules,
    comp: Mapping[str, int],
    *,
    is_post_split: bool = False,
) -> HandEV:
    """EV + win/push probability for every available action."""
    probs = probabilities(comp)
    up = dealer_up_key(dealer_up)
    dealer_dist = dealer_distribution(up, probs, rules.dealer_hits_soft_17)

    hit_memo: Dict[Tuple[int, bool], Outcome] = {}

    def optimal_from(total: int, soft: bool) -> Outcome:
        """Best of stand/hit from a total (post-first-decision states)."""
        stand = _stand_outcome(total, dealer_dist)
        if total >= 21:
            return stand
        key = (total, soft)
        if key in hit_memo:
            best_hit = hit_memo[key]
        else:
            hit_memo[key] = _stand_outcome(22, dealer_dist)  # cycle guard: bust
            branches = []
            for rank, p in probs.items():
                if p == 0.0:
                    continue
                nt, ns = _add(total, soft, rank)
                branches.append((p, optimal_from(nt, ns)))
            best_hit = _combine(branches)
            hit_memo[key] = best_hit
        return stand if stand.ev >= best_hit.ev else best_hit

    def _add(total: int, soft: bool, rank: str) -> Tuple[int, bool]:
        if rank == "A":
            if total + 11 <= 21:
                return total + 11, True
            return total + 1, soft
        nt = total + _RANK_VALUE[rank]
        if nt > 21 and soft:
            return nt - 10, False
        return nt, soft

    value = hand_value(player_cards)
    total, soft = value.total, value.is_soft
    actions: Dict[str, Outcome] = {}

    if len(player_cards) == 2 and total == 21 and not is_post_split:
        # Player natural. Dealer naturals are already conditioned away for
        # 10/A up-cards and impossible otherwise, so this wins the full
        # blackjack payout with certainty (a dealer DRAWN 21 loses to it).
        payout = Outcome(rules.blackjack_payout, 1.0, 0.0)
        return HandEV(actions={"STAND": payout}, best="STAND")

    actions["STAND"] = _stand_outcome(total, dealer_dist)

    hit_branches = []
    for rank, p in probs.items():
        if p == 0.0:
            continue
        nt, ns = _add(total, soft, rank)
        hit_branches.append((p, optimal_from(nt, ns)))
    actions["HIT"] = _combine(hit_branches)

    two_cards = len(player_cards) == 2
    das_ok = not is_post_split or rules.double_after_split
    if two_cards and das_ok and _double_permitted(total, soft, rules):
        dbl_branches = []
        for rank, p in probs.items():
            if p == 0.0:
                continue
            nt, _ = _add(total, soft, rank)
            o = _stand_outcome(nt, dealer_dist)
            dbl_branches.append((p, Outcome(2 * o.ev, o.p_win, o.p_push)))
        actions["DOUBLE"] = _combine(dbl_branches)

    if two_cards and is_pair(player_cards) and not is_post_split:
        split_card = player_cards[0]
        one_hand = _split_hand_ev(split_card, dealer_dist, probs, rules)
        actions["SPLIT"] = Outcome(2 * one_hand.ev, one_hand.p_win, one_hand.p_push)

    if two_cards and rules.late_surrender and not is_post_split:
        actions["SURRENDER"] = Outcome(-0.5, 0.0, 0.0)

    best = max(actions, key=lambda a: actions[a].ev)
    return HandEV(actions=actions, best=best)


def _double_permitted(total: int, soft: bool, rules: Rules) -> bool:
    if rules.double_restrictions == "9-11":
        return not soft and 9 <= total <= 11
    if rules.double_restrictions == "10-11":
        return not soft and 10 <= total <= 11
    return True


def _split_hand_ev(split_card, dealer_dist, probs, rules) -> Outcome:
    """EV of ONE post-split hand (start = split card + one draw)."""
    branches = []
    base = 11 if split_card.rank == "A" else _RANK_VALUE[
        "10" if split_card.is_ten_valued else split_card.rank
    ]
    for rank, p in probs.items():
        if p == 0.0:
            continue
        if split_card.rank == "A":
            # split aces: exactly one card, then stand
            if rank == "A":
                nt, ns = 12, True
            else:
                nt, ns = 11 + _RANK_VALUE[rank], True
            branches.append((p, _stand_outcome(nt, dealer_dist)))
            continue
        if rank == "A":
            nt, ns = (base + 11, True) if base + 11 <= 21 else (base + 1, False)
        else:
            nt, ns = base + _RANK_VALUE[rank], False
        # play the post-split hand stand/hit optimally (no resplit; doubling
        # after split ignored here — second-order effect)
        stand = _stand_outcome(nt, dealer_dist)
        hit = _post_split_optimal(nt, ns, dealer_dist, probs)
        branches.append((p, stand if stand.ev >= hit.ev else hit))
    return _combine(branches)


def _post_split_optimal(total, soft, dealer_dist, probs,
                        memo=None) -> Outcome:
    if memo is None:
        memo = {}
    key = (total, soft)
    if key in memo:
        return memo[key]
    memo[key] = _stand_outcome(22, dealer_dist)
    branches = []
    for rank, p in probs.items():
        if p == 0.0:
            continue
        if rank == "A":
            nt, ns = (total + 11, True) if total + 11 <= 21 else (total + 1, soft)
        else:
            nt = total + _RANK_VALUE[rank]
            ns = soft
            if nt > 21 and ns:
                nt, ns = nt - 10, False
        if nt >= 21:
            branches.append((p, _stand_outcome(nt, dealer_dist)))
        else:
            stand = _stand_outcome(nt, dealer_dist)
            deeper = _post_split_optimal(nt, ns, dealer_dist, probs, memo)
            branches.append((p, stand if stand.ev >= deeper.ev else deeper))
    hit = _combine(branches)
    stand_now = _stand_outcome(total, dealer_dist)
    best = stand_now if stand_now.ev >= hit.ev else hit
    memo[key] = best
    return best
