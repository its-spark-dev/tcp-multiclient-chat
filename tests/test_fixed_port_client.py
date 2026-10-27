"""Regression checks for the fixed-port client example's wire format and disconnect handling."""

import contextlib
import io
from pathlib import Path
import socket
import signal
import subprocess
import sys
import threading
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples"))
from fixed_port_client import receive


class FixedPortClientTests(unittest.TestCase):
    def test_split_utf8_and_unterminated_prompt_keep_exact_output(self):
        client = Mock()
        client.recv.side_effect = [
            b"Enter Username: ", b"[Private] A: caf\xc3",
            b"\xa9\n[A] \xed", b"\x95\x9c\xea\xb8\x80\n", b""]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            receive(client, threading.Event())
        self.assertEqual(output.getvalue(),
                         "Enter Username: [Private] A: café\n[A] 한글\n"
                         "Disconnected from server\n")

    def start_client(self):
        # Use an ephemeral port without changing the client's public CLI.
        listener = socket.socket()
        self.addCleanup(listener.close)
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        listener.settimeout(3)
        port = listener.getsockname()[1]
        code = ("import socket, sys; sys.path.insert(0, 'examples'); "
                "from fixed_port_client import run_client; "
                f"run_client(socket.create_connection(('127.0.0.1', {port})))")
        process = subprocess.Popen(
            [sys.executable, "-u", "-c", code], cwd=ROOT,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.cleanup_client, process)
        connection, _ = listener.accept()
        connection.settimeout(3)
        self.addCleanup(connection.close)
        return process, connection

    def cleanup_client(self, process):
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=3)

    def test_server_disconnect_exits_without_keyboard_input(self):
        process, connection = self.start_client()
        connection.sendall("[A] café\n".encode())
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
        # Keep stdin open: communicate() would close it and mask the original bug.
        process.wait(timeout=3)
        output, errors = process.communicate(timeout=3)
        self.assertEqual(process.returncode, 0, errors)
        self.assertEqual(output, "[A] café\nDisconnected from server\n")
        self.assertEqual(errors, "")

    def test_messages_and_quit_keep_original_wire_format(self):
        process, connection = self.start_client()
        for text in ("Sang", "hello everyone", "@Jiho café"):
            process.stdin.write(text + "\n")
            process.stdin.flush()
            expected = (text + "\n").encode()
            received = b""
            while len(received) < len(expected):
                chunk = connection.recv(1024)
                self.assertTrue(chunk)
                received += chunk
            self.assertEqual(received, expected)
        process.stdin.write("/quit\n")
        process.stdin.flush()
        process.wait(timeout=3)
        output, errors = process.communicate(timeout=3)
        self.assertEqual(process.returncode, 0, errors)
        self.assertEqual(connection.recv(1024), b"")
        self.assertEqual(output, "")
        self.assertEqual(errors, "")

    def test_eof_preserves_last_line_and_quit(self):
        for text, expected in (("last café", "last café\n".encode()),
                               ("/quit", b"")):
            with self.subTest(text=text):
                process, connection = self.start_client()
                output, errors = process.communicate(input=text, timeout=3)
                received = b""
                while True:
                    chunk = connection.recv(1024)
                    if not chunk:
                        break
                    received += chunk
                self.assertEqual(received, expected)
                self.assertEqual(process.returncode, 0, errors)
                self.assertEqual(output, "")
                self.assertEqual(errors, "")

    def test_ctrl_c_exits_cleanly(self):
        process, connection = self.start_client()
        connection.sendall(b"Ready\n")
        self.assertEqual(process.stdout.readline(), "Ready\n")
        process.send_signal(signal.SIGINT)
        process.wait(timeout=3)
        _, errors = process.communicate(timeout=3)
        self.assertEqual(process.returncode, 0, errors)
        self.assertEqual(errors, "")


if __name__ == "__main__":
    unittest.main()
