import socket
from IO.IOStream import *

class RawClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.io_stream = Knock(method='socket', host=host, port=port).knock()

    def send(self, data):
        self.io_stream.send(data)

    def recv(self):
        return self.io_stream.receive()

    def close(self):
        self.io_stream.close()

if __name__ == "__main__":
    client = RawClient("localhost", 9999)
    while True:
        data = input()
        client.send(data)
        response = client.recv()
        print(response)
        if data == "quit":
            break
    client.close()

    client2 = RawClient("localhost", 9997)
    while True:
        data = input()
        client2.send(data)
        response = client2.recv()
        print(response)
        if data == "quit":
            break
    client2.close()