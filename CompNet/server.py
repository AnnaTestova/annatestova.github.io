import socket
import threading
import os

clients = {}       
addresses = {}   

# Saving messages to a file
def save_message(message):
    with open("history.txt", "a") as file:
        file.write(message + "\n")

# Loading messages from history file
def load_chat_history():
    history_lines = []
    if os.path.exists("history.txt"):
        try:
            with open("history.txt", "r") as file:
                history_lines = file.readlines()
        except Exception as e:
            print(f"[ERROR] Could not load chat history: {e}")
    return history_lines

# Sending message to all clients, except sender
def broadcast(msg, sender_conn):
    for conn in clients.values():
        if conn != sender_conn:
            try:
                conn.send(msg.encode())
            except:
                pass
    save_message(msg)

# Sending private message
def send_private_message(to_nick, message):
    conn = clients.get(to_nick)
    if conn:
        try:
            conn.send(message.encode())
        except:
            pass
    save_message(f"[Private] {message}")

# Sending file/photo to all clients except sender
def broadcast_file(filename, filedata, sender_conn):
    header = f"FILE:{filename}:{len(filedata)}".encode()
    for conn in clients.values():
        if conn != sender_conn:
            try:
                conn.send(header)
                conn.sendall(filedata)
            except:
                pass

# Handling one client
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr}")
    nickname = None

    try:
        conn.settimeout(10)
        nickname = conn.recv(1024).decode()
        conn.settimeout(None)

        if not nickname:
            raise Exception("Client disconnected during nickname registration")

        clients[nickname] = conn
        addresses[conn] = addr

        history = load_chat_history()
        for line in history:
            try:
                conn.send(line.encode())
            except Exception as e:
                print(f"[ERROR] Failed to send history to {nickname}: {e}")
                break

        welcome_msg = f"{nickname} joined the chat"
        print(welcome_msg)
        broadcast(welcome_msg, conn)
        save_message(welcome_msg)

        while True:
            header = conn.recv(1024)
            if not header:
                break

            if header.startswith(b"FILE:"):
                parts = header.decode().split(":", 2)
                if len(parts) == 3:
                    _, filename, filesize = parts
                    filesize = int(filesize)
                    filedata = b""
                    while len(filedata) < filesize:
                        chunk = conn.recv(min(4096, filesize - len(filedata)))
                        if not chunk:
                            break
                        filedata += chunk
                    broadcast_file(filename, filedata, conn)
                continue

            msg = header.decode()
            if not msg:
                break

            if msg.strip() == "/contacts":
                contact_list = ", ".join(clients.keys())
                try:
                    conn.send(f"[Server] Online users: {contact_list}".encode())
                except:
                    pass
                continue

            if msg.startswith("PRIVATE:"):
                try:
                    parts = msg.split(":", 3)
                    if len(parts) == 4:
                        _, to_nick, from_nick, message = parts
                        send_private_message(to_nick, f"[Private from {from_nick}]: {message}")
                    else:
                        conn.send("Error: Invalid private message format".encode())
                except Exception as e:
                    conn.send("Error processing private message".encode())
            else:
                broadcast(f"{nickname}: {msg}", conn)

    except Exception as e:
        print(f"[ERROR in handle_client] {addr}: {e}")

    finally:
        print(f"[DISCONNECTED] {addr}")
        disconnect_msg = ""
        if nickname and nickname in clients:
            disconnect_msg = f"{nickname} left the chat"
            temp_conn = clients[nickname]
            del clients[nickname]
            del addresses[temp_conn]
            broadcast(disconnect_msg, temp_conn)
            save_message(disconnect_msg)
        elif nickname:
            disconnect_msg = f"{nickname} (at {addr}) left"
            save_message(disconnect_msg)
        else:
            disconnect_msg = f"An unknown client at {addr} left"
            save_message(disconnect_msg)

        try:
            conn.close()
        except Exception as e:
            print(f"[ERROR] Error closing connection for {addr}: {e}")


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("localhost", 5555))
    except OSError as e:
        print(f"[ERROR] Failed to bind server: {e}")
        return

    server.listen()
    print("[SERVER STARTED] Listening on port 5555...")

    while True:
        try:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()
        except KeyboardInterrupt:
            print("\n[SERVER SHUTDOWN] Shutting down server")
            break
        except Exception as e:
            print(f"[ERROR] Server accept failed: {e}")

if __name__ == "__main__":
    start_server()

