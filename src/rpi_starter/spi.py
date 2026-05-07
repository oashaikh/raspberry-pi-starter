"""SPI helper with mock for off-Pi testing."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol


class SPIBus(Protocol):
    def open(self, bus: int, device: int) -> None: ...
    def xfer2(self, data: list[int]) -> list[int]: ...
    def close(self) -> None: ...
    max_speed_hz: int
    mode: int


class SPIDevice:
    def __init__(self, bus: SPIBus, bus_no: int = 0, device_no: int = 0) -> None:
        self.bus = bus
        bus.open(bus_no, device_no)

    def configure(self, max_speed_hz: int, mode: int = 0) -> None:
        self.bus.max_speed_hz = max_speed_hz
        self.bus.mode = mode

    def transfer(self, data: Iterable[int]) -> list[int]:
        return self.bus.xfer2([b & 0xFF for b in data])

    def close(self) -> None:
        self.bus.close()


class MockSPIBus:
    """In-memory SPI bus. Configure `responses` to drive `xfer2` returns."""

    def __init__(self, responses: list[list[int]] | None = None) -> None:
        self.responses = list(responses or [])
        self.transfers: list[list[int]] = []
        self.max_speed_hz: int = 0
        self.mode: int = 0
        self._opened: tuple[int, int] | None = None

    def open(self, bus: int, device: int) -> None:
        self._opened = (bus, device)

    def xfer2(self, data: list[int]) -> list[int]:
        self.transfers.append(list(data))
        if self.responses:
            return self.responses.pop(0)
        return [0] * len(data)

    def close(self) -> None:
        self._opened = None


def open_bus() -> SPIBus:
    from src.rpi_starter.platform import is_raspberry_pi

    if is_raspberry_pi():  # pragma: no cover
        import spidev

        return spidev.SpiDev()
    return MockSPIBus()
