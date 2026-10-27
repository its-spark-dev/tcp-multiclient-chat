"""Small newline-delimited UTF-8 protocol shared by client and server."""


from collections.abc import Iterator
import socket


def read_lines(connection: socket.socket) -> Iterator[str]:
    """Buffer through newline before decoding; discard an incomplete frame at EOF."""
    buffer = b""
    while True:
        chunk = connection.recv(4096)
        if not chunk:
            return
        buffer += chunk
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            yield line.rstrip(b"\r").decode("utf-8")


def send_line(connection: socket.socket, text: str) -> None:
    """Send exactly one newline-terminated line."""
    connection.sendall((text + "\n").encode("utf-8"))
