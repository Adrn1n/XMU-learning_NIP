import socket
import threading

from config import MAX_BUFFER_SIZE, CHARSET

IP = "0.0.0.0"
PORT = 0
MAX_WAITING_CONNECTIONS = 5


def handle_client(conn, addr):
    print(f"New connection from {addr[0]}:{addr[1]}")
    while True:
        data = conn.recv(MAX_BUFFER_SIZE)
        if data:
            data = data.decode(CHARSET)
            print(f"{addr[0]}: {data}")
            conn.send(data.upper().encode(CHARSET))
        else:
            break
    conn.close()
    print(f"Connection from {addr[0]}: {addr[1]} closed.")


if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = IP if IP else input("ip = ")
    port = PORT if PORT >= 0 else int(input("port = "))
    server_socket.bind((ip, port))
    server_socket.listen(MAX_WAITING_CONNECTIONS)
    print(f"Port: {server_socket.getsockname()[1]}")
    while True:
        thread = threading.Thread(target=handle_client, args=server_socket.accept())
        thread.start()
