"""Classic LED blink. Works on a Pi or with the mock factory off-Pi."""
from __future__ import annotations

import time

from src.rpi_starter import LED


def main() -> None:
    led = LED(pin=17)
    try:
        for _ in range(10):
            led.on()
            time.sleep(0.5)
            led.off()
            time.sleep(0.5)
    finally:
        led.close()


if __name__ == "__main__":
    main()
