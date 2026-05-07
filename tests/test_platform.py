"""Platform detection."""
from __future__ import annotations

from src.rpi_starter.platform import is_raspberry_pi


def test_force_pi_one(monkeypatch) -> None:
    monkeypatch.setenv("FORCE_PI", "1")
    is_raspberry_pi.cache_clear()
    assert is_raspberry_pi() is True


def test_force_pi_zero(monkeypatch) -> None:
    monkeypatch.setenv("FORCE_PI", "0")
    is_raspberry_pi.cache_clear()
    assert is_raspberry_pi() is False


def test_default_off_pi(monkeypatch) -> None:
    monkeypatch.delenv("FORCE_PI", raising=False)
    is_raspberry_pi.cache_clear()
    # On a non-Pi dev machine `/proc/device-tree/model` either doesn't exist
    # or doesn't contain "Raspberry Pi"
    assert is_raspberry_pi() is False
