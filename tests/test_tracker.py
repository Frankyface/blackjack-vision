from src.cards import card
from src.stable import StableState
from src.tracker import Outcome, RoundTracker, SessionStats, score_round
from src.zones import Zone


def table(player=(), dealer=()):
    counts = {}
    for name in player:
        key = (card(name), Zone.PLAYER)
        counts[key] = counts.get(key, 0) + 1
    for name in dealer:
        key = (card(name), Zone.DEALER)
        counts[key] = counts.get(key, 0) + 1
    return StableState(counts=counts, events=())


EMPTY = table()


# --- score_round ---

def test_player_bust_loses_even_if_dealer_busts_too():
    r = score_round(
        (card("10S"), card("9H"), card("5D")),
        (card("10D"), card("6C"), card("KH")),
    )
    assert r.outcome is Outcome.LOSE


def test_player_bust_loses_even_with_hole_card_never_seen():
    # The most common losing outcome: player busts, dealer never reveals.
    r = score_round((card("10S"), card("9H"), card("5D")), (card("10D"),))
    assert r.outcome is Outcome.LOSE


def test_dealer_natural_beats_player_drawn_21():
    r = score_round(
        (card("7S"), card("7H"), card("7D")),
        (card("AD"), card("KC")),
    )
    assert r.outcome is Outcome.LOSE


def test_dealer_bust_wins():
    r = score_round(
        (card("10S"), card("8H")),
        (card("10D"), card("6C"), card("KH")),
    )
    assert r.outcome is Outcome.WIN


def test_higher_total_wins():
    r = score_round((card("10S"), card("9H")), (card("10D"), card("8C")))
    assert r.outcome is Outcome.WIN and r.player_total == 19 and r.dealer_total == 18


def test_equal_totals_push():
    r = score_round((card("10S"), card("9H")), (card("10D"), card("9C")))
    assert r.outcome is Outcome.PUSH


def test_natural_beats_drawn_21():
    r = score_round((card("AS"), card("KH")), (card("7D"), card("7C"), card("7H")))
    assert r.outcome is Outcome.BLACKJACK


def test_both_naturals_push():
    r = score_round((card("AS"), card("KH")), (card("AD"), card("QC")))
    assert r.outcome is Outcome.PUSH


def test_unseen_dealer_hand_is_unscored():
    r = score_round((card("10S"), card("9H")), (card("10D"),))
    assert r.outcome is Outcome.UNSCORED


# --- RoundTracker ---

def test_round_ends_after_sustained_empty_table():
    t = RoundTracker(empty_updates_to_end=3)
    full = table(player=("10S", "9H"), dealer=("8D", "10C"))
    assert t.update(full) is None
    assert t.update(EMPTY) is None
    assert t.update(EMPTY) is None
    result = t.update(EMPTY)
    assert result is not None and result.outcome is Outcome.WIN


def test_brief_empty_flicker_does_not_end_round():
    t = RoundTracker(empty_updates_to_end=3)
    full = table(player=("10S", "9H"), dealer=("8D", "10C"))
    t.update(full)
    t.update(EMPTY)
    t.update(full)  # cards back — not a round end
    for _ in range(2):
        assert t.update(EMPTY) is None
    assert t.update(EMPTY) is not None


def test_empty_table_from_start_never_emits():
    t = RoundTracker(empty_updates_to_end=2)
    for _ in range(10):
        assert t.update(EMPTY) is None


def test_finish_scores_immediately():
    t = RoundTracker(empty_updates_to_end=50)
    t.update(table(player=("10S", "10H"), dealer=("9D", "8C")))
    result = t.finish()
    assert result is not None and result.outcome is Outcome.WIN
    assert t.finish() is None  # nothing left


def test_staggered_zone_cleanup_still_scores():
    """Zones empty at different moments during collection — the last-known
    snapshot per zone must survive (reviewed HIGH bug: most rounds UNSCORED)."""
    t = RoundTracker(empty_updates_to_end=3)
    t.update(table(player=("10S", "9H"), dealer=("8D", "10C")))
    t.update(table(player=(), dealer=("8D", "10C")))   # player collected first
    result = None
    while result is None:
        result = t.update(EMPTY)
    assert result.outcome is Outcome.WIN
    assert result.player_total == 19 and result.dealer_total == 18


def test_finish_with_cards_on_felt_does_not_score_them_twice():
    t = RoundTracker(empty_updates_to_end=2)
    full = table(player=("10S", "10H"), dealer=("9D", "8C"))
    t.update(full)
    assert t.finish() is not None      # SPACE pressed, cards still visible
    t.update(full)                     # same cards still there
    for _ in range(10):
        assert t.update(EMPTY) is None  # collection must NOT emit a 2nd result
    # a fresh deal after the table cleared scores normally again
    t.update(table(player=("9S", "9H"), dealer=("10D", "7C")))
    result = None
    while result is None:
        result = t.update(EMPTY)
    assert result.outcome is Outcome.WIN


# --- SessionStats ---

def make_result(outcome):
    results = {
        Outcome.WIN: (("10S", "9H"), ("10D", "8C")),
        Outcome.LOSE: (("10S", "8H"), ("10D", "9C")),
        Outcome.PUSH: (("10S", "9H"), ("10D", "9C")),
    }
    p, d = results[outcome]
    return score_round(tuple(card(n) for n in p), tuple(card(n) for n in d))


def test_stats_tally_outcomes():
    s = SessionStats()
    s.record_result(make_result(Outcome.WIN))
    s.record_result(make_result(Outcome.LOSE))
    s.record_result(make_result(Outcome.PUSH))
    assert s.hands == 3 and s.wins == 1 and s.losses == 1 and s.pushes == 1


def test_followed_hit_advice_counts_as_followed():
    s = SessionStats()
    s.observe("HIT", 2)
    s.observe("HIT", 3)  # took a card while advice was HIT
    assert s.decisions_total == 1 and s.decisions_followed == 1


def test_ignored_stand_advice_counts_against():
    s = SessionStats()
    s.observe("STAND", 2)
    s.observe("STAND", 3)  # took a card against STAND
    assert s.decisions_total == 1 and s.decisions_followed == 0


def test_standing_on_stand_resolves_at_round_end():
    s = SessionStats()
    s.observe("STAND", 2)
    s.record_result(make_result(Outcome.WIN))
    assert s.decisions_total == 1 and s.decisions_followed == 1
    assert s.accuracy == 1.0


def test_hit_advice_never_taken_resolves_as_not_followed():
    s = SessionStats()
    s.observe("HIT", 2)
    s.record_result(make_result(Outcome.LOSE))
    assert s.decisions_total == 1 and s.decisions_followed == 0


def test_hit_card_confirming_after_hole_card_still_counts_as_followed():
    """Reviewed race: advice goes None (dealer's 2nd card confirmed) before the
    player's hit card confirms — the late growth must still resolve as a hit."""
    s = SessionStats()
    s.observe("HIT", 2)
    s.observe(None, 2)   # hole card appeared -> no advice
    s.observe(None, 3)   # hit card confirms late
    s.record_result(make_result(Outcome.WIN))
    assert s.decisions_total == 1 and s.decisions_followed == 1


def test_detection_dropout_does_not_fabricate_a_decision():
    s = SessionStats()
    s.observe("STAND", 3)
    s.observe("STAND", 2)  # a card flickered out
    s.observe("STAND", 3)  # ...and back — not a new card
    s.record_result(make_result(Outcome.WIN))
    assert s.decisions_total == 1 and s.decisions_followed == 1


def test_summary_line_reads_sensibly():
    s = SessionStats()
    s.record_result(make_result(Outcome.WIN))
    assert "1 hands" in s.summary_line() and "1W" in s.summary_line()
