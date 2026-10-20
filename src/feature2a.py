import socket
import threading

HOST = '127.0.0.1'
PORT = 12345

#Initializes the socket object using IPv4 (AF_INET) and TCP (SOCK_STREAM)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Prevents port in use errors
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#Binds socket to a single tuple of IP and port
server.bind((HOST, PORT))

#Puts socket in server mode
server.listen()
print(f"Server listening on {HOST}:{PORT}")

