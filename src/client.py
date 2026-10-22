"""Interactive chat client with background receiving, derived from Feature 1."""

import argparse
import select
import socket
import sys
import threading

from protocol import read_lines, send_line


def receive_messages(connection, connected):
    try:
        for line in read_lines(connection):
            print(line, flush=True)
    except (OSError, UnicodeError) as error:
        if connected.is_set():
            print(f"Receive error: {error}", flush=True)
    finally:
        connected.clear()
        print("Disconnected.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
            connection.connect((args.host, args.port))
            print("Enter a username when prompted; then chat or use @username message.")
            print("Type /quit to exit.")
            connected = threading.Event()
            connected.set()
            receiver = threading.Thread(target=receive_messages,
                                        args=(connection, connected))
            receiver.start()
            try:
                while connected.is_set():
                    ready, _, _ = select.select([sys.stdin], [], [], 0.2)
                    if not ready:
                        continue
                    line = sys.stdin.readline()
                    if not line:
                        break
                    send_line(connection, line.rstrip("\r\n"))
                    if line.strip() == "/quit":
                        break
            finally:
                connected.clear()
                try:
                    connection.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                receiver.join()
    except KeyboardInterrupt:
        print("\nClient stopped.")
    except OSError as error:
        parser.exit(1, f"Client error: {error}\n")


if __name__ == "__main__":
    main()
