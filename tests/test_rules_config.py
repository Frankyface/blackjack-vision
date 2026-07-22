import pytest

from src.engines.rules import Rules, RulesError, load_rules, rules_from_mapping


def test_defaults_are_the_shipped_game():
    r = Rules()
    assert r.decks == 6 and r.dealer_hits_soft_17 and r.double_after_split
    assert r.blackjack_payout == 1.5 and not r.late_surrender


def test_shipped_rules_yaml_loads(tmp_path):
    # the real shipped file must always be valid
    from pathlib import Path
    r = load_rules(Path(__file__).resolve().parents[1] / "config" / "rules.yaml")
    assert r == Rules()


def test_unknown_key_names_the_key():
    with pytest.raises(RulesError, match="banana"):
        rules_from_mapping({"banana": 1})


@pytest.mark.parametrize(
    "field,value,fragment",
    [
        ("decks", 0, "decks"),
        ("decks", 9, "decks"),
        ("decks", "six", "decks"),
        ("dealer_hits_soft_17", "yes", "dealer_hits_soft_17"),
        ("resplit_limit", 0, "resplit_limit"),
        ("blackjack_payout", 3.0, "blackjack_payout"),
        ("double_restrictions", "whenever", "double_restrictions"),
    ],
)
def test_invalid_values_name_the_field(field, value, fragment):
    data = {field: value}
    with pytest.raises(RulesError, match=fragment):
        rules_from_mapping(data)


def test_missing_file_is_a_clear_error(tmp_path):
    with pytest.raises(RulesError, match="not found"):
        load_rules(tmp_path / "nope.yaml")


def test_non_mapping_yaml_rejected(tmp_path):
    p = tmp_path / "rules.yaml"
    p.write_text("- just\n- a list\n", encoding="utf-8")
    with pytest.raises(RulesError, match="mapping"):
        load_rules(p)


def test_round_trip_non_default(tmp_path):
    p = tmp_path / "rules.yaml"
    p.write_text(
        "decks: 2\ndealer_hits_soft_17: false\nlate_surrender: true\n",
        encoding="utf-8",
    )
    r = load_rules(p)
    assert r.decks == 2 and not r.dealer_hits_soft_17 and r.late_surrender
    assert not r.uses_multideck_chart
