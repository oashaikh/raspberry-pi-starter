"""I2C unit tests using MockI2CBus."""
from __future__ import annotations

from src.rpi_starter import I2CDevice, MockI2CBus


def test_write_and_read_register() -> None:
    bus = MockI2CBus()
    device = I2CDevice(bus, address=0x68)

    device.write_register(0x10, 0xA5)
    assert device.read_register(0x10) == 0xA5
    assert ("write_byte", 0x68, 0x10, 0xA5) in bus.writes


def test_write_register_truncates_to_byte() -> None:
    bus = MockI2CBus()
    device = I2CDevice(bus, address=0x68)

    device.write_register(0x10, 0x1FF)  # 9-bit value
    assert device.read_register(0x10) == 0xFF


def test_block_write_and_read() -> None:
    bus = MockI2CBus()
    device = I2CDevice(bus, address=0x77)

    device.write_block(0x00, [0x01, 0x02, 0x03, 0x04])
    assert device.read_block(0x00, 4) == [0x01, 0x02, 0x03, 0x04]


def test_preseeded_register() -> None:
    bus = MockI2CBus(registers={(0x68, 0x75): 0xD0})  # MPU-6050 WHO_AM_I
    device = I2CDevice(bus, address=0x68)
    assert device.read_register(0x75) == 0xD0
