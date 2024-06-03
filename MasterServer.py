
import socket
import threading
import time
from DirectoryTree.DirectoryTree import DirectoryTree
from User.User import User
from Protocol.MCThread import MCThread
from Protocol.MSThread import MSThread
from IO.IOStream import Answer, IOStream
from Scheduler.Scheduler import Scheduler
from Constants import *

class MasterServer:

    def __init__(self, ip = "localhost", port = 9999):

        self.client_answer = Answer(method = 'socket', host = ip, port = port)
        self.clients = []

        self.slave_answer = Answer(method = 'socket', host = ip, port = 9998)
        self.slaves = []

        self.directory_tree = DirectoryTree.load_tree("Data/tree.json")
        self.users = User.load_users("Data/users.json")
        self.scheduler = Scheduler(chunk_size = CHUNK_SIZE, n_backups = N_BACKUPS)
    
    def master_client_start(self):
        while True:
            try:
                iostream = self.client_answer.accept()
                client_thread = MCThread(iostream, self.directory_tree, self.users, self.scheduler)
                self.clients.append(client_thread)
                client_thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"MasterServer: Error: {e}")
                break
    
    def master_slave_start(self):
        while True:
            try:
                iostream = self.slave_answer.accept()
                slave_thread = MSThread(self.scheduler, iostream)
                self.slaves.append(slave_thread)
                slave_thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"MasterServer: Error: {e}")
                break
    
    def stop(self):
        self.client_answer.close()
        self.directory_tree.save_tree("Data/tree.json")
        User.save_users(self.users, "Data/users.json")
    
if __name__ == "__main__":
    master_server = MasterServer()
    try:
        threading.Thread(target = master_server.master_client_start, daemon = True).start()
        threading.Thread(target = master_server.master_slave_start, daemon = True).start()
        while True:
            time.sleep(1)
            pass
    except KeyboardInterrupt:
        master_server.stop()
