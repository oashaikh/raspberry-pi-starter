"""GPIO tests using gpiozero's MockFactory — no hardware needed."""
from __future__ import annotations

from src.rpi_starter import LED, Button


class TestLED:
    def test_starts_off(self) -> None:
        led = LED(pin=17)
        assert led.is_lit is False
        led.close()

    def test_on_off(self) -> None:
        led = LED(pin=17)
        led.on()
        assert led.is_lit is True
        led.off()
        assert led.is_lit is False
        led.close()

    def test_toggle(self) -> None:
        led = LED(pin=17)
        led.toggle()
        assert led.is_lit is True
        led.toggle()
        assert led.is_lit is False
        led.close()


class TestButton:
    def test_press_and_release(self, mock_pin_factory) -> None:
        button = Button(pin=4)
        pin = mock_pin_factory.pin(4)

        pin.drive_low()    # active-low when pull-up
        assert button.is_pressed is True

        pin.drive_high()
        assert button.is_pressed is False

        button.close()

    def test_callback_fires(self, mock_pin_factory) -> None:
        button = Button(pin=4)
        events: list[str] = []
        button.when_pressed(lambda: events.append("pressed"))
        button.when_released(lambda: events.append("released"))

        pin = mock_pin_factory.pin(4)
        pin.drive_low()
        pin.drive_high()

        assert "pressed" in events
        assert "released" in events
        button.close()
