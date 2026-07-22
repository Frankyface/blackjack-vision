"""Game rules: immutable Rules object + validated YAML loading.

No engine reads rules.yaml directly — everything receives a Rules instance.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

DOUBLE_RESTRICTIONS = ("any2", "9-11", "10-11")


class RulesError(ValueError):
    """Invalid rules config — message always names the offending field."""


@dataclass(frozen=True)
class Rules:
    decks: int = 6
    dealer_hits_soft_17: bool = True
    double_after_split: bool = True
    resplit_limit: int = 3
    resplit_aces: bool = False
    late_surrender: bool = False
    blackjack_payout: float = 1.5
    double_restrictions: str = "any2"

    def __post_init__(self) -> None:
        if not isinstance(self.decks, int) or not 1 <= self.decks <= 8:
            raise RulesError(f"decks: must be an integer 1-8, got {self.decks!r}")
        for name in ("dealer_hits_soft_17", "double_after_split",
                     "resplit_aces", "late_surrender"):
            if not isinstance(getattr(self, name), bool):
                raise RulesError(f"{name}: must be true or false, got {getattr(self, name)!r}")
        if not isinstance(self.resplit_limit, int) or not 1 <= self.resplit_limit <= 4:
            raise RulesError(f"resplit_limit: must be an integer 1-4, got {self.resplit_limit!r}")
        if not isinstance(self.blackjack_payout, (int, float)) or not 1.0 <= float(self.blackjack_payout) <= 2.0:
            raise RulesError(f"blackjack_payout: must be a number 1.0-2.0, got {self.blackjack_payout!r}")
        if self.double_restrictions not in DOUBLE_RESTRICTIONS:
            raise RulesError(
                f"double_restrictions: must be one of {DOUBLE_RESTRICTIONS}, got {self.double_restrictions!r}"
            )

    @property
    def uses_multideck_chart(self) -> bool:
        """Strategy charts encoded in this project are the 4-8 deck tables."""
        return self.decks >= 4


def rules_from_mapping(data: Mapping[str, Any]) -> Rules:
    valid_keys = set(Rules.__dataclass_fields__)
    unknown = set(data) - valid_keys
    if unknown:
        raise RulesError(f"unknown rules key(s): {sorted(unknown)} — valid keys: {sorted(valid_keys)}")
    return Rules(**data)


def load_rules(path: "str | Path") -> Rules:
    p = Path(path)
    if not p.exists():
        raise RulesError(f"rules file not found: {p}")
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RulesError(f"rules file must be a YAML mapping, got {type(raw).__name__}")
    return rules_from_mapping(raw)
