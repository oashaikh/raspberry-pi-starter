"""I2C helper with a Bus protocol so tests can supply a mock implementation."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol


class I2CBus(Protocol):
    def write_byte_data(self, address: int, register: int, value: int) -> None: ...
    def read_byte_data(self, address: int, register: int) -> int: ...
    def write_i2c_block_data(self, address: int, register: int, data: list[int]) -> None: ...
    def read_i2c_block_data(self, address: int, register: int, length: int) -> list[int]: ...
    def close(self) -> None: ...


class I2CDevice:
    """A single addressed device on an I2C bus."""

    def __init__(self, bus: I2CBus, address: int) -> None:
        self.bus = bus
        self.address = address

    def write_register(self, register: int, value: int) -> None:
        self.bus.write_byte_data(self.address, register, value & 0xFF)

    def read_register(self, register: int) -> int:
        return self.bus.read_byte_data(self.address, register) & 0xFF

    def write_block(self, register: int, data: Iterable[int]) -> None:
        self.bus.write_i2c_block_data(self.address, register, [b & 0xFF for b in data])

    def read_block(self, register: int, length: int) -> list[int]:
        return self.bus.read_i2c_block_data(self.address, register, length)


class MockI2CBus:
    """In-memory I2C bus for tests. Records writes and serves stub reads."""

    def __init__(self, registers: dict[tuple[int, int], int] | None = None) -> None:
        self.registers: dict[tuple[int, int], int] = dict(registers or {})
        self.writes: list[tuple[str, int, int, object]] = []

    def write_byte_data(self, address: int, register: int, value: int) -> None:
        self.registers[(address, register)] = value & 0xFF
        self.writes.append(("write_byte", address, register, value))

    def read_byte_data(self, address: int, register: int) -> int:
        return self.registers.get((address, register), 0) & 0xFF

    def write_i2c_block_data(self, address: int, register: int, data: list[int]) -> None:
        for offset, value in enumerate(data):
            self.registers[(address, register + offset)] = value & 0xFF
        self.writes.append(("write_block", address, register, list(data)))

    def read_i2c_block_data(self, address: int, register: int, length: int) -> list[int]:
        return [
            self.registers.get((address, register + i), 0) & 0xFF for i in range(length)
        ]

    def close(self) -> None:
        pass


def open_bus(bus_number: int = 1) -> I2CBus:
    """Open a real SMBus on the Pi, or return a MockI2CBus off-Pi."""
    from src.rpi_starter.platform import is_raspberry_pi

    if is_raspberry_pi():  # pragma: no cover — only on real hardware
        from smbus2 import SMBus

        return SMBus(bus_number)
    return MockI2CBus()
