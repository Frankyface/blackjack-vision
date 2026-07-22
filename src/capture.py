"""Webcam capture wrapper around OpenCV."""
from __future__ import annotations

from typing import Optional, Tuple


class Camera:
    def __init__(self, index: int = 0, width: int = 1280, height: int = 720) -> None:
        import cv2  # lazy: keeps pure-logic tests light

        self._cv2 = cv2
        self._cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # DSHOW: fast open on Windows
        if not self._cap.isOpened():
            # Fall back to the default backend (Linux/Pi path).
            self._cap = cv2.VideoCapture(index)
        if not self._cap.isOpened():
            raise RuntimeError(
                f"could not open camera index {index} — is the webcam plugged in?"
            )
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    @property
    def resolution(self) -> Tuple[int, int]:
        return (
            int(self._cap.get(self._cv2.CAP_PROP_FRAME_WIDTH)),
            int(self._cap.get(self._cv2.CAP_PROP_FRAME_HEIGHT)),
        )

    def read(self):
        """Return one BGR frame, or None if the grab failed."""
        ok, frame = self._cap.read()
        return frame if ok else None

    def release(self) -> None:
        self._cap.release()
