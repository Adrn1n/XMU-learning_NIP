<!--
任务
熟悉基本套接字相关函数
利用UDP协议编写简单的客户服务器程序，实现如下功能：
客户端：1. 等待键盘输入，若输入为EXIT则退出，否则转22. 将键盘接收内容发送内容给服务端3. 接收服务端反馈后显示在屏幕上4. 转到1
服务端：1. 侦听并等待客户端数据2. 收到数据后，将所收数据全部转大写后反馈给客户3. 转到1
采用TCP协议重新实现上述的任务。采用并发型服务器。

-->
# Report 5
## 1. Experiment Name
Socket Programming: Implementation of UDP and Concurrent TCP Client-Server Applications.

## 2. Experiment Tasks
- UDP Protocol Implementation:
    - Client:
        1. Wait for keyboard input, if the input is "EXIT", then exit, otherwise go to step 2
        2. Send the keyboard input to the server
        3. Receive the feedback from the server and display it on the screen
        4. Go back to step 1
    - Server:
        1. Listen and wait for client data
        2. After receiving the data, convert it to uppercase and send it back to the client
        3. Go back to step 1
- TCP Protocol Implementation:
    - Re-implement the above client-server logic using the TCP protocol
    - The TCP server must be a concurrent server capable of handling multiple client connections simultaneously

## 3. Experiment Environment and Tools
- M4 MacBook Air
- Python 3.12.12

## 4. Experiment Records and Result Analysis
### 4.1 Records
- `config.py`:
    ```python
    MAX_BUFFER_SIZE = 1024
    CHARSET = "utf-8"

    ```

#### UDP
- `udp_client.py`:
    ```python
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

    ```
- `udp_server.py`:
    ```python
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

    ```

#### TCP
- `tcp_client.py`:
    ```python
    import socket

    from config import CHARSET, MAX_BUFFER_SIZE

    IP = ""
    PORT = -1
    EXIT_COMMAND = "EXIT"

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

    ```
- `tcp_server.py`:
    ```python
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

    ```

### 4.2 Analysis
#### UDP
- Client:
    ```text
    ip = 127.0.0.1
    port = 61803
    Enter message ("EXIT" to quit): hello
    Response: HELLO
    Enter message ("EXIT" to quit): hi
    Response: HI
    Enter message ("EXIT" to quit): nihao1
    Response: NIHAO1
    Enter message ("EXIT" to quit): exit
    Response: EXIT
    Enter message ("EXIT" to quit): EXIT

    ```
- Server:
    ```text
    Port: 61803
    127.0.0.1: hello
    127.0.0.1: hi
    127.0.0.1: nihao1
    127.0.0.1: exit

    ```

The UDP server binds to port 61803 and uses a single-threaded loop to process incoming packets.

Because UDP is connectionless (`SOCK_DGRAM`), the server does not need to accept connections. It directly extracts the sender's address using `recvfrom()` and replies to that address using `sendto()`.

When the client enters "EXIT", the loop terminates locally, closing the client socket without sending "EXIT" to the server. The server remains online, waiting for packets from other potential clients.

#### TCP
- Client1:
    ```text
    ip = 127.0.0.1
    port = 58854
    Enter message ("EXIT" to quit): hi0
    Response: HI0
    Enter message ("EXIT" to quit): hello0
    Response: HELLO0
    Enter message ("EXIT" to quit): nihao0
    Response: NIHAO0
    Enter message ("EXIT" to quit): zaijian0
    Response: ZAIJIAN0
    Enter message ("EXIT" to quit): EXIT

    ```
- Client2:
    ```text
    ip = 127.0.0.1
    port = 58854
    Enter message ("EXIT" to quit): hi1
    Response: HI1
    Enter message ("EXIT" to quit): hello1
    Response: HELLO1
    Enter message ("EXIT" to quit): nihao1
    Response: NIHAO1
    Enter message ("EXIT" to quit): zaijian1
    Response: ZAIJIAN1
    Enter message ("EXIT" to quit): EXIT

    ```
- Server:
    ```text
    Port: 58854
    New connection from 127.0.0.1:58947
    127.0.0.1: hi0
    127.0.0.1: hello0
    New connection from 127.0.0.1:58982
    127.0.0.1: hi1
    127.0.0.1: hello1
    127.0.0.1: nihao1
    127.0.0.1: nihao0
    127.0.0.1: zaijian0
    Connection from 127.0.0.1: 58947 closed.
    127.0.0.1: zaijian1
    Connection from 127.0.0.1: 58982 closed.

    ```

The TCP server is connection-oriented (`SOCK_STREAM`) and implements concurrency using Python's threading library.

When Client 1 connects, the server accepts the connection and spawns a new thread executing handle_client.

While Client 1 is active, Client 2 connects. The main server thread accepts Client 2's connection immediately and spawns another thread.

The interleaved server logs prove that the server handles both clients concurrently.

When a client inputs "EXIT", the client-side socket closes. This causes the server's `conn.recv()` to return an empty byte string (`b''`). The server detects this, breaks the processing loop, closes the connection socket, and terminates the corresponding thread safely.

## 5. Problems Encountered and Solutions
### 5.1 Problems
None

### 5.2 Solutions
None
