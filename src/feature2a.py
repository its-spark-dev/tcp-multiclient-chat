import socket
import threading

HOST = '127.0.0.1'
PORT = 5000

#Initializes the socket object using IPv4 (AF_INET) and TCP (SOCK_STREAM)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Prevents port in use errors
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#Binds socket to a single tuple of IP and port
server.bind((HOST, PORT))

#Puts socket in server mode
server.listen()
print(f"Server listening on {HOST}:{PORT}")

#Empty dictionary (username, socket), creates a list of who is in the chat
clients = {}
clientsLock = threading.Lock()


def handleClients(conn, addr):
    username = None
    try:
        #Asks for a username inside the thread so the accept loop is never blocked
        conn.sendall("Enter Username: ".encode())
        username = conn.recv(1024).decode().strip()

        #Waits till no one else is talking to client then uses it and gives it back
        with clientsLock:
            clients[username] = conn
        print(f"{username} connected from {addr}")

        while True:
            #Tracking if this client sent a message
            data = conn.recv(1024)
            #Empty bytes meaning the client disconnected
            if not data:
                break
            
            #Actually makes the message thats readable
            message = f"{username}: {data.decode().strip()}\n"

            #Sends the message to every client except the sender
            with clientsLock:
                for otherName, otherConn in clients.items():
                    if otherName != username:
                        try:
                            otherConn.sendall(message.encode())
                        except OSError:
                            pass
    except OSError as error:
        print(f"Error with {addr}: {error}")
    finally:
        #Removeing client and close socket when it leaves
        with clientsLock:
            if username is not None and clients.get(username) is conn:
                del clients[username]
        conn.close()
        print(f"{username or addr} disconnected")


while True:
    conn, addr = server.accept()

    thread = threading.Thread(target = handleClients, args = (conn, addr), daemon = True)

    thread.start()
