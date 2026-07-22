from src.cards import card
from src.session import ShoeSession
from src.stable import CardEvent, EventKind
from src.zones import Zone


def added(name, instance=1):
    return CardEvent(EventKind.ADDED, card(name), Zone.PLAYER, instance)


def test_fresh_shoe_composition():
    s = ShoeSession(decks=6)
    comp = s.remaining_composition()
    assert comp["10"] == 96  # 16 ten-values per deck
    assert comp["A"] == 24
    assert comp["5"] == 24
    assert sum(comp.values()) == 312


def test_seen_cards_reduce_composition():
    s = ShoeSession(decks=6)
    s.apply_events((added("KS"), added("10H"), added("AS"), added("5D")))
    comp = s.remaining_composition()
    assert comp["10"] == 94  # K and 10 share the ten bucket
    assert comp["A"] == 23
    assert comp["5"] == 23


def test_composition_survives_end_hand():
    s = ShoeSession(decks=6)
    s.apply_events((added("KS"),))
    s.end_hand()
    assert s.remaining_composition()["10"] == 95


def test_new_shoe_restores_composition():
    s = ShoeSession(decks=6)
    s.apply_events((added("KS"),))
    s.new_shoe()
    assert s.remaining_composition()["10"] == 96


def test_composition_floors_at_zero():
    s = ShoeSession(decks=1)
    for i in range(6):  # more aces than a single deck holds
        s.apply_events((added("AS", instance=i + 1),))
    assert s.remaining_composition()["A"] == 0
