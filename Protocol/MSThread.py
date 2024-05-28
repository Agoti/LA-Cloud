
import threading
import socket
from User.User import User
from DirectoryTree.DirectoryTree import DirectoryTree
from User.Cipher import MD5Cipher

class MSThread(threading.Thread):
        
    def __init__(self,
                client: socket.socket, 
                address: str,
                directory_tree: DirectoryTree,
                users: list):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address

        self.directory_tree = directory_tree
        self.users = users

        self.state = "init"

        self.user_name = None
        self.user = None
        self.node = None
    
    def run(self):
        print(f"MSThread: Connection from {self.address} has been established!")
        while True:
            try:
                data = self.client.recv(1024)
                print(f"MSThread: Received data: {data}")
                response = self.process_data(data)
                self.client.send(bytes(response, "utf-8"))
                print(f"MSThread: Sent data: {response}")
                if response == "221 Goodbye":
                    break
            except Exception as e:
                print(f"MSThread: Error: {e}")
                break
        print(f"MSThread: Connection from {self.address} has been closed!")
    
    def stop(self):
        self.client.close()
    
    def process_data(self, data: bytes):

        data = data.decode("utf-8").strip().lower()
        args = data.split(" ")

        if data.startswith("user"):
            if len(args) < 2:
                return "501 Syntax error in parameters or arguments"
            response = self.ftp_user(args[1])
        elif data.startswith("pass"):
            if len(args) < 2:
                return "501 Syntax error in parameters or arguments"
            response = self.ftp_password(MD5Cipher.encrypt(args[1]))
        elif data.startswith("quit"):
            response = self.ftp_quit()
        elif data.startswith("pwd"):
            response = self.ftp_pwd()
        elif data.startswith("list"):
            response = self.ftp_list()
        elif data.startswith("cd"):
            if len(args) < 2:
                return "501 Syntax error in parameters or arguments"
            response = self.ftp_cd(args[1])
        else:
            response = "500 Syntax error, command unrecognized"
        
        return response
            
    def ftp_user(self, user_name):
        if not User.exists(self.users, user_name):
            return "430 User not found"
        self.state = "user"
        self.user_name = user_name
        return "331 Password required for " + user_name
    
    def ftp_password(self, password):
        if self.state != "user":
            return "503 Bad sequence of commands"
        error, user = User.verify_user(self.users, self.user_name, password)
        if error is None:
            self.user = user
            self.state = "password"
            self.node = self.directory_tree.get_home(self.user)
            return "230 User logged in"
        return "530 Login incorrect"
    
    def ftp_quit(self):
        return "221 Goodbye"
    
    def ftp_pwd(self):
        if self.state != "password":
            return "530 Not logged in"
        return "257 " + self.directory_tree.get_path(self.node)

