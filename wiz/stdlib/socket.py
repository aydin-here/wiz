import socket


class SocketModule:

    def __init__(self):
        self.functions = {
            "tcp": self.tcp,
            "bind": self.bind,
            "listen": self.listen,
            "accept": self.accept,
            "connect": self.connect,
            "send": self.send,
            "recv": self.recv,
            "close": self.close,
        }

    def tcp(self):
        return socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

    def bind(self, sock, host, port):
        sock.bind((host, port))
        return True

    def listen(self, sock, backlog=5):
        sock.listen(backlog)
        return True

    def accept(self, sock):
        client, address = sock.accept()

        return {
            "socket": client,
            "address": address
        }

    def connect(self, sock, host, port):
        sock.connect((host, port))
        return True

    def send(self, sock, data):
        sock.send(str(data).encode())
        return True

    def recv(self, sock, size=1024):
        return sock.recv(size).decode()

    def close(self, sock):
        sock.close()
        return True