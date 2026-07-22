from src.cards import card
from src.session import ShoeSession
from src.stable import CardEvent, EventKind
from src.zones import Zone


def added(name, zone=Zone.PLAYER, instance=1):
    return CardEvent(EventKind.ADDED, card(name), zone, instance)


def removed(name, zone=Zone.PLAYER, instance=1):
    return CardEvent(EventKind.REMOVED, card(name), zone, instance)


def test_added_cards_are_counted():
    s = ShoeSession(decks=6)
    s.apply_events((added("5H"), added("KS", Zone.DEALER)))
    assert s.count.running == 0  # +1 -1
    assert s.count.cards_seen == 2


def test_readd_within_hand_not_double_counted():
    s = ShoeSession(decks=6)
    s.apply_events((added("5H"),))
    s.apply_events((removed("5H"),))   # picked up / long occlusion
    s.apply_events((added("5H"),))     # comes back
    assert s.count.running == 1 and s.count.cards_seen == 1


def test_zone_flicker_not_double_counted():
    """A card near the split line dropping from one zone and confirming in the
    other is a relocation, not a second card."""
    s = ShoeSession(decks=6)
    s.apply_events((added("9C", Zone.DEALER),))
    s.apply_events((removed("9C", Zone.DEALER),))
    s.apply_events((added("9C", Zone.PLAYER),))
    assert s.count.cards_seen == 1


def test_two_concurrent_copies_count_separately():
    s = ShoeSession(decks=6)
    s.apply_events((added("KS", instance=1), added("KS", instance=2)))
    assert s.count.running == -2 and s.count.cards_seen == 2


def test_same_card_both_zones_concurrently_counts_twice():
    s = ShoeSession(decks=6)
    s.apply_events((added("9C", Zone.PLAYER), added("9C", Zone.DEALER)))
    assert s.count.cards_seen == 2


def test_end_hand_keeps_count_and_next_hand_copy_counts():
    s = ShoeSession(decks=6)
    s.apply_events((added("5H"),))
    s.apply_events((removed("5H"),))   # dealer collects before hand ends
    s.end_hand()
    assert s.count.running == 1 and s.hands_played == 1
    s.apply_events((added("5H", instance=2),))  # a new physical 5H next hand
    assert s.count.running == 2 and s.count.cards_seen == 2


def test_space_with_cards_still_on_felt_never_double_counts():
    """The reviewed HIGH bug: END HAND pressed while cards remain visible.
    The leftover card's later removal must not open a recount window, and a
    genuinely new copy next hand must still count."""
    s = ShoeSession(decks=6)
    s.apply_events((added("5H"),))
    s.end_hand()                        # SPACE — 5H still on the felt (stale)
    s.apply_events((removed("5H"),))    # dealer finally collects it
    s.apply_events((added("5H", instance=2),))  # new copy dealt this hand
    assert s.count.running == 2 and s.count.cards_seen == 2


def test_stale_card_readd_after_removal_is_ambiguous_and_counts():
    # stale card removed -> its "slot" is consumed; a subsequent identical
    # ADDED is treated as a new card (documented toward-the-count choice)
    s = ShoeSession(decks=6)
    s.apply_events((added("QD"),))
    s.end_hand()
    s.apply_events((removed("QD"), added("QD", instance=2)))
    assert s.count.cards_seen == 2


def test_empty_hand_does_not_increment_hands_played():
    s = ShoeSession(decks=6)
    s.end_hand()
    assert s.hands_played == 0


def test_new_shoe_resets_everything():
    s = ShoeSession(decks=6)
    s.apply_events((added("5H"), added("6D")))
    s.end_hand()
    s.new_shoe()
    assert s.count.running == 0 and s.count.cards_seen == 0
    assert s.hands_played == 0
    s.apply_events((added("5H"),))  # counts again after reset
    assert s.count.running == 1


def test_removal_alone_never_changes_the_count():
    s = ShoeSession(decks=6)
    s.apply_events((added("QD"),))
    s.apply_events((removed("QD"),))
    assert s.count.running == -1 and s.count.cards_seen == 1


def test_full_shoe_scripted_sequence():
    """52 * 6 cards through in hands of ~5; final running count must be 0."""
    s = ShoeSession(decks=6)
    ranks = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
    n = 0
    for copy in (1, 2, 3, 4, 5, 6):
        for rank in ranks:
            for suit in "SHDC":
                s.apply_events((added(f"{rank}{suit}", instance=copy),))
                n += 1
                if n % 5 == 0:
                    s.end_hand()
    s.end_hand()
    assert s.count.cards_seen == 312
    assert s.count.running == 0
    assert s.count.decks_remaining == 0.5
