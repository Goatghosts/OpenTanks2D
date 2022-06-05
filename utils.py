import enum
import uuid
import socket

class MessageType(enum.IntEnum):
    REGISTER = 1
    MOVE = 2
    SHOOT = 3
    SEND = 4
    LEAVE = 5


class Client:

    def __init__(self, address, username, udp_port):
        self.uuid = None
        self.username = username
        self.ip = str(address[0]) + ':' + str(address[1])
        self.address = address
        self.udp_address = (address[0], int(udp_port))
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def create_uuid(self):
        self.uuid = str(uuid.uuid4())[:8]
        return self.uuid

    def send_tcp(self, data: str, connect):
        connect.send(data.encode())

    def send_udp(self, data: str):
        self.udp_sock.sendto(data.encode(), self.udp_address)