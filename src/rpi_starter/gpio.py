"""Thin wrappers around `gpiozero` that auto-pick a mock pin factory off-Pi.

`gpiozero` already has a `MockFactory`, so unit tests run without hardware.
This module just makes the choice automatic and exposes a couple of common
device types with our own thin layer.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from gpiozero import LED as _LED
from gpiozero import Button as _Button
from gpiozero import Device

from src.rpi_starter.platform import is_raspberry_pi

if TYPE_CHECKING:
    from gpiozero.pins import Factory


def gpio_factory() -> "Factory":
    """Return a real Pi factory or `MockFactory` based on platform."""
    if is_raspberry_pi() and os.environ.get("FORCE_MOCK_GPIO") not in {"1", "true"}:
        # Try the modern lgpio-based factory first; fall back to whichever
        # gpiozero auto-detects on the Pi.
        try:
            from gpiozero.pins.lgpio import LGPIOFactory

            return LGPIOFactory()
        except ImportError:
            return Device.pin_factory  # let gpiozero pick
    from gpiozero.pins.mock import MockFactory

    return MockFactory()


def _ensure_factory() -> None:
    if Device.pin_factory is None:
        Device.pin_factory = gpio_factory()


class LED:
    """Wrapper around gpiozero.LED that uses the mock factory off-Pi."""

    def __init__(self, pin: int) -> None:
        _ensure_factory()
        self._led = _LED(pin)
        self.pin = pin

    @property
    def is_lit(self) -> bool:
        return bool(self._led.is_lit)

    def on(self) -> None:
        self._led.on()

    def off(self) -> None:
        self._led.off()

    def toggle(self) -> None:
        self._led.toggle()

    def blink(self, on_time: float = 1.0, off_time: float = 1.0, n: int | None = None) -> None:
        self._led.blink(on_time=on_time, off_time=off_time, n=n, background=True)

    def close(self) -> None:
        self._led.close()


class Button:
    """Wrapper around gpiozero.Button."""

    def __init__(self, pin: int, pull_up: bool = True) -> None:
        _ensure_factory()
        self._btn = _Button(pin, pull_up=pull_up)
        self.pin = pin

    @property
    def is_pressed(self) -> bool:
        return bool(self._btn.is_pressed)

    def when_pressed(self, callback) -> None:
        self._btn.when_pressed = callback

    def when_released(self, callback) -> None:
        self._btn.when_released = callback

    def close(self) -> None:
        self._btn.close()
