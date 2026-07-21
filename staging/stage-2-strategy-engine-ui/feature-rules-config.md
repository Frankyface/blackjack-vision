# Feature: Rules config
_Stage: stage-2-strategy-engine-ui · Status: not started_

## Goal
All game-rule knobs in one validated `config/rules.yaml`, read at startup by every engine.
Shipped default: 6 decks, dealer hits soft 17, DAS allowed, blackjack pays 3:2.

## Success Criteria
- [ ] Schema covers at least: decks, dealer_hits_soft_17, double_after_split, resplit_limit,
      resplit_aces, late_surrender, blackjack_payout, double_restrictions.
- [ ] Invalid config (bad type, unknown key, out-of-range) fails fast at startup with a clear
      message naming the offending field.
- [ ] Engines receive an immutable Rules object — no engine reads the YAML directly.
- [ ] Unit tests: defaults load, each validation failure case, round-trip of a non-default file.

## How We'll Verify
`pytest tests/test_rules_config.py` green; then deliberately break the YAML (typo a key, set
decks: 0), run the app, confirm the startup error names the field. Log results.

## Verification Log
_(empty)_

## Open Questions
- none yet — revisit when starting.

## Notes & Decisions
- Keep game rules (`rules.yaml`) separate from app settings (`app.yaml` — camera, zones, UI).
