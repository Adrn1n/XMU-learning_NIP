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
