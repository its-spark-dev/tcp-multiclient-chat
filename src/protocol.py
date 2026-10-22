"""Small newline-delimited UTF-8 protocol shared by client and server."""


def read_lines(connection):
    """Buffer incomplete bytes, including split UTF-8 sequences, until newline."""
    buffer = b""
    while True:
        chunk = connection.recv(4096)
        if not chunk:
            return
        buffer += chunk
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            yield line.rstrip(b"\r").decode("utf-8")


def send_line(connection, text):
    """Send exactly one newline-terminated line."""
    connection.sendall((text + "\n").encode("utf-8"))
