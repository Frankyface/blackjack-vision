# Stage 5 — Win Probability / EV  (sketch)

## Goal
The "wow" math: live win % for the current hand and expected value per available action,
shown in the UI alongside the advice.

## Likely features (to be defined when Stage 4 completes)
- [ ] EV engine — per-action EV for the current (hand, up-card, rules, remaining-deck
      composition); approach TBD: exact recursive dealer-outcome computation vs Monte Carlo.
      Composition-aware (uses the Stage 3 ledger) if performance allows on the Pi.
- [ ] Probability UI — win % + EV bars per action, readable at a glance, no advice-panel clutter.

## Definition of done (sketch)
- [ ] EV outputs validated in tests against published/simulated benchmarks (e.g. known EVs for
      standard hands) within an agreed tolerance.
- [ ] Live on the Pi without breaking the ≤ 2 s advice budget (EV may lag advice slightly if
      needed — advice first, always).

Sketch by design — do NOT flesh out before Stage 4 is done (progressive elaboration).
