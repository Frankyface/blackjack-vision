"""Generate web-app data files FROM the tested Python engines.

The web app never re-implements the strategy chart — it ships a JSON lookup
generated here from src/engines/strategy.py (chart-fixture-verified), plus the
model's class names. Run after changing charts or the model:

    python scripts/export_web_assets.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.engines import strategy  # noqa: E402

OUT = ROOT / "web" / "assets"


def chart_tables() -> dict:
    """Raw cell-code tables for both rule sets — resolution happens in JS."""
    def rows(table):
        return {str(total): row for total, row in table.items()}

    return {
        "ups": list(strategy.UPS),
        "H17": {
            "hard": rows(strategy._HARD_H17),
            "soft": rows(strategy._SOFT_H17),
            "pairs": strategy._PAIRS_H17,
        },
        "S17": {
            "hard": rows(strategy._HARD_S17),
            "soft": rows(strategy._SOFT_S17),
            "pairs": strategy._PAIRS_S17,
        },
    }


def class_names() -> list:
    from ultralytics import YOLO

    model = YOLO(str(ROOT / "models" / "best.pt"))
    return [model.names[i] for i in range(len(model.names))]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "strategy.json").write_text(
        json.dumps(chart_tables(), indent=1), encoding="utf-8")
    names = class_names()
    (OUT / "classes.json").write_text(json.dumps(names), encoding="utf-8")
    print(f"wrote {OUT / 'strategy.json'}")
    print(f"wrote {OUT / 'classes.json'} ({len(names)} classes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
