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
