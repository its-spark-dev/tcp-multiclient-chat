"""Minimal TCP client foundation for the future chat application."""

import argparse
import socket


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000


def parse_args():
    """Parse the server address from the command line."""
    parser = argparse.ArgumentParser(description="Connect to the TCP chat server.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="server address")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="server port")
    return parser.parse_args()


def connect_to_server(host, port):
    """Connect once to the server, confirm the connection, and close cleanly."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))
            print(f"Connected to server at {host}:{port}")
    except OSError as error:
        print(f"Client socket error: {error}")


if __name__ == "__main__":
    arguments = parse_args()
    connect_to_server(arguments.host, arguments.port)
