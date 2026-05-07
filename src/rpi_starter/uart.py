"""UART/serial helper with a mock for tests."""
from __future__ import annotations

from typing import Protocol


class SerialPort(Protocol):
    def write(self, data: bytes) -> int: ...
    def read(self, size: int = 1) -> bytes: ...
    def readline(self) -> bytes: ...
    def close(self) -> None: ...
    in_waiting: int


class UartLink:
    def __init__(self, port: SerialPort) -> None:
        self.port = port

    def send_line(self, text: str, terminator: str = "\r\n") -> None:
        self.port.write((text + terminator).encode("utf-8"))

    def read_line(self) -> str:
        return self.port.readline().decode("utf-8", errors="replace").rstrip("\r\n")

    def has_data(self) -> bool:
        return self.port.in_waiting > 0

    def close(self) -> None:
        self.port.close()


class MockUart:
    """Bidirectional buffer-based serial stub for tests."""

    def __init__(self, incoming: bytes = b"") -> None:
        self.rx_buffer = bytearray(incoming)
        self.tx_buffer = bytearray()
        self._closed = False

    @property
    def in_waiting(self) -> int:
        return len(self.rx_buffer)

    def write(self, data: bytes) -> int:
        self.tx_buffer.extend(data)
        return len(data)

    def read(self, size: int = 1) -> bytes:
        out = bytes(self.rx_buffer[:size])
        del self.rx_buffer[:size]
        return out

    def readline(self) -> bytes:
        idx = self.rx_buffer.find(b"\n")
        if idx == -1:
            out = bytes(self.rx_buffer)
            self.rx_buffer.clear()
            return out
        out = bytes(self.rx_buffer[: idx + 1])
        del self.rx_buffer[: idx + 1]
        return out

    def queue(self, data: bytes) -> None:
        self.rx_buffer.extend(data)

    def close(self) -> None:
        self._closed = True


def open_serial(port: str, baudrate: int = 115200, timeout: float = 1.0) -> SerialPort:
    """Open a real `pyserial` port on the Pi, or return MockUart off-Pi."""
    from src.rpi_starter.platform import is_raspberry_pi

    if is_raspberry_pi():  # pragma: no cover
        import serial

        return serial.Serial(port, baudrate=baudrate, timeout=timeout)
    return MockUart()
