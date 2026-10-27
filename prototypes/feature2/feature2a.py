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
print("Type Ctrl + C to close server")

#Empty dictionary (username, socket), creates a list of who is in the chat
clients = {}
clientsLock = threading.Lock()


def handleClients(conn, addr):
    username = None
    try:
        #Asks for a username inside the thread so the accept loop is never blocked
        conn.sendall("Enter Username: \n".encode())
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
            
            text = data.decode().strip()
 
            #Skip blank lines
            if not text:
                continue
 
            #Private message format: @username message
            if text.startswith("@"):
                #Remove the "@" and split on the FIRST space only,
                #so "@bob hi there" -> target = "bob", privateMsg = "hi there"
                parts = text[1:].split(" ", 1)
                target = parts[0]
                privateMsg = parts[1].strip() if len(parts) > 1 else ""
 
                #"@bob" with no message, or just "@"
                if not target or not privateMsg:
                    conn.sendall("[Server] Usage: @username message\n".encode())
                    continue
 
                #Don't let a client message themselves
                if target == username:
                    conn.sendall("[Server] You can't send a private message to yourself.\n".encode())
                    continue
 
                #Look up the target's socket in the dictionary
                with clientsLock:
                    targetConn = clients.get(target)
 
                if targetConn is None:
                    #Target username isn't connected
                    conn.sendall(f"[Server] User '{target}' not found.\n".encode())
                else:
                    try:
                        #Send ONLY to the target, labelled with who sent it
                        targetConn.sendall(f"[Private] {username}: {privateMsg}\n".encode())
                        #Confirm to the sender that it was delivered
                        conn.sendall(f"[To {target}] {privateMsg}\n".encode())
                        print(f"Private message: {username} -> {target}")
                    except OSError:
                        conn.sendall(f"[Server] Could not deliver message to '{target}'.\n".encode())
            else:
                #Anything that doesn't start with @ is the wrong format
                conn.sendall("[Server] Use the format @username message\n".encode())
                
    except OSError as error:
        print(f"Error with {addr}: {error}")
    finally:
        #Removeing client and close socket when it leaves
        with clientsLock:
            if username is not None and clients.get(username) is conn:
                del clients[username]
        conn.close()
        print(f"{username or addr} disconnected")


try:
    while True:
        conn, addr = server.accept()

        thread = threading.Thread(target = handleClients, args = (conn, addr), daemon = True)

        thread.start()
except KeyboardInterrupt:
    #Ctrl + C stops the accept loop instead of showing a traceback
    print("\nShutting down server")
finally:
    #Disconnects every client so their threads end cleanly, then closes the server socket
    with clientsLock:
        for clientConn in clients.values():
            try:
                clientConn.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
    server.close()
