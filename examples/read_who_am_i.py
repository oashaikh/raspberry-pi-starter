"""Read MPU-6050 WHO_AM_I register over I2C.

Off the Pi this just exercises the MockI2CBus seeded with the expected
response. On the Pi it talks to the real device on bus 1, address 0x68.
"""
from __future__ import annotations

from src.rpi_starter import I2CDevice, MockI2CBus
from src.rpi_starter.i2c import open_bus
from src.rpi_starter.platform import is_raspberry_pi

ADDRESS = 0x68
WHO_AM_I = 0x75


def main() -> None:
    if is_raspberry_pi():
        bus = open_bus(1)
    else:
        bus = MockI2CBus(registers={(ADDRESS, WHO_AM_I): 0x68})

    device = I2CDevice(bus, ADDRESS)
    print(f"WHO_AM_I = 0x{device.read_register(WHO_AM_I):02X}")
    bus.close()


if __name__ == "__main__":
    main()
