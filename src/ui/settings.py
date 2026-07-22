"""Stage 6 settings screen: edit game rules on-device with the keyboard.

UP/DOWN select · LEFT/RIGHT change · S save · TAB/ESC cancel.
Saving rewrites config/rules.yaml from a documented template (a .bak copy of
the previous file is kept) and returns the new Rules for the app to apply.
"""
from __future__ import annotations

import shutil
from dataclasses import replace
from pathlib import Path
from typing import List, Optional, Tuple

from ..engines.rules import Rules

_TEMPLATE = """# Game rules — the single source of rule truth. All engines read these via engines/rules.py.
# Edited from the on-device settings screen (previous file saved as rules.yaml.bak).
decks: {decks}
dealer_hits_soft_17: {dealer_hits_soft_17}
double_after_split: {double_after_split}
resplit_limit: {resplit_limit}
resplit_aces: {resplit_aces}
late_surrender: {late_surrender}
blackjack_payout: {blackjack_payout}      # 1.5 = 3:2, 1.2 = 6:5
double_restrictions: {double_restrictions}   # any2 | 9-11 | 10-11
"""

_PAYOUTS = [1.5, 1.2, 1.0, 2.0]
_RESTRICTIONS = ["any2", "9-11", "10-11"]

FIELDS: List[Tuple[str, str]] = [
    ("decks", "Decks in shoe"),
    ("dealer_hits_soft_17", "Dealer hits soft 17"),
    ("double_after_split", "Double after split"),
    ("resplit_limit", "Resplit limit"),
    ("resplit_aces", "Resplit aces"),
    ("late_surrender", "Late surrender"),
    ("blackjack_payout", "Blackjack payout"),
    ("double_restrictions", "Double allowed on"),
]


def step_field(rules: Rules, field: str, direction: int) -> Rules:
    """Pure: return new Rules with `field` stepped by direction (+1/-1)."""
    value = getattr(rules, field)
    if isinstance(value, bool):
        return replace(rules, **{field: not value})
    if field == "decks":
        return replace(rules, **{field: min(8, max(1, value + direction))})
    if field == "resplit_limit":
        return replace(rules, **{field: min(4, max(1, value + direction))})
    if field == "blackjack_payout":
        idx = (_PAYOUTS.index(value) if value in _PAYOUTS else 0) + direction
        return replace(rules, **{field: _PAYOUTS[idx % len(_PAYOUTS)]})
    if field == "double_restrictions":
        idx = (_RESTRICTIONS.index(value) + direction) % len(_RESTRICTIONS)
        return replace(rules, **{field: _RESTRICTIONS[idx]})
    return rules


def save_rules(rules: Rules, path: "str | Path") -> None:
    p = Path(path)
    if p.exists():
        shutil.copy2(p, p.with_suffix(".yaml.bak"))
    yaml_bools = {True: "true", False: "false"}
    p.write_text(
        _TEMPLATE.format(
            decks=rules.decks,
            dealer_hits_soft_17=yaml_bools[rules.dealer_hits_soft_17],
            double_after_split=yaml_bools[rules.double_after_split],
            resplit_limit=rules.resplit_limit,
            resplit_aces=yaml_bools[rules.resplit_aces],
            late_surrender=yaml_bools[rules.late_surrender],
            blackjack_payout=rules.blackjack_payout,
            double_restrictions=rules.double_restrictions,
        ),
        encoding="utf-8",
    )


class SettingsScreen:
    """Modal editor drawn over the dashboard's pygame surface."""

    def __init__(self, screen, rules: Rules) -> None:
        import pygame

        self._pg = pygame
        self._screen = screen
        self._w, self._h = screen.get_size()
        self._font = pygame.font.SysFont("arial,dejavusans", int(self._h * 0.04))
        self._font_small = pygame.font.SysFont("arial,dejavusans", int(self._h * 0.028))
        self.rules = rules
        self._selected = 0
        self.done = False          # exited without saving
        self.saved: Optional[Rules] = None  # set when user saves
        self.quit_requested = False  # window close while modal open = quit the app

    def handle_events(self) -> None:
        pg = self._pg
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
                self.quit_requested = True
            elif event.type == pg.KEYDOWN:
                if event.key in (pg.K_ESCAPE, pg.K_TAB):
                    self.done = True
                elif event.key == pg.K_UP:
                    self._selected = (self._selected - 1) % len(FIELDS)
                elif event.key == pg.K_DOWN:
                    self._selected = (self._selected + 1) % len(FIELDS)
                elif event.key == pg.K_LEFT:
                    self.rules = step_field(self.rules, FIELDS[self._selected][0], -1)
                elif event.key == pg.K_RIGHT:
                    self.rules = step_field(self.rules, FIELDS[self._selected][0], +1)
                elif event.key == pg.K_s:
                    self.saved = self.rules
                    self.done = True

    def render(self) -> None:
        pg = self._pg
        self._screen.fill((10, 30, 18))
        title = self._font.render("Game Rules", True, (230, 190, 90))
        self._screen.blit(title, (self._w // 2 - title.get_width() // 2, int(self._h * 0.06)))
        y = int(self._h * 0.18)
        for i, (field, label) in enumerate(FIELDS):
            value = getattr(self.rules, field)
            if isinstance(value, bool):
                value = "yes" if value else "no"
            color = (240, 240, 235) if i != self._selected else (110, 200, 110)
            prefix = "▶ " if i == self._selected else "   "
            line = self._font.render(f"{prefix}{label}:  {value}", True, color)
            self._screen.blit(line, (int(self._w * 0.18), y))
            y += int(self._h * 0.075)
        hint = self._font_small.render(
            "UP/DOWN select · LEFT/RIGHT change · S save · TAB cancel",
            True, (150, 155, 150))
        self._screen.blit(hint, (self._w // 2 - hint.get_width() // 2,
                                 self._h - int(self._h * 0.08)))
        pg.display.flip()
