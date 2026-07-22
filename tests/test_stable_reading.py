"""Debounce/dedupe state machine tests with synthetic detection sequences."""
from src.cards import card
from src.stable import (
    EventKind,
    RawDetection,
    StableTracker,
    cluster_boxes,
    count_instances,
)
from src.zones import Zone


def det(name, zone=Zone.PLAYER, box=(100, 500, 140, 560), conf=0.9):
    return RawDetection(card=card(name), zone=zone, box=box, confidence=conf)


# --- clustering (pure) ---

def test_two_nearby_boxes_are_one_card():
    boxes = [(100, 100, 140, 160), (150, 170, 190, 230)]  # ~86px apart
    assert len(cluster_boxes(boxes, merge_dist=140)) == 1


def test_two_far_boxes_are_two_cards():
    boxes = [(100, 100, 140, 160), (600, 100, 640, 160)]
    assert len(cluster_boxes(boxes, merge_dist=140)) == 2


def test_close_up_card_corners_merge_via_scale():
    """Real-world regression (live test 2026-07-21): a card near the camera had
    its two corner boxes ~190px apart — beyond the 140px floor — and became a
    phantom duplicate. With merge_scale, big boxes widen the threshold."""
    corners = [(490, 390, 520, 440), (590, 540, 620, 600)]  # ~186px apart, ~55px tall
    assert len(cluster_boxes(corners, merge_dist=140, merge_scale=4.0)) == 1
    # far-away cards have small boxes: the scale term stays below the floor and
    # two genuinely separate cards at 500px stay separate
    small = [(100, 100, 120, 130), (600, 100, 620, 130)]
    assert len(cluster_boxes(small, merge_dist=140, merge_scale=4.0)) == 2


def test_transitive_chain_merges_into_one_cluster():
    boxes = [(0, 0, 40, 60), (100, 0, 140, 60), (200, 0, 240, 60)]  # a-b-c chain
    assert len(cluster_boxes(boxes, merge_dist=120)) == 1


def test_card_straddling_the_zone_line_is_one_card():
    """Live regression (2026-07-21): a 2D on the boundary had one corner in
    each zone and was counted twice. Corners must merge zone-blind, with the
    merged card's zone taken from the cluster centre vs split_y."""
    straddle = [
        det("2D", Zone.DEALER, box=(500, 280, 530, 330)),  # corner above line
        det("2D", Zone.PLAYER, box=(560, 350, 590, 400)),  # corner below line
    ]
    counts = count_instances(straddle, merge_dist=140, merge_scale=4.0, split_y=324)
    assert sum(counts.values()) == 1
    assert counts == {(card("2D"), Zone.PLAYER): 1}  # centroid y=340 > 324
    # same geometry but the card sits clearly above the line -> DEALER
    counts = count_instances(straddle, merge_dist=140, merge_scale=4.0, split_y=400)
    assert counts == {(card("2D"), Zone.DEALER): 1}


def test_count_instances_separates_same_card_in_both_zones():
    detections = [
        det("KS", Zone.PLAYER, box=(100, 500, 140, 560)),
        det("KS", Zone.DEALER, box=(100, 50, 140, 110)),
    ]
    counts = count_instances(detections, merge_dist=140)
    assert counts[(card("KS"), Zone.PLAYER)] == 1
    assert counts[(card("KS"), Zone.DEALER)] == 1


def test_count_instances_two_copies_far_apart_in_one_zone():
    detections = [
        det("KS", box=(100, 500, 140, 560)),
        det("KS", box=(700, 500, 740, 560)),
    ]
    assert count_instances(detections, merge_dist=140)[(card("KS"), Zone.PLAYER)] == 2


# --- debounce over time ---

def test_card_confirmed_only_after_confirm_frames():
    tracker = StableTracker(confirm_frames=3, forget_frames=5)
    s1 = tracker.update([det("7H")])
    s2 = tracker.update([det("7H")])
    assert s1.total_cards == 0 and s2.total_cards == 0
    s3 = tracker.update([det("7H")])
    assert s3.cards(Zone.PLAYER) == (card("7H"),)
    assert [e.kind for e in s3.events] == [EventKind.ADDED]


def test_one_frame_flicker_never_confirms():
    tracker = StableTracker(confirm_frames=3, forget_frames=5)
    tracker.update([det("7H")])
    state = tracker.update([])  # gone next frame
    assert state.total_cards == 0
    for _ in range(5):
        state = tracker.update([])
    assert state.total_cards == 0 and not state.events


def test_occlusion_gap_shorter_than_forget_keeps_card():
    tracker = StableTracker(confirm_frames=2, forget_frames=4)
    for _ in range(2):
        tracker.update([det("AS")])
    for _ in range(4):  # hand waves over the table
        state = tracker.update([])
        assert state.cards(Zone.PLAYER) == (card("AS"),)
    state = tracker.update([det("AS")])  # reappears — no new ADDED event
    assert state.cards(Zone.PLAYER) == (card("AS"),)
    assert not state.events


def test_removed_after_forget_frames():
    tracker = StableTracker(confirm_frames=2, forget_frames=3)
    for _ in range(2):
        tracker.update([det("AS")])
    for _ in range(3):
        tracker.update([])
    state = tracker.update([])  # 4th miss > forget_frames
    assert state.total_cards == 0
    assert [e.kind for e in state.events] == [EventKind.REMOVED]


def test_two_corners_of_one_card_confirm_as_one_instance():
    tracker = StableTracker(confirm_frames=2, forget_frames=5, merge_dist=140)
    frame = [
        det("QD", box=(100, 500, 140, 560)),
        det("QD", box=(160, 570, 200, 630)),  # second corner, nearby
    ]
    tracker.update(frame)
    state = tracker.update(frame)
    assert state.cards(Zone.PLAYER) == (card("QD"),)
    assert len(state.events) == 1


def test_second_identical_card_gets_its_own_added_event():
    tracker = StableTracker(confirm_frames=2, forget_frames=5, merge_dist=140)
    one = [det("KS", box=(100, 500, 140, 560))]
    two = one + [det("KS", box=(700, 500, 740, 560))]
    tracker.update(one)
    state = tracker.update(one)
    assert state.counts[(card("KS"), Zone.PLAYER)] == 1
    tracker.update(two)
    state = tracker.update(two)
    assert state.counts[(card("KS"), Zone.PLAYER)] == 2
    added = [e for e in state.events if e.kind is EventKind.ADDED]
    assert len(added) == 1 and added[0].instance == 2


def test_max_copies_caps_identical_cards_to_deck_count():
    """Single-deck play: a second '8C' is always a misread of a neighbor."""
    tracker = StableTracker(confirm_frames=2, forget_frames=3, max_copies=1)
    two_copies = [
        det("8C", box=(100, 500, 140, 560)),
        det("8C", box=(700, 500, 740, 560)),  # far apart -> 2 clusters
    ]
    state = None
    for _ in range(4):
        state = tracker.update(two_copies)
    assert state.counts[(card("8C"), Zone.PLAYER)] == 1
    # with 6 decks the same input is legitimately two cards
    tracker6 = StableTracker(confirm_frames=2, forget_frames=3, max_copies=6)
    for _ in range(2):
        state = tracker6.update(two_copies)
    assert state.counts[(card("8C"), Zone.PLAYER)] == 2


def test_max_copies_keeps_the_confirmed_zone_on_cross_zone_misread():
    tracker = StableTracker(confirm_frames=2, forget_frames=3, max_copies=1)
    real = det("KS", Zone.PLAYER, box=(100, 500, 140, 560))
    for _ in range(3):
        tracker.update([real])  # KS PLAYER confirmed
    ghost = det("KS", Zone.DEALER, box=(100, 50, 140, 110))
    state = None
    for _ in range(4):
        state = tracker.update([real, ghost])
    assert state.counts.get((card("KS"), Zone.PLAYER)) == 1
    assert (card("KS"), Zone.DEALER) not in state.counts


def test_sporadic_misread_cannot_sustain_a_phantom():
    """Live regression (2026-07-21): a stale card kept 'alive' by an occasional
    misread of a similar card (seen ~1-in-8 frames) never expired, because any
    single sighting fully reset the missed counter. With decay-healing, a card
    seen in only a minority of frames must die."""
    tracker = StableTracker(confirm_frames=2, forget_frames=6)
    for _ in range(2):
        tracker.update([det("QS")])  # confirmed (the card was really there once)

    removed = False
    for cycle in range(20):  # phantom pattern: 1 sighting every 4 frames
        for _ in range(3):
            state = tracker.update([])
            removed = removed or any(
                e.kind is EventKind.REMOVED for e in state.events)
        state = tracker.update([det("QS")])  # the occasional misread
        removed = removed or any(
            e.kind is EventKind.REMOVED for e in state.events)
        if removed:
            break
    assert removed, "a 25%-presence phantom should expire"


def test_mostly_present_card_survives_sporadic_misses():
    tracker = StableTracker(confirm_frames=2, forget_frames=6)
    for _ in range(2):
        tracker.update([det("AS")])
    state = tracker.update([det("AS")])
    for _ in range(15):  # real card: detected 4 of every 5 frames
        state = tracker.update([])
        for _ in range(4):
            state = tracker.update([det("AS")])
    assert state.cards(Zone.PLAYER) == (card("AS"),)


def test_removed_event_carries_the_matching_instance_id():
    """ADDED/REMOVED must pair by permanent id, and ids are never reused."""
    tracker = StableTracker(confirm_frames=1, forget_frames=1, merge_dist=140)
    one = [det("KS", box=(100, 500, 140, 560))]
    two = one + [det("KS", box=(700, 500, 740, 560))]
    s = tracker.update(two)
    assert sorted(e.instance for e in s.events) == [1, 2]
    tracker.update(one)                      # second copy goes missing
    s = tracker.update(one)                  # missed > forget -> removed
    removed = [e for e in s.events if e.kind is EventKind.REMOVED]
    assert [e.instance for e in removed] == [2]   # pairs with its ADDED
    s = tracker.update(two)                  # a new copy appears
    added = [e for e in s.events if e.kind is EventKind.ADDED]
    assert [e.instance for e in added] == [3]     # fresh id, not a reused 2


def test_reset_forgets_the_table():
    tracker = StableTracker(confirm_frames=1, forget_frames=3)
    tracker.update([det("9C")])
    tracker.reset()
    assert tracker.update([]).total_cards == 0
