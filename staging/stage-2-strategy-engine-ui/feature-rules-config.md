# Feature: Rules config
_Stage: stage-2-strategy-engine-ui · Status: verified done_

## Goal
All game-rule knobs in one validated `config/rules.yaml`, read at startup by every engine.
Shipped default: 6 decks, dealer hits soft 17, DAS allowed, blackjack pays 3:2.

## Success Criteria
- [x] Schema covers at least: decks, dealer_hits_soft_17, double_after_split, resplit_limit,
      resplit_aces, late_surrender, blackjack_payout, double_restrictions.
- [x] Invalid config (bad type, unknown key, out-of-range) fails fast at startup with a clear
      message naming the offending field.
- [x] Engines receive an immutable Rules object — no engine reads the YAML directly.
- [x] Unit tests: defaults load, each validation failure case, round-trip of a non-default file.

## How We'll Verify
`pytest tests/test_rules_config.py` green; then deliberately break the YAML (typo a key, set
decks: 0), run the app, confirm the startup error names the field. Log results.

## Verification Log
**2026-07-21 (Claude):** `src/engines/rules.py` — frozen `Rules` dataclass, validation in
`__post_init__`, `load_rules()` YAML loader rejecting unknown keys. `pytest
tests/test_rules_config.py` → 14 tests green (defaults, shipped file loads, every
invalid-value case names the field, missing file, non-mapping YAML, round-trip).
Live break-the-file check executed: set `decks: 0` in config/rules.yaml, ran
`python -m src.app --selftest` → exit 1 with `RulesError: decks: must be an integer 1-8,
got 0`; file restored and reload confirmed (6 decks). All criteria met → verified done.

## Open Questions
- none yet — revisit when starting.

## Notes & Decisions
- Keep game rules (`rules.yaml`) separate from app settings (`app.yaml` — camera, zones, UI).
