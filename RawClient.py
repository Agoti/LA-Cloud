import socket

class RawClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def send(self, data):
        self.sock.sendall(data)

    def recv(self, size):
        return self.sock.recv(size)

    def close(self):
        self.sock.close()

if __name__ == "__main__":
    client = RawClient("localhost", 9999)
    while True:
        data = input()
        client.send(data.encode())
        response = client.recv(1024)
        print(response.decode())
        if data == "quit":
            break
    client.close()