import socket

from config import CHARSET, MAX_BUFFER_SIZE

IP = ""
PORT = -1
EXIT_COMMAND = "EXIT"

if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = IP if IP else input("ip = ")
    port = PORT if PORT >= 0 else int(input("port = "))
    while True:
        msg = input('Enter message ("EXIT" to quit): ')
        if msg != EXIT_COMMAND:
            client_socket.sendto(msg.encode(CHARSET), (ip, port))
            data, _ = client_socket.recvfrom(MAX_BUFFER_SIZE)
            print(f"Response: {data.decode(CHARSET)}")
        else:
            break
    client_socket.close()
