import socket
import json
from threading import Thread, Lock

class UdpSocket(Thread):

    def __init__(self, lock: Lock, callback: object):
        Thread.__init__(self)
        self.lock = lock
        self.callback = callback
        self.is_listening = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("0.0.0.0", 9998))
        self.socket.setblocking(0)
        self.socket.settimeout(5)


    def run(self):
        while self.is_listening:
            try:
                data, address = self.socket.recvfrom(1024)
            except socket.timeout:
                continue
            self.lock.acquire()
            try:
                self.callback(data, address)
            except Exception:
                pass
            self.lock.release()
        self.stop()


    def stop(self):
        self.socket.close()


class TcpSocket(Thread):

    def __init__(self, lock: Lock, callback: object):
        Thread.__init__(self)
        self.lock = lock
        self.callback = callback
        self.is_listening = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('0.0.0.0', 9999))
        self.socket.setblocking(0)
        self.socket.settimeout(5)
        self.socket.listen(1)


    def run(self):
        while self.is_listening:
            try:
                connect, address = self.socket.accept()
            except socket.timeout:
                continue
            try:
                data = connect.recv(1024)
                data = json.loads(data)
            except Exception as ex:
                continue
            self.lock.acquire()
            try:
                self.callback(data, connect, address)
            except Exception:
                pass
            self.lock.release()
            connect.close()
        self.stop()


    def stop(self):
        self.socket.close()