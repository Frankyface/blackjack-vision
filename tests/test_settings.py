from src.engines.rules import Rules, load_rules
from src.ui.settings import save_rules, step_field


def test_step_bool_toggles():
    r = Rules()
    assert step_field(r, "dealer_hits_soft_17", 1).dealer_hits_soft_17 is False
    assert r.dealer_hits_soft_17 is True  # original untouched


def test_step_decks_clamped():
    r = Rules(decks=8)
    assert step_field(r, "decks", 1).decks == 8
    assert step_field(r, "decks", -1).decks == 7
    assert step_field(Rules(decks=1), "decks", -1).decks == 1


def test_step_payout_cycles():
    r = Rules(blackjack_payout=1.5)
    r2 = step_field(r, "blackjack_payout", 1)
    assert r2.blackjack_payout == 1.2
    r3 = step_field(r2, "blackjack_payout", -1)
    assert r3.blackjack_payout == 1.5


def test_step_restrictions_cycles():
    r = Rules(double_restrictions="any2")
    assert step_field(r, "double_restrictions", 1).double_restrictions == "9-11"
    assert step_field(r, "double_restrictions", -1).double_restrictions == "10-11"


def test_save_and_reload_round_trip(tmp_path):
    p = tmp_path / "rules.yaml"
    edited = Rules(decks=2, dealer_hits_soft_17=False, late_surrender=True,
                   blackjack_payout=1.2, double_restrictions="10-11")
    save_rules(edited, p)
    assert load_rules(p) == edited


def test_save_keeps_backup(tmp_path):
    p = tmp_path / "rules.yaml"
    save_rules(Rules(), p)
    save_rules(Rules(decks=4), p)
    backup = tmp_path / "rules.yaml.bak"
    assert backup.exists()
    assert load_rules(backup) == Rules()
    assert load_rules(p).decks == 4
