<!--
任务
利用TCP协议编写一个简单的文件服务器和客户端。
支持功能：
1. list：列表远端目录下的文件和目录信息（目录用方括号括起以示区分）
2. pwd: 查看远端当前目录
3. lpwd: 查看本地当前目录
4. cd xxxxx:  切换远端当前目录为xxxxx
5. lcd xxxxx: 切换本地当前目录为xxxxx
6. down xxxxx: 下载远端当前目录下的文件xxxxx到客户端的当前目录下
7. exit：断开连接并退出
注意：上述描述的是各功能的正常行为，各种出错情况请参照常见文件或ftp操作自行补充，尽量完善。
-->
# Report 6
## 1. Experiment Name

## 2. Experiment Tasks

## 3. Experiment Environment and Tools
- M4 MacBook Air
- Python 3.12.12

## 4. Experiment Records and Result Analysis
### 4.1 Records
- `config.py`:
    ```python
    CHARSET = "utf-8"
    HEADER_FORMAT = "!I"

    ```
- `tools.py`:
    ```python
    import json
    import struct


    class Tools:
        def __init__(self, conn, charset="utf-8", header_format="!I"):
            self.conn = conn
            self.charset = charset
            self.header_format = header_format
            self.format_len = struct.calcsize(header_format)

        def send_header(self, header):
            header = json.dumps(header).encode(self.charset)
            header = struct.pack(self.header_format, len(header)) + header
            self.conn.sendall(header)
            return header

        def __recv(self, size):
            data = b""
            while len(data) < size:
                chnk = self.conn.recv(size - len(data))
                if chnk:
                    data += chnk
                else:
                    return None
            return data

        def recv_header(self):
            l = self.__recv(self.format_len)
            if l is not None:
                l = struct.unpack(self.header_format, l)[0]
                header = self.__recv(l)
                if header is not None:
                    return json.loads(header.decode(self.charset))
            return None

    ```
- `server.py`:
    ```python
    import os
    import socket
    import threading

    import tools
    from config import CHARSET, HEADER_FORMAT


    class FileServer:
        @staticmethod
        def check_safe_path(root: str, target: str):
            abs_root = os.path.realpath(root)
            abs_target = os.path.realpath(target)
            return os.path.commonpath([abs_root, abs_target]) == abs_root

        @staticmethod
        def get_real_path(root: str, cur_dir: str, path):
            if not path.startswith("/"):
                return os.path.abspath(os.path.join(cur_dir, path))
            else:
                return os.path.abspath(os.path.join(root, path[1:]))

        def __init__(
            self, conn, root_dir=os.path.abspath("."), max_read=4096, *args, **kwargs
        ):
            self.tools = tools.Tools(conn=conn, *args, **kwargs)
            self.root_dir = root_dir
            self.current_dir = root_dir
            self.max_read = max_read

        def list(self, _):
            self.tools.send_header(
                {
                    "stats": "OK",
                    "files": [
                        {
                            "name": f,
                            "is_dir": os.path.isdir(os.path.join(self.current_dir, f)),
                        }
                        for f in os.listdir(self.current_dir)
                    ],
                }
            )
            return True

        def pwd(self, _):
            rel_path = os.path.relpath(self.current_dir, self.root_dir)
            self.tools.send_header(
                {
                    "stats": "OK",
                    "dir": "/" + rel_path.replace(os.sep, "/") if rel_path != "." else "/",
                }
            )
            return True

        def cd(self, header):
            tar_dir = header.get("dir")
            if tar_dir:
                tar_dir = self.get_real_path(self.root_dir, self.current_dir, tar_dir)
                safe = self.check_safe_path(self.root_dir, tar_dir)
                if os.path.isdir(tar_dir) and safe:
                    self.current_dir = tar_dir
                    self.tools.send_header({"stats": "OK"})
                    return True
                elif not safe:
                    self.tools.send_header(
                        {
                            "stats": "perm_denied",
                            "info": "Cannot access outside of root directory",
                        }
                    )
                else:
                    self.tools.send_header(
                        {"stats": "err", "info": f"Directory not found: {tar_dir}"}
                    )
            else:
                self.tools.send_header({"stats": "err", "info": "Missing <dir> parameter"})
            return False

        def down(self, header):
            f_name = header.get("f_name")
            if f_name:
                f_name = self.get_real_path(self.root_dir, self.current_dir, f_name)
                safe = self.check_safe_path(self.root_dir, f_name)
                if os.path.isfile(f_name) and safe:
                    size = os.path.getsize(f_name)
                    self.tools.send_header({"stats": "OK", "size": size})
                    with open(f_name, "rb") as f:
                        while True:
                            chnk = f.read(self.max_read)
                            if not chnk:
                                break
                            self.tools.conn.sendall(chnk)
                    return True
                elif not safe:
                    self.tools.send_header(
                        {
                            "stats": "perm_denied",
                            "info": "Cannot access outside of root directory",
                        }
                    )
                else:
                    self.tools.send_header(
                        {"stats": "err", "info": f"File not found: {f_name}"}
                    )
            else:
                self.tools.send_header(
                    {"stats": "err", "info": "Missing <f_name> parameter"}
                )
            return False

        def exit(self, _):
            self.tools.send_header({"stats": "OK"})
            return True

        commands = {"list": list, "pwd": pwd, "cd": cd, "down": down, "exit": exit}


    def run(conn, addr, root_dir):
        print(f"New connection from {addr[0]}:{addr[1]}")
        fs = FileServer(conn, root_dir, charset=CHARSET, header_format=HEADER_FORMAT)
        while True:
            header = fs.tools.recv_header()
            if header:
                cmd = header.get("cmd")
                if cmd in fs.commands:
                    getattr(fs, cmd)(header)
                else:
                    fs.tools.send_header(
                        {"stats": "fail", "info": f"Unknown command: {cmd}"}
                    )
            else:
                break
        conn.close()
        print(f"Connection from {addr[0]}:{addr[1]} closed.")


    IP = "0.0.0.0"
    PORT = 0
    MAX_WAITING_CONNECTIONS = 5
    ROOT_DIR = os.path.abspath(".")

    if __name__ == "__main__":
        ip = IP if IP else input("ip = ")
        port = PORT if PORT >= 0 else int(input("port = "))
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((ip, port))
        server_socket.listen(MAX_WAITING_CONNECTIONS)
        print(f"Port: {server_socket.getsockname()[1]}")
        while True:
            thread = threading.Thread(target=run, args=(*server_socket.accept(), ROOT_DIR))
            thread.start()

    ```
- `client.py`:
    ```python
    import os
    import socket

    import tools
    from config import CHARSET, HEADER_FORMAT


    class FileClient:
        command_help = "help"

        @staticmethod
        def parse_cd_lcd_down(*args):
            return [args[0]] if args else [None]

        def __init__(self, max_write=4096, *args, **kwargs):
            self.max_write = max_write
            self.tools = tools.Tools(*args, **kwargs)
            self.alive = True

        def __close(self):
            self.tools.conn.close()
            self.alive = False

        def __check_res(self, res):
            if res:
                if res.get("stats") == "OK":
                    return True
                else:
                    print(res)
            else:
                print("No response received")
                self.__close()
            return False

        def list(self):
            self.tools.send_header({"cmd": "list"})
            res = self.tools.recv_header()
            if self.__check_res(res):
                for item in res.get("files", []):
                    if item.get("is_dir"):
                        print(f"[{item.get('name')}]")
                    else:
                        print(item.get("name"))
                return True
            return False

        def pwd(self):
            self.tools.send_header({"cmd": "pwd"})
            res = self.tools.recv_header()
            if self.__check_res(res):
                tar_dir = res.get("dir")
                if tar_dir is not None:
                    print(tar_dir)
                    return True
                else:
                    print("No directory information received")
            return False

        @staticmethod
        def lpwd(_):
            print(os.getcwd())
            return True

        def cd(self, tar_dir):
            self.tools.send_header({"cmd": "cd", "dir": tar_dir if tar_dir else "/"})
            res = self.tools.recv_header()
            if self.__check_res(res):
                return True
            return False

        @staticmethod
        def lcd(_, tar_dir):
            tar_dir = tar_dir if tar_dir else os.path.expanduser("~")
            if os.path.isdir(tar_dir):
                os.chdir(tar_dir)
                return True
            else:
                print(f"Directory not found: {tar_dir}")
            return False

        def down(self, f_name):
            self.tools.send_header({"cmd": "down", "f_name": f_name})
            res = self.tools.recv_header()
            if self.__check_res(res):
                size = res.get("size")
                if size is not None:
                    f_dir = os.path.dirname(f_name)
                    if f_dir:
                        os.makedirs(f_dir, exist_ok=True)
                    rem = size
                    with open(f_name, "wb") as f:
                        while rem > 0:
                            chnk = self.tools.conn.recv(min(self.max_write, rem))
                            if not chnk:
                                print("Connection interrupted during download")
                                return False
                            f.write(chnk)
                            rem -= len(chnk)
                    return True
                else:
                    print("No size information received")
            return False

        def exit(self):
            self.tools.send_header({"cmd": "exit"})
            res = self.tools.recv_header()
            if self.__check_res(res):
                self.__close()
                return True
            return False

        commands = {
            "list": (
                "list: List files and directories in the current directory on the server (directories are enclosed in square brackets)",
                list,
                None,
            ),
            "pwd": ("pwd: Show the current directory on the server", pwd, None),
            "lpwd": ("lpwd: Show the current directory on the client", lpwd, None),
            "cd": (
                "cd <directory>: Change the current directory on the server",
                cd,
                parse_cd_lcd_down,
            ),
            "lcd": (
                "lcd <directory>: Change the current directory on the client",
                lcd,
                parse_cd_lcd_down,
            ),
            "down": (
                "down <filename>: Download a file from the server",
                down,
                parse_cd_lcd_down,
            ),
            "exit": ("exit: Disconnect from the server and exit", exit, None),
        }


    IP = ""
    PORT = -1

    if __name__ == "__main__":
        ip = IP if IP else input("ip = ")
        port = PORT if PORT >= 0 else int(input("port = "))
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((ip, port))
        fc = FileClient(conn=conn, charset=CHARSET, header_format=HEADER_FORMAT)
        while fc.alive:
            inp = input('Command (type "help" for available commands) = ').split()
            if inp:
                cmd, pars = inp[0], inp[1:]
                if cmd in fc.commands:
                    _, action, parser = fc.commands[cmd]
                    if parser:
                        params = parser(*pars)
                        action(fc, *params)
                    else:
                        action(fc)
                    continue
                elif cmd == fc.command_help:
                    for command, (description, _, _) in fc.commands.items():
                        print(description)
                    continue
            print("Unknown command")

    ```

### 4.2 Analysis

## 5. Problems Encountered and Solutions
### 5.1 Problems
None.

### 5.2 Solutions
None.
