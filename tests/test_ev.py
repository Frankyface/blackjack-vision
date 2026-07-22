"""EV engine validation.

Benchmarks: dealer-outcome probabilities are checked against the classic
infinite-deck figures (loose windows, since exact published tables vary by
conditioning); action EVs are checked for ORDER against unambiguous basic
strategy cells — the EV-optimal action must match the chart on clear-cut
hands under both H17 and S17.
"""
import pytest

from src.cards import Card, card
from src.engines.ev import (
    dealer_distribution,
    full_composition,
    hand_ev,
    probabilities,
)
from src.engines.rules import Rules
from src.engines.strategy import decide

H17 = Rules(dealer_hits_soft_17=True)
S17 = Rules(dealer_hits_soft_17=False)
COMP = full_composition(6)
PROBS = probabilities(COMP)


def up(key):
    return card("AS") if key == "A" else Card(key, "D")


def hand(names):
    return tuple(card(n) for n in names)


# --- dealer distribution sanity ---

@pytest.mark.parametrize("up_key", ["2", "3", "4", "5", "6", "7", "8", "9", "10", "A"])
@pytest.mark.parametrize("hits17", [True, False])
def test_dealer_distribution_sums_to_one(up_key, hits17):
    dist = dealer_distribution(up_key, PROBS, hits17)
    assert sum(dist.values()) == pytest.approx(1.0, abs=1e-9)
    assert all(v >= 0 for v in dist.values())


@pytest.mark.parametrize(
    "up_key,lo,hi",
    [
        ("2", 0.32, 0.38),   # classic ~35%
        ("4", 0.37, 0.43),   # ~40%
        ("6", 0.40, 0.46),   # ~42-44%
        ("7", 0.24, 0.29),   # ~26%
        ("9", 0.21, 0.26),   # ~23%
        ("10", 0.20, 0.26),  # ~21-23% (no-BJ conditional)
        ("A", 0.15, 0.23),   # ~17-20% (no-BJ conditional)
    ],
)
def test_dealer_bust_windows_s17(up_key, lo, hi):
    dist = dealer_distribution(up_key, PROBS, hits_soft_17=False)
    assert lo <= dist.get("bust", 0.0) <= hi


def test_h17_busts_more_than_s17_on_ace_and_six():
    for up_key in ("A", "6"):
        h17 = dealer_distribution(up_key, PROBS, True).get("bust", 0.0)
        s17 = dealer_distribution(up_key, PROBS, False).get("bust", 0.0)
        assert h17 > s17


def test_no_blackjack_key_after_conditioning():
    for up_key in ("10", "A"):
        dist = dealer_distribution(up_key, PROBS, True)
        assert "bj" not in dist


# --- EV magnitudes on well-known hands (loose, safe windows) ---

def test_stand_20_v_10_strongly_positive():
    ev = hand_ev(hand(["KS", "QH"]), up("10"), S17, COMP)
    assert 0.35 <= ev.actions["STAND"].ev <= 0.65


def test_hard_16_v_10_all_options_negative_but_survivable():
    ev = hand_ev(hand(["9S", "7H"]), up("10"), S17, COMP)
    assert -0.65 <= ev.actions["HIT"].ev <= -0.40
    assert -0.65 <= ev.actions["STAND"].ev <= -0.40


def test_blackjack_pays_the_configured_payout():
    ev = hand_ev(hand(["AS", "KH"]), up("6"), S17, COMP)
    assert ev.best == "STAND"
    assert ev.actions["STAND"].ev == pytest.approx(1.5)  # 3:2
    assert ev.actions["STAND"].p_win == 1.0
    six_five = Rules(blackjack_payout=1.2)
    ev65 = hand_ev(hand(["AS", "KH"]), up("6"), six_five, COMP)
    assert ev65.actions["STAND"].ev == pytest.approx(1.2)


def test_blackjack_vs_ten_conditional_on_no_dealer_natural():
    # 10/A up-cards are conditioned on no dealer blackjack, so a player
    # natural still wins the full payout with certainty
    ev = hand_ev(hand(["AS", "KH"]), up("10"), S17, COMP)
    assert ev.actions["STAND"].ev == pytest.approx(1.5)


# --- EV-optimal action must agree with basic strategy on clear-cut cells ---

CLEAR_CELLS = [
    (["10S", "6H"], "6", "STAND"),
    (["10S", "6H"], "10", "HIT"),
    (["5S", "6H"], "6", "DOUBLE"),
    (["5S", "6H"], "5", "DOUBLE"),
    (["2S", "9H"], "5", "DOUBLE"),
    (["10S", "10H"], "6", "STAND"),
    (["8S", "8H"], "6", "SPLIT"),
    (["AS", "AH"], "6", "SPLIT"),
    (["AS", "7H"], "10", "HIT"),
    (["AS", "6H"], "6", "DOUBLE"),
    (["9S", "5H"], "2", "STAND"),
    (["9S", "5H"], "10", "HIT"),
    (["2S", "7H"], "6", "DOUBLE"),
    (["10S", "2H"], "6", "STAND"),
    (["3S", "3H"], "6", "SPLIT"),
]


@pytest.mark.parametrize("names,up_key,expected", CLEAR_CELLS)
@pytest.mark.parametrize("rules", [H17, S17], ids=["H17", "S17"])
def test_ev_optimal_matches_chart_on_clear_cells(names, up_key, expected, rules):
    result = hand_ev(hand(names), up(up_key), rules, COMP)
    chart = decide(hand(names), up(up_key), rules).action.value
    assert chart == expected, f"fixture wrong: chart says {chart}"
    assert result.best == expected, (
        f"EV best {result.best} != chart {expected} "
        f"({ {a: round(o.ev, 3) for a, o in result.actions.items()} })"
    )


def test_surrender_available_and_correctly_valued():
    rules = Rules(late_surrender=True)
    result = hand_ev(hand(["10S", "6H"]), up("10"), rules, COMP)
    assert result.actions["SURRENDER"].ev == -0.5
    # 16 v 10: surrender is the EV-best play (chart agrees: Rh)
    assert result.best == "SURRENDER"


def test_composition_shifts_ev():
    """A ten-rich shoe should make standing on 16 v 10 relatively better."""
    rich = dict(COMP)
    rich["10"] = rich["10"] + 60   # artificially ten-rich
    poor = dict(COMP)
    poor["10"] = max(poor["10"] - 60, 1)
    ev_rich = hand_ev(hand(["9S", "7H"]), up("10"), S17, rich)
    ev_poor = hand_ev(hand(["9S", "7H"]), up("10"), S17, poor)
    rich_gap = ev_rich.actions["STAND"].ev - ev_rich.actions["HIT"].ev
    poor_gap = ev_poor.actions["STAND"].ev - ev_poor.actions["HIT"].ev
    assert rich_gap > poor_gap


def test_double_restrictions_remove_double():
    rules = Rules(double_restrictions="10-11")
    result = hand_ev(hand(["2S", "7H"]), up("5"), rules, COMP)  # hard 9
    assert "DOUBLE" not in result.actions


def test_empty_composition_rejected():
    with pytest.raises(ValueError):
        probabilities({r: 0 for r in COMP})
