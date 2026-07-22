"""Pygame fullscreen dashboard: camera + boxes left, advice/count/EV right.

The dashboard is deliberately dumb: it renders whatever ViewModel it's given
and reports key presses. All game logic lives in app.py and the engines.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

BG = (12, 60, 30)          # felt green
PANEL = (8, 40, 22)
WHITE = (240, 240, 235)
GOLD = (230, 190, 90)
RED = (220, 90, 80)
BLUE = (110, 170, 240)
GREY = (150, 155, 150)
ACTION_COLORS = {
    "HIT": (110, 200, 110),
    "STAND": (220, 90, 80),
    "DOUBLE": (230, 190, 90),
    "SPLIT": (110, 170, 240),
    "SURRENDER": (200, 140, 220),
}


@dataclass
class ViewModel:
    frame: object = None                         # BGR numpy array or None
    boxes: Sequence[Tuple[Tuple[float, float, float, float], str]] = ()
    zone_split_y: int = 0
    player_cards: Sequence[str] = ()
    dealer_cards: Sequence[str] = ()
    action: Optional[str] = None                 # "HIT" ... or None = waiting
    player_total: str = ""
    dealer_up: str = ""
    running_count: int = 0
    true_count: float = 0.0
    decks_remaining: float = 0.0
    bet_units: int = 1
    bet_amount: int = 0
    hands_played: int = 0
    ev: Dict[str, float] = field(default_factory=dict)   # action -> EV (stage 5)
    win_prob: Optional[float] = None
    stats_line: str = ""                          # stage 6
    status: str = ""                              # transient message line
    fps: float = 0.0
    paused: bool = False
    show_fps: bool = True


class Dashboard:
    def __init__(self, fullscreen: bool = False, size: Tuple[int, int] = (1280, 720)) -> None:
        import pygame  # lazy

        self._pg = pygame
        pygame.init()
        pygame.display.set_caption("blackjack-vision")
        flags = pygame.FULLSCREEN if fullscreen else 0
        self._screen = pygame.display.set_mode((0, 0) if fullscreen else size, flags)
        self._w, self._h = self._screen.get_size()
        self._cam_w = int(self._w * 0.55)
        self._font_big = pygame.font.SysFont("arialblack,dejavusans", int(self._h * 0.16))
        self._font_mid = pygame.font.SysFont("arial,dejavusans", int(self._h * 0.045))
        self._font_small = pygame.font.SysFont("arial,dejavusans", int(self._h * 0.03))

    # ---- input ----

    def poll(self) -> List[str]:
        """Return UI intents: QUIT, END_HAND, NEW_SHOE, PAUSE, SETTINGS."""
        pg = self._pg
        intents: List[str] = []
        for event in pg.event.get():
            if event.type == pg.QUIT:
                intents.append("QUIT")
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    intents.append("QUIT")
                elif event.key == pg.K_SPACE:
                    intents.append("END_HAND")
                elif event.key == pg.K_n:
                    intents.append("NEW_SHOE")
                elif event.key == pg.K_p:
                    intents.append("PAUSE")
                elif event.key == pg.K_TAB:
                    intents.append("SETTINGS")
        return intents

    # ---- rendering ----

    def render(self, vm: ViewModel) -> None:
        pg = self._pg
        self._screen.fill(BG)
        self._draw_camera(vm)
        self._draw_panel(vm)
        pg.display.flip()

    def _draw_camera(self, vm: ViewModel) -> None:
        pg = self._pg
        area = pg.Rect(0, 0, self._cam_w, self._h)
        pg.draw.rect(self._screen, PANEL, area)
        if vm.frame is not None:
            import cv2
            import numpy as np  # noqa: F401 — frame is numpy

            fh, fw = vm.frame.shape[:2]
            scale = min(self._cam_w / fw, self._h / fh)
            disp_w, disp_h = int(fw * scale), int(fh * scale)
            annotated = vm.frame.copy()
            for box, label in vm.boxes:
                x1, y1, x2, y2 = (int(v) for v in box)
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (80, 220, 120), 2)
                cv2.putText(annotated, label, (x1, max(y1 - 6, 12)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 220, 120), 2)
            if vm.zone_split_y:
                cv2.line(annotated, (0, vm.zone_split_y), (fw, vm.zone_split_y),
                         (230, 190, 90), 2)
                cv2.putText(annotated, "DEALER", (10, vm.zone_split_y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (230, 190, 90), 2)
                cv2.putText(annotated, "PLAYER", (10, vm.zone_split_y + 26),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (230, 190, 90), 2)
            rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            surf = pg.image.frombuffer(rgb.tobytes(), (fw, fh), "RGB")
            surf = pg.transform.smoothscale(surf, (disp_w, disp_h))
            self._screen.blit(surf, ((self._cam_w - disp_w) // 2, (self._h - disp_h) // 2))
        else:
            self._center_text("no camera frame", self._font_mid, GREY,
                              self._cam_w // 2, self._h // 2)
        if vm.show_fps and vm.fps:
            self._text(f"{vm.fps:.1f} fps", self._font_small, GREY, 10, self._h - 30)

    def _draw_panel(self, vm: ViewModel) -> None:
        pg = self._pg
        x0 = self._cam_w
        pw = self._w - x0
        pad = int(pw * 0.06)
        y = pad

        # Dealer / player card lines
        self._text(f"Dealer: {' '.join(vm.dealer_cards) or '—'}"
                   + (f"  ({vm.dealer_up})" if vm.dealer_up else ""),
                   self._font_mid, WHITE, x0 + pad, y)
        y += int(self._h * 0.06)
        self._text(f"You: {' '.join(vm.player_cards) or '—'}"
                   + (f"  ({vm.player_total})" if vm.player_total else ""),
                   self._font_mid, WHITE, x0 + pad, y)
        y += int(self._h * 0.08)

        # THE action word
        if vm.paused:
            word, color = "PAUSED", GREY
        elif vm.action:
            word, color = vm.action, ACTION_COLORS.get(vm.action, WHITE)
        else:
            word, color = "…", GREY
        self._center_text(word, self._font_big, color, x0 + pw // 2,
                          y + int(self._h * 0.11))
        y += int(self._h * 0.25)

        # EV bars (stage 5) — only when provided
        if vm.ev:
            best = max(vm.ev.values())
            for action, value in sorted(vm.ev.items(), key=lambda kv: -kv[1]):
                bar_w = int((pw - 2 * pad) * min(max((value + 1) / 2, 0.02), 1.0))
                color = ACTION_COLORS.get(action, GREY)
                pg.draw.rect(self._screen, color if value == best else PANEL,
                             (x0 + pad, y, bar_w, int(self._h * 0.028)))
                self._text(f"{action:<9} {value:+.3f}", self._font_small,
                           WHITE, x0 + pad + 4, y)
                y += int(self._h * 0.036)
            if vm.win_prob is not None:
                self._text(f"win ~{vm.win_prob * 100:.0f}%", self._font_small,
                           GOLD, x0 + pad, y)
            y += int(self._h * 0.05)

        # Count block
        self._text(f"Running {vm.running_count:+d}   True {vm.true_count:+.1f}",
                   self._font_mid, GOLD, x0 + pad, y)
        y += int(self._h * 0.055)
        self._text(
            f"{vm.decks_remaining:.1f} decks left · bet {vm.bet_units}u"
            + (f" (${vm.bet_amount})" if vm.bet_amount else "")
            + f" · hand #{vm.hands_played + 1}",
            self._font_small, WHITE, x0 + pad, y)
        y += int(self._h * 0.05)

        if vm.stats_line:
            self._text(vm.stats_line, self._font_small, BLUE, x0 + pad, y)
            y += int(self._h * 0.045)

        if vm.status:
            self._text(vm.status, self._font_small, RED, x0 + pad, y)

        self._text("SPACE end hand · N new shoe · P pause · TAB settings · ESC quit",
                   self._font_small, GREY, x0 + pad, self._h - int(self._h * 0.05))

    # ---- helpers ----

    @property
    def screen(self):
        """The pygame surface — used by the modal settings screen."""
        return self._screen

    def _text(self, s, font, color, x, y):
        self._screen.blit(font.render(s, True, color), (x, y))

    def _center_text(self, s, font, color, cx, cy):
        surf = font.render(s, True, color)
        self._screen.blit(surf, (cx - surf.get_width() // 2, cy - surf.get_height() // 2))

    def close(self) -> None:
        self._pg.quit()
