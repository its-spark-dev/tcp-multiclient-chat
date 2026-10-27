"""Additional terminal client using a positional server address and fixed port 5000."""

import codecs
import os
import socket
import sys
import threading

PORT = 5000


# Print the same text even when a UTF-8 character spans multiple recv calls.
def receive(client, stopping):
    """Decode the server byte stream incrementally, preserving displayed text."""
    decoder = codecs.getincrementaldecoder("utf-8")()
    try:
        while True:
            data = client.recv(1024)
            if not data:
                print(decoder.decode(b"", final=True), end="", flush=True)
                if not stopping.is_set():
                    print("Disconnected from server", flush=True)
                break
            print(decoder.decode(data), end="", flush=True)
    except (OSError, UnicodeError):
        pass


def run_client(client):
    """Run input and receiving until local exit or server disconnect."""
    stopping = threading.Event()

    # Blocking keyboard input must not keep the process alive after disconnect.
    def send():
        try:
            # Read the descriptor directly: a blocked daemon must not hold
            # sys.stdin's buffered-reader lock during interpreter shutdown.
            buffer = b""
            while not stopping.is_set():
                data = os.read(sys.stdin.fileno(), 4096)
                buffer += data
                if not data:
                    if buffer:
                        msg = buffer.decode(sys.stdin.encoding or "utf-8")
                        if msg != "/quit":
                            client.sendall((msg + "\n").encode())
                    break
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    msg = line.rstrip(b"\r").decode(sys.stdin.encoding or "utf-8")
                    if msg == "/quit":
                        return
                    client.sendall((msg + "\n").encode())
        except (OSError, UnicodeError):
            pass
        finally:
            stopping.set()
            try:
                client.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

    threading.Thread(target=send, daemon=True).start()
    try:
        receive(client, stopping)
    except KeyboardInterrupt:
        pass
    finally:
        stopping.set()
        try:
            client.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        client.close()


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    run_client(socket.create_connection((host, PORT)))
