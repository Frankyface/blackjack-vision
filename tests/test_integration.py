"""End-to-end pipeline test with synthetic detections — no camera, no UI.

Simulates dealing a hand the way frames would arrive from the detector and
checks that tracking, counting, advice, EV, and round scoring all connect.
"""
from src.app import compute_decision, compute_ev
from src.cards import card
from src.engines.rules import Rules
from src.session import ShoeSession
from src.stable import RawDetection, StableTracker
from src.tracker import Outcome, RoundTracker, SessionStats
from src.zones import Zone

RULES = Rules()  # 6-deck H17 DAS


def det(name, zone, x=100):
    y = (100, 600)[zone is Zone.PLAYER]
    return RawDetection(card=card(name), zone=zone,
                        box=(x, y, x + 40, y + 60), confidence=0.9)


class _FakeState:
    pass


def test_full_hand_through_the_pipeline():
    tracker = StableTracker(confirm_frames=3, forget_frames=5, merge_dist=140)
    session = ShoeSession(decks=RULES.decks)
    rounds = RoundTracker(empty_updates_to_end=5)
    stats = SessionStats()

    # deal: player 10S 6H, dealer 10D — the classic hard 16 vs 10
    frame = [det("10S", Zone.PLAYER, 100), det("6H", Zone.PLAYER, 300),
             det("10D", Zone.DEALER, 100)]
    state = None
    for _ in range(3):
        state = tracker.update(frame)
        session.apply_events(state.events)
        assert rounds.update(state) is None

    assert state.cards(Zone.PLAYER) == (card("10S"), card("6H"))
    assert state.cards(Zone.DEALER) == (card("10D"),)
    assert session.count.running == -1  # +0(6) -1(10) -1(10) ... wait: 10S -1, 6H +1, 10D -1

    action, total, up = compute_decision(state, RULES)
    assert action == "HIT" and total == "hard 16" and up == "10"
    stats.observe(action, 2)

    ev, win = compute_ev(state, RULES, session, {})
    assert set(ev) >= {"HIT", "STAND"}
    assert -0.65 < ev["HIT"] < -0.40 and win is not None

    # player hits and draws 4C -> hard 20, advice flips to STAND
    frame.append(det("4C", Zone.PLAYER, 500))
    for _ in range(3):
        state = tracker.update(frame)
        session.apply_events(state.events)
        rounds.update(state)
    action, total, up = compute_decision(state, RULES)
    assert action == "STAND" and total == "hard 20"
    stats.observe(action, 3)
    assert stats.decisions_total == 1 and stats.decisions_followed == 1  # hit taken

    # dealer reveals + draws: 10D 9C -> 19. Then table cleared.
    frame.append(det("9C", Zone.DEALER, 300))
    for _ in range(3):
        state = tracker.update(frame)
        session.apply_events(state.events)
        rounds.update(state)

    # table cleared: cards linger for forget_frames, then the empty streak
    # runs — exactly as the app's loop drives it every frame
    result = None
    guard = 0
    while result is None and guard < 40:
        state = tracker.update([])
        session.apply_events(state.events)
        result = rounds.update(state)
        guard += 1
    assert result is not None
    assert result.outcome is Outcome.WIN  # 20 beats 19
    stats.record_result(result)
    session.end_hand()

    assert stats.hands == 1 and stats.wins == 1
    assert stats.accuracy == 1.0  # followed HIT, then round ended on STAND
    assert session.count.cards_seen == 5
    # composition reflects what crossed the table
    comp = session.remaining_composition()
    assert comp["10"] == 16 * 6 - 2  # 10S and 10D
    assert comp["9"] == 24 - 1       # 9C
    assert comp["6"] == 24 - 1       # 6H
    assert comp["4"] == 24 - 1       # 4C


def test_count_arithmetic_for_that_hand():
    # 10S(-1) 6H(+1) 10D(-1) 4C(+1) 9C(0) = 0
    session = ShoeSession(decks=6)
    from src.stable import CardEvent, EventKind

    for i, name in enumerate(("10S", "6H", "10D", "4C", "9C")):
        session.apply_events(
            (CardEvent(EventKind.ADDED, card(name), Zone.PLAYER, i + 1),)
        )
    assert session.count.running == 0
