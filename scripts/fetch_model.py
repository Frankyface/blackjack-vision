"""Download the pretrained card-vision weights into models/best.pt.

Usage: python scripts/fetch_model.py
Weights: https://github.com/cadyze/card-vision (MIT) — see README credits.
"""
from __future__ import annotations

import socket
import sys
import urllib.request
from pathlib import Path

URL = (
    "https://github.com/cadyze/card-vision/raw/main/"
    "card-vision-model-output/weights/best.pt"
)
DEST = Path(__file__).resolve().parents[1] / "models" / "best.pt"
MIN_PLAUSIBLE_BYTES = 1_000_000


def main() -> int:
    if DEST.exists():
        size = DEST.stat().st_size
        if size >= MIN_PLAUSIBLE_BYTES:
            print(f"already present: {DEST} ({size:,} bytes)")
            return 0
        print(f"existing file looks truncated ({size} bytes) — re-downloading")
        DEST.unlink()
    DEST.parent.mkdir(parents=True, exist_ok=True)
    part = DEST.with_suffix(".pt.part")
    print(f"downloading {URL} ...")
    socket.setdefaulttimeout(60)
    try:
        urllib.request.urlretrieve(URL, part)  # noqa: S310 — fixed https URL
    except OSError as exc:
        if part.exists():
            part.unlink()
        print(f"download failed: {exc}")
        return 1
    size = part.stat().st_size
    if size < MIN_PLAUSIBLE_BYTES:
        part.unlink()
        print(f"download looks wrong ({size} bytes) — removed. Check the URL.")
        return 1
    part.replace(DEST)
    print(f"saved {DEST} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
