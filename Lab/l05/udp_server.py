import socket

from config import MAX_BUFFER_SIZE, CHARSET

IP = "0.0.0.0"
PORT = 0

if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = IP if IP else input("ip = ")
    port = PORT if PORT >= 0 else int(input("port = "))
    server_socket.bind((ip, port))
    print(f"Port: {server_socket.getsockname()[1]}")
    while True:
        data, addr = server_socket.recvfrom(MAX_BUFFER_SIZE)
        data = data.decode(CHARSET)
        print(f"{addr[0]}: {data}")
        server_socket.sendto(data.upper().encode(CHARSET), addr)
