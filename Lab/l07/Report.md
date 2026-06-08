<!--
任务
采用TCP协议实现一个简易的POP3客户端。支持功能：
1. 具有基本的登录和验证的功能，注意输入口令要以*号屏蔽。
2. 登录后能查看邮件列表，读取某邮件内容，删除某邮件内容

DNS的操作——gethostbyname ()
功能：查找主机名返回IP地址。
语法：# include <netdb.h>
　　　struct hostent *gethostbyname (const char *hostname);
返回值：成功时返回非空指针，失败时返回NULL。
说明：hostent结构的说明如下：
　　　struct hostent{
　　　　char	*h_name;	//主机的正式（规范）名字
　　　　char	**h_aliases;	//指向别名指针队列的指针
　　　　int	h_addrtype;	//AF_INET或AF_INET6
　　　　int	h_length;	//地址长度：4或16
　　　　char	**h_addr_list;	//指向地址指针链的指针					//地址均为网络字节顺序
　　　}
    错误发生时本函数并不设置errno，而设置h_errno变量。用hstrerror (h_errno)可取得错误的ascii描述。

4038E24D1A5878051A7782454FFDEDCF

3446E4F2C87F28C8A92C337638C69357

其他相关知识回顾
POP3一般端口号为110
POP3主要命令有：
USER username 认证用户名
PASS password 认证密码认证，认证通过则状态转换
STAT 处理请求 server 回送邮箱统计资料，如邮件数、 邮件总字节数
LIST n 处理 server 返回指定邮件的大小等
RETR n 处理 server 返回邮件的全部文本
DELE n 处理 server 标记删除，QUIT 命令执行时才真正删除
RSET 处理撤消所有的 DELE 命令
TOP n,m 处理返回 n 号邮件的前 m 行内容，m 必须是自然数
QUIT 希望结束会话。如果 server 处于"处理" 状态，则现在进入"更新"状态，删除那些标记成删除的邮件。如果 server 处于"认可"状态，则结束会话时 server 不进入"更新"状态 。
-->
# Report 7
## 1. Experiment Name

## 2. Experiment Tasks

## 3. Experiment Environment and Tools
- M4 MacBook Air
- Python 3.12.12

## 4. Experiment Records and Result Analysis
### 4.1 Records
- `config.py`:
    ```python
    PORT = 110
    CHARSET = "utf-8"

    ```
- `tools.py`:
    ```python
    import sys


    class Tools:
        enter_char = "\r\n"
        backspace_char = "\x7f\x08"
        interrupt_char = "\x03"

        @staticmethod
        def __flush_input(inp):
            sys.stdout.write(inp)
            sys.stdout.flush()

        @staticmethod
        def __increase_pwd(pwd, char):
            Tools.__flush_input("*")
            return pwd + char

        @staticmethod
        def __back_pwd(pwd):
            if len(pwd) > 0:
                pwd = pwd[:-1]
                Tools.__flush_input("\b \b")
            return pwd

        def __init__(self, charset="utf-8"):
            self.charset = charset

        def get_pwd_input(self, prompt="Password: "):
            print(prompt, end="", flush=True)
            termios = None
            tty = None
            fd = None
            org_sets = None
            msvcrt = None
            if not sys.platform == "win32":
                import termios
                import tty

                fd = sys.stdin.fileno()
                org_sets = termios.tcgetattr(fd)
            else:
                import msvcrt
            try:
                if not fd is None:
                    tty.setraw(fd)
                pwd = ""
                while True:
                    ch = (
                        sys.stdin.read(1)
                        if termios
                        else msvcrt.getch().decode(self.charset, errors="ignore")
                    )
                    if (
                        ch not in self.enter_char
                        and ch not in self.backspace_char
                        and ch != self.interrupt_char
                    ):
                        pwd = Tools.__increase_pwd(pwd, ch)
                    elif ch in self.backspace_char:
                        pwd = Tools.__back_pwd(pwd)
                    elif ch in self.enter_char:
                        break
                    else:
                        raise KeyboardInterrupt
            finally:
                if fd is not None and org_sets is not None:
                    termios.tcsetattr(fd, termios.TCSADRAIN, org_sets)
                print()
            return pwd

    ```
- `main.py`:
    ```python
    import socket

    from tools import Tools
    from config import PORT, CHARSET


    class POP3Client:
        @staticmethod
        def __check_response(resp):
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
            self.alive = POP3Client.__check_response(welcome)
            return self.alive

        def login(self, name, pwd):
            resp = self.__send_cmd(f"USER {name}")
            print(f"Server: {resp}")
            if POP3Client.__check_response(resp):
                resp = self.__send_cmd(f"PASS {pwd}")
                print(f"Server: {resp}")
                return POP3Client.__check_response(resp)
            return False

        def stat(self):
            resp = self.__send_cmd("STAT")
            print(f"Server: {resp}")
            if POP3Client.__check_response(resp):
                parts = resp.split()
                return int(parts[1]), int(parts[2])
            return None

        def list(self):
            resp = self.__send_cmd("LIST")
            print(f"Server: {resp}")
            if POP3Client.__check_response(resp):
                res = self.__recv_multiline()
                return [tuple(map(int, line.split())) for line in res.splitlines()]
            return None

        def retr(self, n):
            resp = self.__send_cmd(f"RETR {n}")
            print(f"Server: {resp}")
            if POP3Client.__check_response(resp):
                return self.__recv_multiline()
            return None

        def dele(self, n):
            resp = self.__send_cmd(f"DELE {n}")
            print(f"Server: {resp}")
            return POP3Client.__check_response(resp)

        def rset(self):
            resp = self.__send_cmd("RSET")
            print(f"Server: {resp}")
            return POP3Client.__check_response(resp)

        def top(self, n, m):
            resp = self.__send_cmd(f"TOP {n} {m}")
            print(f"Server: {resp}")
            if POP3Client.__check_response(resp):
                return self.__recv_multiline()
            return None

        def quit(self):
            resp = self.__send_cmd("QUIT")
            print(f"Server: {resp}")
            if POP3Client.__check_response(resp):
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

    ```

### 4.2 Analysis
```text
(base) b@MacBook-Air-6 Lab %  cd /Users/Shared/Files/XMU/Learning/NIP/Lab ; /usr/bin/env /opt/anaconda3/bin/python /Users/b/.vscode/extensions/ms-python.de
bugpy-2026.6.0-darwin-arm64/bundled/libs/debugpy/adapter/../../debugpy/launcher 63032 -- /Users/Shared/Files/XMU/Learning/NIP/Lab/l07/main.py 
Enter POP3 server address = a.com
Traceback (most recent call last):
  File "/Users/Shared/Files/XMU/Learning/NIP/Lab/l07/main.py", line 175, in <module>
    if client.connect():
       ^^^^^^^^^^^^^^^^
  File "/Users/Shared/Files/XMU/Learning/NIP/Lab/l07/main.py", line 50, in connect
    self.sock.connect((socket.gethostbyname(self.host), self.port))
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
socket.gaierror: [Errno 8] nodename nor servname provided, or not known
(base) b@MacBook-Air-6 Lab %  cd /Users/Shared/Files/XMU/Learning/NIP/Lab ; /usr/bin/env /opt/anaconda3/bin/python /Users/b/.vscode/extensions/ms-python.de
bugpy-2026.6.0-darwin-arm64/bundled/libs/debugpy/adapter/../../debugpy/launcher 63049 -- /Users/Shared/Files/XMU/Learning/NIP/Lab/l07/main.py 
Enter POP3 server address = pop.163.com
Server: +OK Welcome to coremail Mail Pop3 Server (163coms[10774b260cc7a37d26d71b52404dcf5cs])
Username = a@163.com
Password = ****************
Server: +OK core mail
Server: -ERR ûȨʹpop3
Login failed
(base) b@MacBook-Air-6 Lab %  cd /Users/Shared/Files/XMU/Learning/NIP/Lab ; /usr/bin/env /opt/anaconda3/bin/python /Users/b/.vscode/extensions/ms-python.de
bugpy-2026.6.0-darwin-arm64/bundled/libs/debugpy/adapter/../../debugpy/launcher 63084 -- /Users/Shared/Files/XMU/Learning/NIP/Lab/l07/main.py 
Enter POP3 server address = pop.163.com
Server: +OK Welcome to coremail Mail Pop3 Server (163coms[10774b260cc7a37d26d71b52404dcf5cs])
Username = liu_xingyi_001@163.com
Password = *
Server: +OK core mail
Server: -ERR Unable to log on
Login failed
(base) b@MacBook-Air-6 Lab %  cd /Users/Shared/Files/XMU/Learning/NIP/Lab ; /usr/bin/env /opt/anaconda3/bin/python /Users/b/.vscode/extensions/ms-python.de
bugpy-2026.6.0-darwin-arm64/bundled/libs/debugpy/adapter/../../debugpy/launcher 63130 -- /Users/Shared/Files/XMU/Learning/NIP/Lab/l07/main.py 
Enter POP3 server address = pop.163.com
Server: +OK Welcome to coremail Mail Pop3 Server (163coms[10774b260cc7a37d26d71b52404dcf5cs])
Username = liu_xingyi_001
Password = ****************
Server: +OK core mail
Server: +OK 7 message(s) [281652 byte(s)]

Enter command (type "help" for available commands) = help
stat: Display the number of messages and their sizes; Usage: stat
list: List all messages with their sizes; Usage: list
retr: Retrieve the full content of a specific message; Usage: retr <message_number>
dele: Mark a specific message for deletion; Usage: dele <message_number>
rset: Unmark any messages marked for deletion; Usage: rset
top: Retrieve the top lines of a specific message; Usage: top <message_number> <line_count>
quit: Exit the client and commit any deletions; Usage: quit

Enter command (type "help" for available commands) = a
Unknown command: a

Enter command (type "help" for available commands) = 
Unknown command: None

Enter command (type "help" for available commands) = stat
Server: +OK 7 281652
Total Messages: 7, Total Size: 281652 bytes

Enter command (type "help" for available commands) = stat 1
Error executing command 'stat': POP3Client.stat() takes 1 positional argument but 2 were given

Enter command (type "help" for available commands) = list
Server: +OK 7 281652
Message 1: 8594 bytes
Message 2: 65825 bytes
Message 3: 8331 bytes
Message 4: 65825 bytes
Message 5: 65825 bytes
Message 6: 65823 bytes
Message 7: 1429 bytes

Enter command (type "help" for available commands) = list 1
Error executing command 'list': POP3Client.list() takes 1 positional argument but 2 were given

Enter command (type "help" for available commands) = retr
Error executing command 'retr': POP3Client.retr() missing 1 required positional argument: 'n'

Enter command (type "help" for available commands) = retr 1 2
Error executing command 'retr': POP3Client.retr() takes 2 positional arguments but 3 were given

Enter command (type "help" for available commands) = retr 7
Server: +OK 1429 octets
Received: from liu_xingyi_001$163.com (
 [2409:8734:1a70:7e2:d836:3927:599f:47e6] ) by ajax-webmail-wmsvr-40-132
 (Coremail) ; Mon, 8 Jun 2026 13:42:09 +0800 (CST)
X-Originating-IP: [2409:8734:1a70:7e2:d836:3927:599f:47e6]
Date: Mon, 8 Jun 2026 13:42:09 +0800 (CST)
From: liu_xingyi_001 <liu_xingyi_001@163.com>
To: liu_xingyi_001@163.com
Subject: TEST
X-Priority: 3
X-Mailer: Coremail Webmail Server Version 2023.4-cmXT build
 20260403(27802f6d) Copyright (c) 2002-2026 www.mailtech.cn 163com
X-NTES-SC: AL_Qu2TAvSSuEsp7yOaZekcnEsVhOY6WsS1v/oi2Ydec8IFkQvK9TklfllNPkHr3fqSMRGomgSNcDh21el9U7h9MYQKjuHmVurOQZynWiGVSw==
Content-Type: multipart/alternative; 
        boundary="----=_Part_69566_1013729075.1780897329327"
MIME-Version: 1.0
Message-ID: <4cc99c6.4831.19ea5c0b0b0.Coremail.liu_xingyi_001@163.com>
X-Coremail-Locale: zh_CN
X-CM-TRANSID:hCgvCgD3_+oxViZqWHkEAA--.1535W
X-CM-SenderInfo: polxs55lqj5xjbqqiqqrwthudrp/xtbC7RHF+momVjEWoAAA3e
X-Coremail-Antispam: 1U5529EdanIXcx71UUUUU7vcSsGvfC2KfnxnUU==

------=_Part_69566_1013729075.1780897329327
Content-Type: text/plain; charset=GBK
Content-Transfer-Encoding: 7bit

temp
------=_Part_69566_1013729075.1780897329327
Content-Type: text/html; charset=GBK
Content-Transfer-Encoding: 7bit

<div data-ntes="ntes_mail_body_root" style="line-height:1.7;color:#000000;font-size:14px;font-family:Arial">temp</div>
------=_Part_69566_1013729075.1780897329327--

Enter command (type "help" for available commands) = dele
Error executing command 'dele': POP3Client.dele() missing 1 required positional argument: 'n'

Enter command (type "help" for available commands) = dele 1 2
Error executing command 'dele': POP3Client.dele() takes 2 positional arguments but 3 were given

Enter command (type "help" for available commands) = dele 7
Server: +OK core mail
True

Enter command (type "help" for available commands) = stat
Server: +OK 6 280223
Total Messages: 6, Total Size: 280223 bytes

Enter command (type "help" for available commands) = list
Server: +OK 6 280223
Message 1: 8594 bytes
Message 2: 65825 bytes
Message 3: 8331 bytes
Message 4: 65825 bytes
Message 5: 65825 bytes
Message 6: 65823 bytes

Enter command (type "help" for available commands) = rset 7
Error executing command 'rset': POP3Client.rset() takes 1 positional argument but 2 were given

Enter command (type "help" for available commands) = rset 
Server: +OK core mail
True

Enter command (type "help" for available commands) = list
Server: +OK 7 281652
Message 1: 8594 bytes
Message 2: 65825 bytes
Message 3: 8331 bytes
Message 4: 65825 bytes
Message 5: 65825 bytes
Message 6: 65823 bytes
Message 7: 1429 bytes

Enter command (type "help" for available commands) = top
Error executing command 'top': POP3Client.top() missing 2 required positional arguments: 'n' and 'm'

Enter command (type "help" for available commands) = top 7
Error executing command 'top': POP3Client.top() missing 1 required positional argument: 'm'

Enter command (type "help" for available commands) = top 7 8 9
Error executing command 'top': POP3Client.top() takes 3 positional arguments but 4 were given

Enter command (type "help" for available commands) = top 7 3
Server: +OK 1429 octets
Received: from liu_xingyi_001$163.com (
 [2409:8734:1a70:7e2:d836:3927:599f:47e6] ) by ajax-webmail-wmsvr-40-132
 (Coremail) ; Mon, 8 Jun 2026 13:42:09 +0800 (CST)
X-Originating-IP: [2409:8734:1a70:7e2:d836:3927:599f:47e6]
Date: Mon, 8 Jun 2026 13:42:09 +0800 (CST)
From: liu_xingyi_001 <liu_xingyi_001@163.com>
To: liu_xingyi_001@163.com
Subject: TEST
X-Priority: 3
X-Mailer: Coremail Webmail Server Version 2023.4-cmXT build
 20260403(27802f6d) Copyright (c) 2002-2026 www.mailtech.cn 163com
X-NTES-SC: AL_Qu2TAvSSuEsp7yOaZekcnEsVhOY6WsS1v/oi2Ydec8IFkQvK9TklfllNPkHr3fqSMRGomgSNcDh21el9U7h9MYQKjuHmVurOQZynWiGVSw==
Content-Type: multipart/alternative; 
        boundary="----=_Part_69566_1013729075.1780897329327"
MIME-Version: 1.0
Message-ID: <4cc99c6.4831.19ea5c0b0b0.Coremail.liu_xingyi_001@163.com>
X-Coremail-Locale: zh_CN
X-CM-TRANSID:hCgvCgD3_+oxViZqWHkEAA--.1535W
X-CM-SenderInfo: polxs55lqj5xjbqqiqqrwthudrp/xtbC7RHF+momVjEWoAAA3e
X-Coremail-Antispam: 1U5529EdanIXcx71UUUUU7vcSsGvfC2KfnxnUU==

------=_Part_69566_1013729075.1780897329327
Content-Type: text/plain; charset=GBK
Content-Transfer-Encoding: 7bit

Enter command (type "help" for available commands) = dele 7
Server: +OK core mail
True

Enter command (type "help" for available commands) = stat
Server: +OK 6 280223
Total Messages: 6, Total Size: 280223 bytes

Enter command (type "help" for available commands) = quit
Server: +OK core mail
True
(base) b@MacBook-Air-6 Lab %  cd /Users/Shared/Files/XMU/Learning/NIP/Lab ; /usr/bin/env /opt/anaconda3/bin/python /Users/b/.vscode/extensions/ms-python.de
bugpy-2026.6.0-darwin-arm64/bundled/libs/debugpy/adapter/../../debugpy/launcher 63344 -- /Users/Shared/Files/XMU/Learning/NIP/Lab/l07/main.py 
Enter POP3 server address = pop.163.com
Server: +OK Welcome to coremail Mail Pop3 Server (163coms[10774b260cc7a37d26d71b52404dcf5cs])
Username = liu_xingyi_001@163.com
Password = ****************
Server: +OK core mail
Server: +OK 6 message(s) [280223 byte(s)]

Enter command (type "help" for available commands) = stat
Server: +OK 6 280223
Total Messages: 6, Total Size: 280223 bytes

Enter command (type "help" for available commands) = lsit
Unknown command: lsit

Enter command (type "help" for available commands) = list
Server: +OK 6 280223
Message 1: 8594 bytes
Message 2: 65825 bytes
Message 3: 8331 bytes
Message 4: 65825 bytes
Message 5: 65825 bytes
Message 6: 65823 bytes

Enter command (type "help" for available commands) = quit
Server: +OK core mail
True
(base) b@MacBook-Air-6 Lab %  cd /Users/Shared/Files/XMU/Learning/NIP/Lab ; /usr/bin/env /opt/anaconda3/bin/python /Users/b/.vscode/extensions/ms-python.de
bugpy-2026.6.0-darwin-arm64/bundled/libs/debugpy/adapter/../../debugpy/launcher 63408 -- /Users/Shared/Files/XMU/Learning/NIP/Lab/l07/main.py 
Enter POP3 server address = pop.163.com
Server: +OK Welcome to coremail Mail Pop3 Server (163coms[10774b260cc7a37d26d71b52404dcf5cs])
Username = liu_xingyi_001@163.com
Password = ****************
Server: +OK core mail
Server: +OK 6 message(s) [280223 byte(s)]

Enter command (type "help" for available commands) = stat
Server: +OK 6 280223
Total Messages: 6, Total Size: 280223 bytes

Enter command (type "help" for available commands) = lsit
Unknown command: lsit

Enter command (type "help" for available commands) = list
Server: +OK 6 280223
Message 1: 8594 bytes
Message 2: 65825 bytes
Message 3: 8331 bytes
Message 4: 65825 bytes
Message 5: 65825 bytes
Message 6: 65823 bytes

Enter command (type "help" for available commands) = rset
Server: +OK core mail
True

Enter command (type "help" for available commands) = list
Server: +OK 6 280223
Message 1: 8594 bytes
Message 2: 65825 bytes
Message 3: 8331 bytes
Message 4: 65825 bytes
Message 5: 65825 bytes
Message 6: 65823 bytes

Enter command (type "help" for available commands) = quit
Server: +OK core mail
True

```

## 5. Problems Encountered and Solutions
### 5.1 Problems
None.

### 5.2 Solutions
None.
