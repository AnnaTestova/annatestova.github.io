import socket
import threading
import time
import os

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def receive_messages(sock):
    while True:
        try:
            header = sock.recv(1024)
            if not header:
                print("[INFO] Server closed the connection")
                break

            if header.startswith(b"FILE:"):
                _, filename, filesize = header.decode().split(":", 2)
                filesize = int(filesize)
                file_data = b""
                while len(file_data) < filesize:
                    chunk = sock.recv(min(4096, filesize - len(file_data)))
                    if not chunk:
                        break
                    file_data += chunk

                save_path = os.path.join(DOWNLOAD_DIR, filename)
                with open(save_path, "wb") as f:
                    f.write(file_data)
                print(f"\nReceived file saved as {save_path}\n")
            else:
                print(header.decode())

        except Exception:
            print("[ERROR] Connection closed")
            break
        time.sleep(0.1)

def send_file(sock, filepath):
    if not os.path.exists(filepath):
        print("[ERROR] File doesn't exist.")
        return

    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    header = f"FILE:{filename}:{filesize}".encode()

    try:
        sock.send(header)
        with open(filepath, "rb") as f:
            while chunk := f.read(4096):
                sock.sendall(chunk)
        print(f"[FILE SENT] {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to send file: {e}")

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(("localhost", 5555))
        print("You're now connected")
    except ConnectionRefusedError:
        print("[ERROR] Server isn't running or connection is refused. Make sure the server is online")
        return

    nickname = input("Enter your nickname: ").strip()
    if not nickname:
        print("[ERROR] Nickname cannot be empty")
        return
    client.send(nickname.encode())

    thread = threading.Thread(target=receive_messages, args=(client,))
    thread.daemon = True
    thread.start()

    print("""
          You joined the chat
          Availlable functions:
          /contacts - to get the list of online users
          quit - to leave the chat
          /private nickname message - to send a private message to a sertain person
          /sendfile path/to/file.ext - to send the file/photo
          
          """)

    while True:
        try:
            msg = input()

            # "/private" command
            if msg.strip().lower().startswith("/private"):
                parts = msg.strip().split(" ", 2)
                if len(parts) < 3:
                    print("[ERROR] Usage: /private nickname message")
                    continue
                to_nick = parts[1]
                message = parts[2]
                client.send(f"PRIVATE:{to_nick}:{nickname}:{message}".encode())
                continue

            # "/sendfile" command
            if msg.strip().lower().startswith("/sendfile"):
                parts = msg.strip().split(" ", 1)
                if len(parts) < 2:
                    print("[ERROR] Usage: /sendfile path/to/file.ext")
                    continue
                filepath = parts[1].strip()
                send_file(client, filepath)
                continue

            # "exit" command
            if msg.strip().lower() in ["exit"]:
                print("Disconnecting...")
                break

            client.send(msg.encode())
        except Exception as e:
            print(f"[ERROR] Couldn't send message: {e}")
            break

if __name__ == "__main__":
    start_client()

