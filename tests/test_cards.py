import pytest

from src.cards import Card, card, parse_class_name


def test_parses_compact_names():
    assert parse_class_name("10S") == Card("10", "S")
    assert parse_class_name("As") == Card("A", "S")
    assert parse_class_name("kh") == Card("K", "H")
    assert parse_class_name("2c") == Card("2", "C")
    assert parse_class_name("QD") == Card("Q", "D")


def test_parses_wordy_names():
    assert parse_class_name("ace of spades") == Card("A", "S")
    assert parse_class_name("10 of clubs") == Card("10", "C")
    assert parse_class_name("ten of hearts") == Card("10", "H")
    assert parse_class_name("queen_of_diamonds") == Card("Q", "D")


def test_rejects_non_cards():
    assert parse_class_name("joker") is None
    assert parse_class_name("back") is None
    assert parse_class_name("card back") is None
    assert parse_class_name("") is None
    assert parse_class_name("banana") is None


def test_blackjack_values():
    assert card("AS").blackjack_value == 11
    assert card("KS").blackjack_value == 10
    assert card("10D").blackjack_value == 10
    assert card("7C").blackjack_value == 7
    assert card("2H").blackjack_value == 2


def test_ten_valued():
    assert card("JH").is_ten_valued
    assert card("10S").is_ten_valued
    assert not card("9S").is_ten_valued
    assert not card("AS").is_ten_valued


def test_card_helper_raises_on_junk():
    with pytest.raises(ValueError):
        card("XX")
