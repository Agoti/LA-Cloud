
import socket
import threading
from DirectoryTree.DirectoryTree import DirectoryTree
from User.User import User
from Protocol.MSThread import MSThread

class MasterServer:

    def __init__(self, ip = "localhost", port = 9999):

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.server.settimeout(5)
        print(f"MasterServer: Server started at {ip}:{port}")

        self.clients = []

        self.directory_tree = DirectoryTree.load_tree("Data/tree.json")
        self.users = User.load_users("Data/users.txt")
    
    def start(self):
        self.server.listen(5)
        while True:
            try:
                client, address = self.server.accept()
            except socket.timeout:
                continue
            print(f"MasterServer: Connection from {address} has been established!")
            client_thread = MSThread(client, address, self.directory_tree, self.users)
            self.clients.append(client_thread)
            client_thread.start()
    
    def stop(self):
        self.server.close()
    
if __name__ == "__main__":
    master_server = MasterServer()
    master_server.start()
    master_server.stop()
