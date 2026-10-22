"""Fast unit coverage and actual three-client localhost smoke tests."""

import ast
from pathlib import Path
import signal
import socket
import subprocess
import sys
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from protocol import read_lines, send_line
from server import ChatServer
from network_conditions import NetworkConditions


class ChatTests(unittest.TestCase):
    def test_fragmented_and_coalesced_frames(self):
        connection = Mock()
        connection.recv.side_effect = [b"ali", b"ce\nhello\ntrai", b"ling", b""]
        self.assertEqual(list(read_lines(connection)), ["alice", "hello"])

    def test_metrics_and_independent_recipient_decisions(self):
        conditions = NetworkConditions(loss_rate=0.5, seed=1, sleep_func=lambda _: None)
        server = ChatServer(conditions)
        a, b, c = Mock(), Mock(), Mock()
        server.clients = {"a": a, "b": b, "c": c}
        server.route("a", a, "hello")
        self.assertEqual(b.send.call_count + c.send.call_count, 1)
        c.send.side_effect = OSError("broken")
        server.conditions = NetworkConditions()
        server.deliver(c, "fail")
        metrics = server.metrics.summary()
        self.assertEqual([metrics[key] for key in (
            "delivery_attempts", "simulated_drops", "simulator_passes",
            "socket_send_successes", "socket_send_failures")], [3, 1, 2, 1, 1])

    def test_full_loss_and_control_errors(self):
        server = ChatServer(NetworkConditions(loss_rate=1))
        a, b = Mock(), Mock()
        server.clients = {"a": a, "b": b}
        server.route("a", a, "hi")
        b.send.assert_not_called()
        for text in ("@", "@b", "@a hello", "@missing hello"):
            server.route("a", a, text)
        self.assertEqual(a.send.call_count, 4)
        self.assertEqual(server.metrics.summary()["delivery_attempts"], 1)


class LocalhostTests(unittest.TestCase):
    def start_server(self, *options):
        process = subprocess.Popen(
            [sys.executable, "-u", "src/server.py", "--port", "0", *options],
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.addCleanup(self.stop_server, process)
        # Bound the startup wait so a startup failure cannot hang the suite.
        import select
        self.assertTrue(select.select([process.stdout], [], [], 5)[0])
        address = ast.literal_eval(process.stdout.readline().split("on ", 1)[1])
        return process, address

    def stop_server(self, process):
        if process.poll() is None:
            process.send_signal(signal.SIGINT)
        try:
            output, _ = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            self.fail("Server failed to shut down")
        return output

    def connect(self, address, name):
        connection = socket.create_connection(address, timeout=2)
        self.addCleanup(connection.close)
        lines = connection.makefile("rb")
        self.addCleanup(lines.close)
        self.assertIn(b"Enter username", lines.readline())
        send_line(connection, name)
        self.assertIn(b"Registered", lines.readline())
        return connection, lines

    def assert_quiet(self, connection):
        import select
        self.assertFalse(select.select([connection], [], [], 0.08)[0])

    def test_baseline_three_clients(self):
        process, address = self.start_server()
        a, ar = self.connect(address, "Alice")
        b, br = self.connect(address, "Bob")
        c, cr = self.connect(address, "Carol")
        send_line(a, "hello")
        self.assertEqual(br.readline(), b"[Alice] hello\n")
        self.assertEqual(cr.readline(), b"[Alice] hello\n")
        self.assert_quiet(a)
        send_line(a, "@Bob secret")
        self.assertEqual(br.readline(), b"[Private] Alice: secret\n")
        self.assert_quiet(c)
        for text in ("@missing hi", "@", "@Alice hi"):
            send_line(a, text)
            self.assertIn(b"[Server]", ar.readline())
        self.assert_quiet(b)
        duplicate = socket.create_connection(address, timeout=2)
        self.addCleanup(duplicate.close)
        reader = duplicate.makefile("rb")
        self.addCleanup(reader.close)
        reader.readline()
        send_line(duplicate, "Alice")
        self.assertIn(b"already in use", reader.readline())
        send_line(duplicate, "")
        self.assertIn(b"1-24", reader.readline())
        send_line(a, "/quit")
        self.assertEqual(ar.readline(), b"")
        send_line(duplicate, "Alice")
        self.assertIn(b"Registered", reader.readline())
        # Fragmented UTF-8 and two complete frames in one socket write.
        duplicate.sendall(b"caf\xc3")
        duplicate.sendall(b"\xa9\nsecond\n")
        self.assertEqual(br.readline(), "[Alice] café\n".encode())
        self.assertEqual(br.readline(), b"[Alice] second\n")
        self.assertEqual(cr.readline(), "[Alice] café\n".encode())
        self.assertEqual(cr.readline(), b"[Alice] second\n")
        output = self.stop_server(process)
        self.assertIn("socket_send_successes: 7", output)
        self.assertEqual(process.returncode, 0)

    def test_impaired_three_clients(self):
        process, address = self.start_server("--latency-ms", "20", "--jitter-ms", "5",
                                             "--loss-rate", "0.2", "--seed", "42")
        a, ar = self.connect(address, "Alice")
        b, br = self.connect(address, "Bob")
        c, cr = self.connect(address, "Carol")
        # Seed 42 first two per-recipient decisions both pass.
        send_line(a, "hello")
        self.assertIn(b"hello", br.readline())
        self.assertIn(b"hello", cr.readline())
        send_line(a, "@missing hi")
        self.assertIn(b"not found", ar.readline())
        output = self.stop_server(process)
        self.assertIn("delivery_attempts: 2", output)
        self.assertIn("simulator_passes: 2", output)
        self.assertIn("average_artificial_delay_ms:", output)
        print("\nPreliminary impaired localhost metrics:\n" + output)

    def test_interactive_client_exits_on_server_disconnect(self):
        process, address = self.start_server()
        client = subprocess.Popen(
            [sys.executable, "-u", "src/client.py", "--port", str(address[1])],
            cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True)
        self.addCleanup(self.stop_server, client)
        # Register via the real terminal client's stdin.
        client.stdin.write("TerminalUser\n")
        client.stdin.flush()
        import concurrent.futures
        def await_registration():
            for line in client.stdout:
                if "Registered: TerminalUser" in line:
                    return True
            return False
        with concurrent.futures.ThreadPoolExecutor() as pool:
            self.assertTrue(pool.submit(await_registration).result(timeout=3))
        self.stop_server(process)
        output, _ = client.communicate(timeout=5)
        self.assertEqual(client.returncode, 0, output)


if __name__ == "__main__":
    unittest.main()
