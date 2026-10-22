"""CSE 3461 — Feature 1: TCP broadcast client.

This client sends messages to the server and receives messages
from other clients through the server.
"""

import argparse
import select
import socket
import sys
import threading


def receive_messages(client_socket, connected):
    """Receive and display messages from the server."""
    try:
        with client_socket.makefile("r", encoding="utf-8") as incoming:
            for line in incoming:
                print(f"\n{line.rstrip()}", flush=True)
    except (OSError, UnicodeError) as exc:
        if connected.is_set():
            print(f"\n[!] Receive error: {exc}", flush=True)
    finally:
        # Stop receiving when the server disconnects
        connected.clear()
        print("\n[!] Disconnected from server.", flush=True)


def main():
    # Set the server IP and port
    parser = argparse.ArgumentParser(description="Feature 1 TCP broadcast client")
    parser.add_argument("server_ip", nargs="?", default="127.0.0.1",
                        help="Server IP (default: 127.0.0.1 for simulation)")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    try:
        # Connect to the TCP server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((args.server_ip, args.port))

            # Show the client's IP address and port
            local_ip, local_port = client_socket.getsockname()
            print(f"[+] Connected to server {args.server_ip}:{args.port}")
            print(f"[+] My local IP address: {local_ip}")
            print(f"[+] My local port: {local_port}")
            print("[+] Type messages and press Enter. Type /quit to leave.")

            # Use a separate thread to receive messages while typing
            connected = threading.Event()
            connected.set()
            receiver = threading.Thread(target=receive_messages,
                                        args=(client_socket, connected), daemon=True)
            receiver.start()

            # Check for keyboard input so a server disconnect can end the client
            print("> ", end="", flush=True)
            while connected.is_set():
                try:
                    # Wait briefly for input instead of blocking at input()
                    ready, _, _ = select.select([sys.stdin], [], [], 0.2)
                    if not ready:
                        continue
                    message = input()
                except (EOFError, KeyboardInterrupt, OSError):
                    break

                if message.strip() == "/quit":
                    break
                if not message.strip():
                    print("> ", end="", flush=True)
                    continue

                # Send the message to the server
                try:
                    client_socket.sendall((message + "\n").encode("utf-8"))
                except OSError as exc:
                    print(f"[!] Send error: {exc}")
                    break
                print("> ", end="", flush=True)
            connected.clear()

    # Show an error if the client cannot connect
    except OSError as exc:
        print(f"[!] Could not connect: {exc}")


if __name__ == "__main__":
    main()
