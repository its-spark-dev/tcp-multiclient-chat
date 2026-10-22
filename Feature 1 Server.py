
"""CSE 3461 - Feature 1: TCP Broadcast Server

This server connects multiple clients and sends messages from one
client to all the other connected clients.
Each client has its own thread so they can communicate at the same time.
"""

import argparse
import socket
import threading


# Store connected clients with their IP, port, and send lock
clients = {}  

# Use a lock to safely manage clients when multiple threads are running
clients_lock = threading.Lock()


def remove_client(client_socket):
    """Remove a client when it disconnects."""

    # Remove the client from the active client list
    with clients_lock:
        client_info = clients.pop(client_socket, None)

    # Show which client disconnected
    if client_info is not None:
        print(f"[-] Disconnected: {client_info[0]}", flush=True)

    # Close the client's socket
    try:
        client_socket.close()
    except OSError:
        pass


def broadcast(sender_socket, sender_id, text):
    """Send a message to all connected clients except the sender."""

    # Add the sender's IP and port to the message
    payload = f"[{sender_id}] {text}\n".encode("utf-8")

    # Get all connected clients except the one sending the message
    # Copy the list so other threads can still add or remove clients
    with clients_lock:
        recipients = [(sock, info[1]) for sock, info in clients.items()
                      if sock is not sender_socket]

    # Send the message to each client
    for recipient_socket, send_lock in recipients:
        try:
            # Prevent multiple threads from sending to the same client at once
            with send_lock:
                recipient_socket.sendall(payload)

        # Remove the client if sending the message fails
        except OSError:
            remove_client(recipient_socket)


def handle_client(client_socket, address):
    """Receive messages from one client and broadcast them."""

    # Save the client's IP address and port
    sender_id = f"{address[0]}:{address[1]}"

    try:
        # Read messages from the client one line at a time
        # Each message ends with a newline character
        with client_socket.makefile("r", encoding="utf-8") as incoming:
            for line in incoming:
                message = line.rstrip("\r\n")

                # Skip empty messages
                if not message:
                    continue

                # Show the received message on the server
                print(f"[{sender_id}] {message}", flush=True)

                # Forward the message to all other connected clients
                broadcast(client_socket, sender_id, message)

    # Show an error if something goes wrong with the client connection
    except (OSError, UnicodeError) as exc:
        print(f"[!] Client {sender_id}: {exc}", flush=True)

    # Remove the client when the connection ends
    finally:
        remove_client(client_socket)


def main():
    # Set the server IP address and port
    parser = argparse.ArgumentParser(description="Feature 1 TCP broadcast server")
    parser.add_argument("--host", default="0.0.0.0",
                        help="IP to bind (default: 0.0.0.0 for LAN clients)")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    # Create a TCP server socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        # Allow the server port to be reused after restarting
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the server to the IP address and port
        server_socket.bind((args.host, args.port))

        # Start listening for client connections
        server_socket.listen()
        print(f"[+] TCP server listening on {args.host}:{args.port}", flush=True)
        print("[+] Press Ctrl+C to stop the server.", flush=True)

        try:
            # Keep accepting new clients while the server is running
            while True:
                client_socket, address = server_socket.accept()
                client_id = f"{address[0]}:{address[1]}"

                # Add the new client to the active client list
                with clients_lock:
                    clients[client_socket] = (client_id, threading.Lock())

                print(f"[+] Connected: {client_id}", flush=True)

                # Create a separate thread to handle this client
                thread = threading.Thread(target=handle_client,
                                          args=(client_socket, address), daemon=True)
                thread.start()

        # Stop the server when Ctrl+C is pressed
        except KeyboardInterrupt:
            print("\n[+] Server stopping.", flush=True)

        # Close all remaining client connections before stopping
        finally:
            with clients_lock:
                connected = list(clients)
            for client_socket in connected:
                remove_client(client_socket)


if __name__ == "__main__":
    main()
