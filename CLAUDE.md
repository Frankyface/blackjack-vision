# blackjack-vision — CLAUDE.md

Blackjack trainer: a webcam + YOLOv8 reads real cards on the table; a Raspberry Pi 5 + HDMI
screen shows the correct play, the running/true count, and win odds.
Stack: Python 3.9 on the PC / 3.11 on the Pi (write 3.9-compatible code) · Ultralytics
YOLOv8-nano (pretrained weights from cadyze/card-vision, MIT) · OpenCV · Pygame fullscreen
UI · pytest · NCNN export for Pi inference.

## First actions every session
1. Read `handoff.md` FIRST, then follow its Pointer to the active stage/feature file.
2. Doc model: CLAUDE.md = the constant · handoff.md = head of the list (current state) ·
   `staging/*/feature-*.md` = the ordered work list · `docs/` = the full vision.

## Standing command
When the user says "update all relevant files", run `/sync-docs`.

## Conventions
- Python, type hints on public functions, small modules (<400 lines).
- Pure logic (strategy / counting / EV engines) lives apart from I/O (camera, UI) so it is
  unit-testable. Engines return new state — never mutate inputs.
- All game-rule-dependent values come from `config/rules.yaml`. Never hardcode them.
- Run the app (PC, via .venv): `python -m src.app` (`--selftest` headless smoke,
  `--camera-test` webcam check, `--run-seconds N` timed run) · Run tests: `pytest`
- Fresh clone: `pip install -r requirements.txt` + `python scripts/fetch_model.py`
  (models/ is gitignored).
- Verification convention: math engines → pytest required (80%+ on engine modules);
  CV/UI features → live webcam demo, result recorded in the feature's Verification Log.
- Git: work on `main`, commit at every verified-green checkpoint, conventional commits
  (feat/fix/docs/test/refactor/chore). No AI-attribution lines in commits or PRs.

## Verification protocol (full text: .claude/commands/verify.md)
- Status state machine: `not started → in progress → awaiting verification → verified done`.
- `verified done` REQUIRES a dated entry in that feature's Verification Log — no exceptions.
- If verification is blocked (missing hardware, needs the user), status stays
  `awaiting verification` and the blocker is added to `help.md`.
- `/verify` runs this loop on the active feature.

## Truth & budgets
- Truth hierarchy: actual code/system state > handoff.md > stage files > docs/master_plan.md.
  When docs and reality conflict, reality wins — fix the docs and say so.
- `handoff.md` hard budget: ≤60 lines, every section rewritten in place on each sync
  ("Things I've Changed" keeps only the last 5; "Watch Out" at most 3).

## Scope guardrail
Home practice trainer only. Never add features intended to aid play inside a real casino —
using such a device there is illegal in many jurisdictions.
