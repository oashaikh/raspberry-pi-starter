"""UART unit tests using MockUart."""
from __future__ import annotations

from src.rpi_starter import MockUart, UartLink


def test_send_line_writes_with_terminator() -> None:
    port = MockUart()
    link = UartLink(port)
    link.send_line("AT+CMD")
    assert bytes(port.tx_buffer) == b"AT+CMD\r\n"


def test_read_line() -> None:
    port = MockUart(b"OK\r\nERROR\r\n")
    link = UartLink(port)
    assert link.read_line() == "OK"
    assert link.read_line() == "ERROR"


def test_has_data() -> None:
    port = MockUart()
    link = UartLink(port)
    assert link.has_data() is False
    port.queue(b"hello\r\n")
    assert link.has_data() is True
    link.read_line()
    assert link.has_data() is False
