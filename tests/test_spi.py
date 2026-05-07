"""SPI unit tests using MockSPIBus."""
from __future__ import annotations

from src.rpi_starter import MockSPIBus, SPIDevice


def test_transfer_returns_zeros_by_default() -> None:
    bus = MockSPIBus()
    device = SPIDevice(bus)
    assert device.transfer([0x01, 0x02, 0x03]) == [0, 0, 0]
    assert bus.transfers == [[0x01, 0x02, 0x03]]


def test_transfer_returns_canned_response() -> None:
    bus = MockSPIBus(responses=[[0xDE, 0xAD]])
    device = SPIDevice(bus)
    assert device.transfer([0x00, 0x00]) == [0xDE, 0xAD]


def test_configure_sets_speed_and_mode() -> None:
    bus = MockSPIBus()
    device = SPIDevice(bus)
    device.configure(max_speed_hz=1_000_000, mode=3)
    assert bus.max_speed_hz == 1_000_000
    assert bus.mode == 3


def test_close_resets_open_state() -> None:
    bus = MockSPIBus()
    device = SPIDevice(bus)
    assert bus._opened == (0, 0)
    device.close()
    assert bus._opened is None
