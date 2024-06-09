import socket
from IO.IOStream import *
from Constants import *

class RawClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.knock = Knock(method='socket', host=host, port=port)
        self.io_stream = self.knock.knock()

    def send(self, data, is_byte = False):
        print(f"Sending: {data[:100]}")
        self.io_stream.send(data, is_byte = is_byte)

    def recv(self, is_byte = False):
        data = self.io_stream.receive(is_byte=is_byte)
        print(f"Received: {data[:100]}")
        return data

    def close(self):
        self.io_stream.close()

if __name__ == "__main__":
    client = RawClient(MASTER_IP, MASTER_CLIENT_PORT)
    while True:
        data = input()
        client.send(data)
        response = client.recv()
        print(response)
        if data == "quit":
            break
    client.close()

    client2 = RawClient(SLAVE_IP_PORT["pi1"]["ip"], SLAVE_IP_PORT["pi1"]["port"])
    while True:
        data = input()
        client2.send(data)
        response = client2.recv()
        print(response)
        if data == "quit":
            break
    client2.close()