# raspberry-pi-starter

A drop-in Python scaffold for Raspberry Pi peripheral work — GPIO, I2C,
SPI, UART — designed so the code runs and is **testable on a normal
laptop**, not just on the Pi.

## What this repo does

- Wraps `gpiozero` and gives you `LED` / `Button` types that auto-pick the
  `MockFactory` off-Pi, so unit tests work everywhere.
- Provides protocol-based wrappers for I2C, SPI and UART with built-in
  mocks (`MockI2CBus`, `MockSPIBus`, `MockUart`) for tests.
- Detects whether it's running on a Pi via `/proc/device-tree/model`, with
  `FORCE_PI=1` / `FORCE_PI=0` overrides for CI.
- All Pi-specific dependencies (`smbus2`, `spidev`, `pyserial`,
  `lgpio`) are isolated in `requirements-pi.txt` so dev installs and CI
  remain fast and platform-portable.

## Project layout

- `src/rpi_starter/`
  - `gpio.py` - LED, Button (gpiozero wrappers).
  - `i2c.py` - I2CDevice + MockI2CBus.
  - `spi.py` - SPIDevice + MockSPIBus.
  - `uart.py` - UartLink + MockUart.
  - `platform.py` - `is_raspberry_pi()` detection.
- `tests/` - unit tests using mocks. No hardware needed.
- `examples/blink.py` - LED blink (real or mock).
- `examples/read_who_am_i.py` - MPU-6050 WHO_AM_I over I2C (real or mock).

## Quick start

On any machine (laptop, CI, dev container):

```bash
python -m venv .venv
source .venv/bin/activate          # or .venv\Scripts\activate on Windows
pip install -r requirements-dev.txt
pytest                             # all 25+ tests run with mocks
python -m examples.blink           # uses MockFactory off-Pi
```

On the Pi itself (additionally):

```bash
pip install -r requirements-pi.txt
python -m examples.read_who_am_i
```

## Why mocks instead of a real Pi for tests

Two reasons:

1. CI is faster, simpler and free when it can run on a normal Linux box.
2. The mock surface forces you to write driver code that is testable —
   thin device classes that take a `bus` parameter, instead of code that
   reaches into globals to find a hardware instance. That same pattern
   lets you swap in a fake bus in production tests of higher-level logic.

If you need genuine hardware-in-the-loop tests, mark them
`@pytest.mark.on_pi` and run with `ON_PI=1 pytest`.

## Adding a new device driver

```python
from src.rpi_starter.i2c import I2CBus, I2CDevice

class TMP102:
    """12-bit I2C temperature sensor."""

    ADDRESS = 0x48
    REG_TEMP = 0x00

    def __init__(self, bus: I2CBus) -> None:
        self.dev = I2CDevice(bus, self.ADDRESS)

    def read_celsius(self) -> float:
        msb, lsb = self.dev.read_block(self.REG_TEMP, 2)
        raw = (msb << 4) | (lsb >> 4)
        if raw & 0x800:               # sign extend
            raw -= 1 << 12
        return raw * 0.0625
```

Test it without hardware:

```python
from src.rpi_starter import MockI2CBus

def test_tmp102_positive():
    bus = MockI2CBus(registers={(0x48, 0x00): 0x19, (0x48, 0x01): 0xC0})
    sensor = TMP102(bus)
    assert sensor.read_celsius() == 25.75
```

## Off-Pi dev caveat

`gpiozero` works with `MockFactory` for digital IO but doesn't simulate
real-world timing. Tests should assert on observable state changes, not
sleep-based behaviour, and should never rely on PWM accuracy off-Pi.
