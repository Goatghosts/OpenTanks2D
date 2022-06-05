import time
import socket
from threading import Thread, Lock
from sockets import UdpSocket, TcpSocket

from utils import Client, MessageType


class Server:

    def __init__(self) -> None:
        self.lock = Lock()
        self.udp = UdpSocket(lock=self.lock, callback=self.udp_callback)
        self.udp.daemon = True
        self.tcp = TcpSocket(lock=self.lock, callback=self.tcp_callback)
        self.tcp.daemon = True
        self.clients = {}


    def run(self) -> None:
        print("Start up UDP server!")
        self.udp.start()
        print("Start up TCP server!")
        self.tcp.start()


    def udp_callback(self, data, address):
        request = data.split(b' ')
        command = request[0]
        identifier = str(address[0]) + ':' + str(address[1])
        print(request, identifier)
        return b'ACK'


    def tcp_callback(self, data, connect, address):
        if data['type'] in [MessageType.REGISTER]:
            client = Client(address, data['payload']['username'], data['payload']['udp_port'])
            uuid = client.create_uuid()
            while uuid in self.clients:
                uuid = client.create_uuid()
            self.clients[uuid] = client
            print(f"Client with address [{client.ip}] and name [{client.username}] ({client.uuid}) registered successfully")
            client.send_tcp(uuid, connect=connect)
        return None


    def shutdown(self):
        print("Shutting down UDP server...")
        self.udp.is_listening = False
        self.udp.join()
        print("Shutting down TCP server...")
        self.tcp.is_listening = False
        self.tcp.join()


if __name__ == "__main__":
    server = Server()
    server.run()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    server.shutdown()