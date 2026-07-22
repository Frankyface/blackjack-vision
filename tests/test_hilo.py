import pytest

from src.cards import card
from src.engines.hilo import CountState, bet_units, hilo_value


def test_hilo_values():
    assert hilo_value(card("2S")) == 1
    assert hilo_value(card("6D")) == 1
    assert hilo_value(card("7H")) == 0
    assert hilo_value(card("9C")) == 0
    assert hilo_value(card("10S")) == -1
    assert hilo_value(card("KD")) == -1
    assert hilo_value(card("AS")) == -1


def test_see_is_immutable():
    s0 = CountState(decks=6)
    s1 = s0.see(card("5H"))
    assert s0.running == 0 and s0.cards_seen == 0
    assert s1.running == 1 and s1.cards_seen == 1


def test_full_deck_counts_to_zero():
    s = CountState(decks=1)
    for rank in ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"):
        for suit in "SHDC":
            s = s.see(card(f"{rank}{suit}"))
    assert s.running == 0 and s.cards_seen == 52


def test_true_count_uses_decks_remaining():
    s = CountState(decks=6, running=6, cards_seen=52)  # 5 decks left
    assert s.decks_remaining == 5.0
    assert s.true_count == pytest.approx(1.2)
    assert s.true_count_floor == 1


def test_true_count_floors_toward_negative_infinity():
    s = CountState(decks=6, running=-3, cards_seen=104)  # 4 decks left
    assert s.true_count == pytest.approx(-0.75)
    assert s.true_count_floor == -1


def test_decks_remaining_never_below_half():
    s = CountState(decks=1, running=0, cards_seen=51)
    assert s.decks_remaining == 0.5


def test_decks_remaining_floors_to_half_deck():
    # 13 cards from 6 decks: exactly 5.75 decks physically left -> 5.5 floored;
    # flooring never claims more decks than actually remain
    assert CountState(decks=6, cards_seen=13).decks_remaining == 5.5
    assert CountState(decks=6, cards_seen=26).decks_remaining == 5.5
    assert CountState(decks=6, cards_seen=27).decks_remaining == 5.0


def test_scripted_shoe_checkpoints():
    """A scripted mini-shoe with hand-computed checkpoints."""
    s = CountState(decks=6)
    s = s.see_all([card(n) for n in ("2S", "3D", "4H", "5C", "6S")])  # +5
    assert s.running == 5
    s = s.see_all([card(n) for n in ("KS", "QD", "JH", "10C", "AS")])  # -5
    assert s.running == 0
    s = s.see_all([card(n) for n in ("7S", "8D", "9H")])  # 0
    assert s.running == 0 and s.cards_seen == 13


def test_bet_ramp():
    ramp = {1: 1, 2: 2, 3: 4, 4: 8, 5: 12}
    assert bet_units(-3, ramp) == 1
    assert bet_units(0, ramp) == 1
    assert bet_units(1, ramp) == 1
    assert bet_units(2, ramp) == 2
    assert bet_units(3, ramp) == 4
    assert bet_units(5, ramp) == 12
    assert bet_units(9, ramp) == 12


def test_empty_ramp_rejected():
    with pytest.raises(ValueError):
        bet_units(1, {})
