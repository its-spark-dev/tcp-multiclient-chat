"""Unified threaded chat server, combining Features 1, 2A and 2B."""

import argparse
import re
import socket
import threading

from protocol import read_lines, send_line
from network_conditions import NetworkConditions
from send_metrics import SendMetrics
from feature3_experiment import non_negative_float, loss_rate


class Peer:
    """Serialize writes to one client, as in the original Feature 1 server."""

    def __init__(self, connection):
        self.connection = connection
        self.send_lock = threading.Lock()

    def send(self, text: str) -> None:
        with self.send_lock:
            send_line(self.connection, text)

    def close(self) -> None:
        try:
            self.connection.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.connection.close()


class ChatServer:
    """Protect registration state without holding its lock during socket I/O."""

    def __init__(self, conditions=None):
        self.clients = {}
        self.peers = set()
        self.workers = []
        self.lock = threading.Lock()
        self.conditions = conditions if conditions is not None else NetworkConditions()
        self.metrics = SendMetrics()

    def deliver(self, peer: Peer, text: str) -> None:
        """Apply impairment once per recipient and record the socket-send outcome."""
        self.metrics.attempt()
        result = self.conditions.apply(text)
        if not result.delivered:
            self.metrics.record(result)
            return
        try:
            peer.send(text)
        except OSError:
            self.metrics.record(result, success=False)
            with self.lock:
                for name, client in list(self.clients.items()):
                    if client is peer:
                        del self.clients[name]
            peer.close()
        else:
            self.metrics.record(result, success=True)

    def route(self, username: str, peer: Peer, text: str) -> None:
        """Route user text; control errors bypass impairment and message metrics."""
        if not text.strip():
            return
        if text.startswith("@"):
            parts = text[1:].split(maxsplit=1)
            if len(parts) != 2 or not parts[1].strip():
                peer.send("[Server] Usage: @username message")
                return
            target, message = parts
            if target == username:
                peer.send("[Server] You can't send a private message to yourself.")
                return
            with self.lock:
                recipient = self.clients.get(target)
            if recipient is None:
                peer.send(f"[Server] User '{target}' not found.")
                return
            self.deliver(recipient, f"[Private] {username}: {message}")
        else:
            with self.lock:
                recipients = [other for name, other in self.clients.items()
                              if name != username]
            # Release shared-state lock before simulated delay or blocking I/O.
            for recipient in recipients:
                self.deliver(recipient, f"[{username}] {text}")

    def handle(self, peer: Peer) -> None:
        """Register one connection and process its complete frames until disconnect."""
        username = None
        try:
            peer.send("[Server] Enter username:")
            lines = read_lines(peer.connection)
            for candidate in lines:
                if not re.fullmatch(r"[A-Za-z0-9_]{1,24}", candidate):
                    peer.send("[Server] Use 1-24 letters, digits or underscores.")
                    continue
                with self.lock:
                    available = candidate not in self.clients
                    if available:
                        self.clients[candidate] = peer
                if available:
                    username = candidate
                    peer.send(f"[Server] Registered: {username}")
                    break
                peer.send("[Server] Username already in use. Try another:")
            if username is None:
                return
            for text in lines:
                if text == "/quit":
                    break
                self.route(username, peer, text)
        except (OSError, UnicodeError):
            pass
        finally:
            with self.lock:
                if self.clients.get(username) is peer:
                    del self.clients[username]
                self.peers.discard(peer)
            peer.close()

    def serve(self, host: str, port: int) -> None:
        """Accept per-client workers, then close sockets and join workers on exit."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind((host, port))
            listener.listen()
            print(f"Server listening on {listener.getsockname()}", flush=True)
            try:
                while True:
                    connection, _ = listener.accept()
                    peer = Peer(connection)
                    with self.lock:
                        self.peers.add(peer)
                    self.workers = [worker for worker in self.workers if worker.is_alive()]
                    worker = threading.Thread(target=self.handle, args=(peer,))
                    self.workers.append(worker)
                    worker.start()
            finally:
                with self.lock:
                    peers = list(self.peers)
                for peer in peers:
                    peer.close()
                for worker in self.workers:
                    worker.join()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1",
                        help="IPv4 bind address (default: 127.0.0.1; use 0.0.0.0 for LAN)")
    parser.add_argument("--port", type=int, default=5000, help="TCP port (default: 5000)")
    parser.add_argument("--latency-ms", type=non_negative_float, default=0,
                        help="artificial latency in milliseconds (default: 0)")
    parser.add_argument("--jitter-ms", type=non_negative_float, default=0,
                        help="uniform +/- jitter in milliseconds (default: 0)")
    parser.add_argument("--loss-rate", type=loss_rate, default=0,
                        help="application-level drop probability, 0 to 1 (default: 0)")
    parser.add_argument("--seed", type=int, help="seed random decisions for a fixed call order")
    args = parser.parse_args()
    server = ChatServer(NetworkConditions(args.latency_ms, args.jitter_ms,
                                          args.loss_rate, args.seed))
    try:
        server.serve(args.host, args.port)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except OSError as error:
        parser.exit(1, f"Server error: {error}\n")
    finally:
        print("Server send-path metrics (no receipt acknowledgement):", flush=True)
        for name, value in server.metrics.summary().items():
            print(f"  {name}: {value}", flush=True)


if __name__ == "__main__":
    main()
