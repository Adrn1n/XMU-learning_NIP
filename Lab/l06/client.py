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
    def lpwd():
        print(os.getcwd())
        return True

    def cd(self, tar_dir):
        self.tools.send_header({"cmd": "cd", "dir": tar_dir if tar_dir else "/"})
        res = self.tools.recv_header()
        if self.__check_res(res):
            return True
        return False

    @staticmethod
    def lcd(tar_dir):
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
