
import socket
import threading
from DirectoryTree.DirectoryTree import DirectoryTree
from User.User import User
from Protocol.MSThread import MSThread
from IO.IOStream import Answer, IOStream

class MasterServer:

    def __init__(self, ip = "localhost", port = 9999):

        self.answer = Answer(method = 'socket', host = ip, port = port)

        self.clients = []

        self.directory_tree = DirectoryTree.load_tree("Data/tree.json")
        self.users = User.load_users("Data/users.json")
    
    def start(self):
        while True:
            try:
                iostream = self.answer.accept()
            except socket.timeout:
                continue
            client_thread = MSThread(iostream, self.directory_tree, self.users)
            self.clients.append(client_thread)
            client_thread.start()
    
    def stop(self):
        self.answer.close()
    
if __name__ == "__main__":
    master_server = MasterServer()
    master_server.start()
    master_server.stop()
