"""Force the gpiozero MockFactory for tests so we don't touch real hardware."""
from __future__ import annotations

import os

import pytest
from gpiozero import Device
from gpiozero.pins.mock import MockFactory


@pytest.fixture(autouse=True)
def mock_pin_factory(monkeypatch: pytest.MonkeyPatch) -> MockFactory:
    monkeypatch.setenv("FORCE_PI", "0")
    factory = MockFactory()
    Device.pin_factory = factory
    yield factory
    factory.reset()


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if os.environ.get("ON_PI") in {"1", "true"}:
        return
    skip = pytest.mark.skip(reason="not running on a Pi (set ON_PI=1)")
    for item in items:
        if "on_pi" in item.keywords:
            item.add_marker(skip)
