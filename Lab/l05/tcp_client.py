import socket

IP = ""
PORT = -1
EXIT_COMMAND = "EXIT"
CHARSET = "utf-8"
MAX_BUFFER_SIZE = 1024

if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = IP if IP else input("ip = ")
    port = PORT if PORT >= 0 else int(input("port = "))
    client_socket.connect((ip, port))
    while True:
        msg = input('Enter message ("EXIT" to quit): ')
        if msg != EXIT_COMMAND:
            client_socket.send(msg.encode(CHARSET))
            data = client_socket.recv(MAX_BUFFER_SIZE)
            print(f"Response: {data.decode(CHARSET)}")
        else:
            break
    client_socket.close()
