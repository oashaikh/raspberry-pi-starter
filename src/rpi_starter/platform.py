"""Detect whether we're running on a Raspberry Pi."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def is_raspberry_pi() -> bool:
    """Best-effort detection — checks `/proc/device-tree/model`.

    Set `FORCE_PI=1` in env to override (handy in CI tests against real-Pi
    code paths). Set `FORCE_PI=0` to force off.
    """
    forced = os.environ.get("FORCE_PI")
    if forced in {"1", "true", "yes"}:
        return True
    if forced in {"0", "false", "no"}:
        return False
    model = Path("/proc/device-tree/model")
    try:
        return "Raspberry Pi" in model.read_text(errors="ignore")
    except OSError:
        return False
