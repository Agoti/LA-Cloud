
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
                client_thread = MSThread(iostream, self.directory_tree, self.users)
                self.clients.append(client_thread)
                client_thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"MasterServer: Error: {e}")
                break
    
    def stop(self):
        self.answer.close()
        self.directory_tree.save_tree("Data/tree.json")
        User.save_users(self.users, "Data/users.json")
    
if __name__ == "__main__":
    master_server = MasterServer()
    try:
        master_server.start()
    except KeyboardInterrupt:
        master_server.stop()
