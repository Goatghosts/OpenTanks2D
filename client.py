import json
import threading
import socket

from utils import MessageType


class Client:

    def __init__(self, username, client_port_udp):
        self.uuid = None
        self.username = username
        self.server_message = []
        self.client_udp = ("0.0.0.0", client_port_udp)
        self.lock = threading.Lock()
        self.server_listener = SocketThread(self.client_udp, self, self.lock)
        self.server_listener.start()
        self.server_udp = ("127.0.0.1", 9998)
        self.server_tcp = ("127.0.0.1", 9999)
        self.register()


    def leave(self):
        request = json.dumps({
            "type": int(MessageType.LEAVE),
            "uuid": self.uuid,
        })
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(request.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        message = data


    def send(self, message):
        request = json.dumps({
            "type": int(MessageType.SEND),
            "uuid": self.uuid,
            "payload": {
                "message": message
            },
        })
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(request.encode(), self.server_udp)


    def register(self):
        request = json.dumps({
            "type": int(MessageType.REGISTER),
            'payload': {
                "username": self.username,
                "udp_port": self.client_udp[1]
            }
        })
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(request.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        self.uuid = data.decode('utf-8')


    def get_messages(self):
        message = self.server_message
        self.server_message = []
        return set(message)


class SocketThread(threading.Thread):
    def __init__(self, addr, client, lock):
        threading.Thread.__init__(self)
        self.client = client
        self.lock = lock
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(addr)

    def run(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            self.lock.acquire()
            try:
                print(data)
                self.client.server_message.append(data)
            except Exception as ex:
                pass
            self.lock.release()

    def stop(self):
        self.sock.close()


if __name__ == "__main__":
    client1 = Client("Petr", 1235)
    client2 = Client("Sup", 1236)
    client3 = Client("Jhon", 1237)

    print("Client 1 : %s" % client1.uuid)
    print("Client 2 : %s" % client2.uuid)
    print("Client 3 : %s" % client3.uuid)

    client1.send('Client 1 test')
    client3.send('Client 3 test')