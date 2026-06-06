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
