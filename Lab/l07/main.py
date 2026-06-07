import socket

from tools import Tools
from config import PORT, CHARSET


class POP3Client:
    @staticmethod
    def check_response(resp):
        if resp and resp.startswith("+OK"):
            return True
        else:
            return False

    def __init__(self, host, port=110, charset="utf-8"):
        self.host = host
        self.port = port
        self.charset = charset
        self.tools = Tools(charset)
        self.sock = None
        self.alive = False

    def __recv_line(self):
        line = b""
        while not line.endswith(b"\r\n"):
            chunk = self.sock.recv(1)
            if not chunk:
                self.alive = False
                raise ConnectionError("Connection closed by server")
            line += chunk
        return line.decode(self.charset, errors="ignore").rstrip("\r\n")

    def __send_cmd(self, cmd):
        self.sock.sendall(f"{cmd}\r\n".encode(self.charset))
        return self.__recv_line()

    def __recv_multiline(self):
        lines = []
        while True:
            line = self.__recv_line()
            if line == ".":
                break
            elif line.startswith("."):
                line = line[1:]
            lines.append(line)
        return "\n".join(lines)

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((socket.gethostbyname(self.host), self.port))
        welcome = self.__recv_line()
        print(f"Server: {welcome}")
        self.alive = POP3Client.check_response(welcome)
        return self.alive

    def login(self, name, pwd):
        resp = self.__send_cmd(f"USER {name}")
        print(f"Server: {resp}")
        if POP3Client.check_response(resp):
            resp = self.__send_cmd(f"PASS {pwd}")
            print(f"Server: {resp}")
            return POP3Client.check_response(resp)
        return False

    def stat(self):
        resp = self.__send_cmd("STAT")
        print(f"Server: {resp}")
        if POP3Client.check_response(resp):
            parts = resp.split()
            return int(parts[1]), int(parts[2])
        return None

    def list(self):
        resp = self.__send_cmd("LIST")
        print(f"Server: {resp}")
        if POP3Client.check_response(resp):
            res = self.__recv_multiline()
            return [tuple(map(int, line.split())) for line in res.splitlines()]
        return None

    def retr(self, n):
        resp = self.__send_cmd(f"RETR {n}")
        print(f"Server: {resp}")
        if POP3Client.check_response(resp):
            return self.__recv_multiline()
        return None

    def dele(self, n):
        resp = self.__send_cmd(f"DELE {n}")
        print(f"Server: {resp}")
        return POP3Client.check_response(resp)

    def rset(self):
        resp = self.__send_cmd("RSET")
        print(f"Server: {resp}")
        return POP3Client.check_response(resp)

    def top(self, n, m):
        resp = self.__send_cmd(f"TOP {n} {m}")
        print(f"Server: {resp}")
        if POP3Client.check_response(resp):
            return self.__recv_multiline()
        return None

    def quit(self):
        resp = self.__send_cmd("QUIT")
        print(f"Server: {resp}")
        if POP3Client.check_response(resp):
            self.sock.close()
            self.alive = False
            return True
        return False


def parse_command(line):
    parts = line.split()
    if parts:
        return parts[0], [int(arg) if arg.isdigit() else arg for arg in parts[1:]]
    return None, []


def disp_stat(res):
    print(f"Total Messages: {res[0]}, Total Size: {res[1]} bytes")


def disp_list(res):
    if res:
        for num, size in res:
            print(f"Message {num}: {size} bytes")


COMMANDS = {
    "stat": (
        "Display the number of messages and their sizes; Usage: stat",
        POP3Client.stat,
        disp_stat,
    ),
    "list": (
        "List all messages with their sizes; Usage: list",
        POP3Client.list,
        disp_list,
    ),
    "retr": (
        "Retrieve the full content of a specific message; Usage: retr <message_number>",
        POP3Client.retr,
        None,
    ),
    "dele": (
        "Mark a specific message for deletion; Usage: dele <message_number>",
        POP3Client.dele,
        None,
    ),
    "rset": (
        "Unmark any messages marked for deletion; Usage: rset",
        POP3Client.rset,
        None,
    ),
    "top": (
        "Retrieve the top lines of a specific message; Usage: top <message_number> <line_count>",
        POP3Client.top,
        None,
    ),
    "quit": (
        "Exit the client and commit any deletions; Usage: quit",
        POP3Client.quit,
        None,
    ),
}
HELP_COMMAND = "help"

if __name__ == "__main__":
    server_addr = input("Enter POP3 server address = ")
    server_port = PORT if PORT >= 0 else int(input("Enter POP3 server port = "))
    client = POP3Client(server_addr, server_port, charset=CHARSET)
    if client.connect():
        username = input("Username = ")
        passwd = client.tools.get_pwd_input("Password = ")
        if client.login(username, passwd):
            while client.alive:
                inp = input('\nEnter command (type "help" for available commands) = ')
                command, args = parse_command(inp)
                result = None
                if command in COMMANDS:
                    try:
                        _, action, disp = COMMANDS[command]
                        result = action(client, *args)
                        if result:
                            if disp:
                                disp(result)
                            else:
                                print(result)
                    except Exception as e:
                        print(f"Error executing command '{command}': {e}")
                elif command == HELP_COMMAND:
                    for command, (description, _, _) in COMMANDS.items():
                        print(command + ": " + description)
                else:
                    print(f"Unknown command: {command}")
        else:
            print("Login failed")
    else:
        print("Connection failed")
