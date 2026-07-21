# Stage 2 — Strategy Engine + UI

## Goal
Add the brain (a rules-configurable basic-strategy engine, rigorously unit-tested) and the face
(the Pygame camera + advice panel UI). At stage end the device's core loop works on the PC:
deal cards → correct action on screen in under 2 seconds.

## Features
- [ ] `feature-rules-config.md` — `config/rules.yaml` schema, validation, defaults
- [ ] `feature-strategy-engine.md` — basic strategy, chart-tested per rule set
- [ ] `feature-advice-ui.md` — Pygame fullscreen: camera + boxes left, big advice right

## Definition of done (testable checklist)
- [ ] `pytest` green, including the full published-chart fixture tests for at least
      6-deck H17 DAS (default config) and 6-deck S17 (the alternate).
- [ ] Editing `config/rules.yaml` (H17→S17) flips the engine's advice on a known
      divergent hand (e.g. A,7 vs dealer 2) without code changes.
- [ ] Live PC demo: 10 dealt hands, each shows the correct action (checked against a printed
      chart) within 2 s of the last card landing.
- [ ] Hands beyond 2 cards work: hit, re-advise, until stand/bust — shown live.
- [ ] All three feature files `verified done` with log entries.
