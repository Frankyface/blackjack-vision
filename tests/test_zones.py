import pytest

from src.zones import Zone, assign_zone


def test_clearly_top_is_dealer():
    assert assign_zone(center_y=50, frame_height=720, split=0.45) is Zone.DEALER


def test_clearly_bottom_is_player():
    assert assign_zone(center_y=700, frame_height=720, split=0.45) is Zone.PLAYER


def test_exactly_on_the_line_is_player():
    assert assign_zone(center_y=0.45 * 720, frame_height=720, split=0.45) is Zone.PLAYER


def test_just_above_the_line_is_dealer():
    assert assign_zone(center_y=0.45 * 720 - 1, frame_height=720, split=0.45) is Zone.DEALER


def test_moved_boundary_changes_assignment():
    y = 300  # dealer under the default split of 0.45 (line at 324)
    assert assign_zone(y, 720, 0.45) is Zone.DEALER
    assert assign_zone(y, 720, 0.30) is Zone.PLAYER  # line moved up past it


@pytest.mark.parametrize("bad_split", [0.0, 1.0, -0.2, 1.5])
def test_invalid_split_rejected(bad_split):
    with pytest.raises(ValueError):
        assign_zone(100, 720, bad_split)


def test_invalid_frame_height_rejected():
    with pytest.raises(ValueError):
        assign_zone(100, 0, 0.45)
