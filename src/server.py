"""Minimal TCP server foundation for the future chat application."""

import argparse
import socket


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000


def parse_args():
    """Parse the server address from the command line."""
    parser = argparse.ArgumentParser(description="Start the TCP chat server.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="address to bind to")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="port to bind to")
    return parser.parse_args()


def run_server(host, port):
    """Listen for connections and close each client after logging its address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((host, port))
            server_socket.listen()
            print(f"Server listening on {host}:{port}", flush=True)

            while True:
                client_socket, client_address = server_socket.accept()
                with client_socket:
                    print(f"Connection accepted from {client_address}", flush=True)
    except OSError as error:
        print(f"Server socket error: {error}")


if __name__ == "__main__":
    arguments = parse_args()
    try:
        run_server(arguments.host, arguments.port)
    except KeyboardInterrupt:
        print("\nServer stopped.")
