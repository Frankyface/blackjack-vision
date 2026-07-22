"""Full-chart fixture tests for the basic strategy engine.

Expected grids transcribed from the Wizard of Odds 4-8 deck basic strategy
charts (H17 and S17, DAS, no surrender unless stated). Every cell asserted.
Grid letters are the RESOLVED action for a fresh 2-card hand under the config:
H=hit S=stand D=double P=split.
"""
import pytest

from src.cards import Card, card
from src.engines.rules import Rules
from src.engines.strategy import Action, decide

UPS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "A"]
H17 = Rules(dealer_hits_soft_17=True, late_surrender=False)
S17 = Rules(dealer_hits_soft_17=False, late_surrender=False)
H17_LS = Rules(dealer_hits_soft_17=True, late_surrender=True)
S17_LS = Rules(dealer_hits_soft_17=False, late_surrender=True)
NO_DAS = Rules(double_after_split=False)

ACT = {"H": Action.HIT, "S": Action.STAND, "D": Action.DOUBLE,
       "P": Action.SPLIT, "R": Action.SURRENDER}

# Two-card hard hands with no ace and no pair, per total.
HARD_HANDS = {
    5: ("2S", "3H"), 6: ("2S", "4H"), 7: ("2S", "5H"), 8: ("2S", "6H"),
    9: ("2S", "7H"), 10: ("2S", "8H"), 11: ("2S", "9H"), 12: ("2S", "10H"),
    13: ("6S", "7H"), 14: ("6S", "8H"), 15: ("7S", "8H"), 16: ("7S", "9H"),
    17: ("8S", "9H"),
}

HARD_H17 = {
    5:  "H H H H H H H H H H",
    6:  "H H H H H H H H H H",
    7:  "H H H H H H H H H H",
    8:  "H H H H H H H H H H",
    9:  "H D D D D H H H H H",
    10: "D D D D D D D D H H",
    11: "D D D D D D D D D D",
    12: "H H S S S H H H H H",
    13: "S S S S S H H H H H",
    14: "S S S S S H H H H H",
    15: "S S S S S H H H H H",
    16: "S S S S S H H H H H",
    17: "S S S S S S S S S S",
}
HARD_S17 = dict(HARD_H17)
HARD_S17[11] = "D D D D D D D D D H"

SOFT_HANDS = {t: ("AS", f"{t - 11}H") for t in range(13, 21)}  # A2..A9

SOFT_H17 = {
    13: "H H H D D H H H H H",
    14: "H H H D D H H H H H",
    15: "H H D D D H H H H H",
    16: "H H D D D H H H H H",
    17: "H D D D D H H H H H",
    18: "D D D D D S S H H H",
    19: "S S S S D S S S S S",
    20: "S S S S S S S S S S",
}
SOFT_S17 = dict(SOFT_H17)
SOFT_S17[18] = "S D D D D S S H H H"
SOFT_S17[19] = "S S S S S S S S S S"

PAIR_GRID = {  # DAS, no surrender; identical H17/S17 here
    "2":  "P P P P P P H H H H",
    "3":  "P P P P P P H H H H",
    "4":  "H H H P P H H H H H",
    "5":  "D D D D D D D D H H",   # never split — hard 10
    "6":  "P P P P P H H H H H",
    "7":  "P P P P P P H H H H",
    "8":  "P P P P P P P P P P",
    "9":  "P P P P P S P P S S",
    "10": "S S S S S S S S S S",
    "A":  "P P P P P P P P P P",
}


def up(key):
    return card("AS") if key == "A" else Card(key, "D")


def hand(names):
    return tuple(card(n) for n in names)


def assert_grid(hands, grid, rules, label):
    for total, row in grid.items():
        cells = row.split()
        assert len(cells) == 10
        for up_key, expected in zip(UPS, cells):
            got = decide(hand(hands[total]), up(up_key), rules).action
            assert got is ACT[expected], (
                f"{label} {total} vs {up_key}: expected {expected}, got {got.value}"
            )


def test_hard_chart_h17():
    assert_grid(HARD_HANDS, HARD_H17, H17, "hard H17")


def test_hard_chart_s17():
    assert_grid(HARD_HANDS, HARD_S17, S17, "hard S17")


def test_soft_chart_h17():
    assert_grid(SOFT_HANDS, SOFT_H17, H17, "soft H17")


def test_soft_chart_s17():
    assert_grid(SOFT_HANDS, SOFT_S17, S17, "soft S17")


@pytest.mark.parametrize("rules,label", [(H17, "H17"), (S17, "S17")])
def test_pair_chart(rules, label):
    for rank, row in PAIR_GRID.items():
        cards = (Card(rank, "S"), Card(rank, "H"))
        for up_key, expected in zip(UPS, row.split()):
            got = decide(cards, up(up_key), rules).action
            assert got is ACT[expected], (
                f"pair {rank},{rank} vs {up_key} ({label}): expected {expected}, got {got.value}"
            )


def test_ten_value_mixed_pair_stands():
    assert decide(hand(["KS", "10H"]), up("6"), H17).action is Action.STAND


# --- known H17/S17 divergent cells, asserted explicitly ---

@pytest.mark.parametrize(
    "names,up_key,h17_action,s17_action",
    [
        (("2S", "9H"), "A", Action.DOUBLE, Action.HIT),   # 11 vs A
        (("AS", "7H"), "2", Action.DOUBLE, Action.STAND), # soft 18 vs 2
        (("AS", "8H"), "6", Action.DOUBLE, Action.STAND), # soft 19 vs 6
    ],
)
def test_h17_s17_divergences(names, up_key, h17_action, s17_action):
    assert decide(hand(names), up(up_key), H17).action is h17_action
    assert decide(hand(names), up(up_key), S17).action is s17_action


# --- surrender (late surrender on) ---

@pytest.mark.parametrize(
    "names,up_key,rules,expected",
    [
        (("7S", "9H"), "9", H17_LS, Action.SURRENDER),    # 16 v 9
        (("7S", "9H"), "10", H17_LS, Action.SURRENDER),   # 16 v 10
        (("7S", "9H"), "A", H17_LS, Action.SURRENDER),    # 16 v A
        (("7S", "8H"), "10", H17_LS, Action.SURRENDER),   # 15 v 10
        (("7S", "8H"), "A", H17_LS, Action.SURRENDER),    # 15 v A (H17 only)
        (("7S", "8H"), "A", S17_LS, Action.HIT),          # 15 v A (S17: hit)
        (("8S", "9H"), "A", H17_LS, Action.SURRENDER),    # 17 v A (H17 only)
        (("8S", "9H"), "A", S17_LS, Action.STAND),
        (("8S", "8H"), "A", H17_LS, Action.SURRENDER),    # 8,8 v A (H17+LS)
        (("8S", "8H"), "A", S17_LS, Action.SPLIT),
    ],
)
def test_surrender_cells(names, up_key, rules, expected):
    assert decide(hand(names), up(up_key), rules).action is expected


def test_no_surrender_with_three_cards():
    assert decide(hand(["7S", "5H", "4D"]), up("10"), H17_LS).action is Action.HIT


# --- fallbacks and availability ---

def test_double_unavailable_with_three_cards_falls_back():
    # hard 11 in three cards vs 6 -> would double, must hit
    assert decide(hand(["2S", "4H", "5D"]), up("6"), H17).action is Action.HIT
    # soft 18 three cards vs 3 -> Ds falls back to stand
    assert decide(hand(["AS", "3H", "4D"]), up("3"), H17).action is Action.STAND


def test_double_restrictions_10_11():
    r = Rules(double_restrictions="10-11")
    assert decide(hand(["2S", "7H"]), up("5"), r).action is Action.HIT      # 9: no double
    assert decide(hand(["2S", "8H"]), up("5"), r).action is Action.DOUBLE   # 10: ok
    assert decide(hand(["AS", "7H"]), up("5"), r).action is Action.STAND    # soft: no double


def test_das_affects_borderline_splits():
    assert decide(hand(["2S", "2H"]), up("2"), H17).action is Action.SPLIT
    assert decide(hand(["2S", "2H"]), up("2"), NO_DAS).action is Action.HIT
    assert decide(hand(["6S", "6H"]), up("2"), NO_DAS).action is Action.HIT
    assert decide(hand(["4S", "4H"]), up("5"), NO_DAS).action is Action.HIT


def test_post_split_no_das_blocks_double():
    got = decide(hand(["2S", "9H"]), up("6"), NO_DAS, is_post_split=True)
    assert got.action is Action.HIT  # 11 vs 6 would double, DAS off


def test_resplit_aces_disallowed_plays_soft_12_as_hit():
    # soft 12 always hits — it must NOT inherit the A,2 row's doubles
    for up_key in UPS:
        got = decide(hand(["AS", "AH"]), up(up_key), H17, is_post_split=True)
        assert got.action is Action.HIT, f"A,A (no resplit) vs {up_key}: {got.action}"


def test_can_split_false_blocks_split():
    got = decide(hand(["8S", "8H"]), up("6"), H17, can_split=False)
    assert got.action is not Action.SPLIT  # plays as hard 16 -> stand vs 6
    assert got.action is Action.STAND


def test_rejects_short_hand():
    with pytest.raises(ValueError):
        decide(hand(["AS"]), up("6"), H17)
