import socket
import sys
import threading

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = 5000

client = socket.create_connection((HOST, PORT))

#Background thread: print everything the server sends
def receive():
    while True:
        try:
            data = client.recv(1024)
        except OSError:
            break
        if not data:
            print("Disconnected from server")
            break
        print(data.decode(), end="")

threading.Thread(target=receive, daemon=True).start()

#Main thread: send what the user types
try:
    while True:
        msg = input()
        if msg == "/quit":
            break
        client.sendall((msg + "\n").encode())
except (EOFError, KeyboardInterrupt, OSError):
    pass
client.close()
