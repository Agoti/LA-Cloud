
import threading
from User.User import User
from DirectoryTree.DirectoryTree import DirectoryTree
from DirectoryTree.Node import FileNode, DirectoryNode
from User.Cipher import MD5Cipher
from IO.IOStream import IOStream

class MSThread(threading.Thread):
        
    def __init__(self,
                io_stream: IOStream,
                directory_tree: DirectoryTree,
                users: list):
        threading.Thread.__init__(self)
        self.io_stream = io_stream

        self.directory_tree = directory_tree
        self.users = users

        self.state = "init"

        self.user_name = None
        self.user = None
        self.node = None
    
    def run(self):
        while True:
            try:
                data = self.io_stream.receive()
                print(f"MSThread: Received data: {data}")
                response = self.process_data(data)
                self.io_stream.send(response)
                print(f"MSThread: Sent data: {response}")
                if response == "221 Goodbye":
                    break
            except Exception as e:
                print(f"MSThread: Error: {e}")
                self.io_stream.send("500 Internal server error")
                break

        self.stop()
    
    def stop(self):
        self.io_stream.close()
    
    def process_data(self, data: str):

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
            if len(args) < 2:
                response = self.ftp_list()
            else:
                response = self.ftp_list(args[1])
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
    
    def ftp_list(self, path = None):
        if self.state != "password":
            return "530 Not logged in"
        print(f"ftp_list: path: {path}")
        node = self.node if path is None else self.directory_tree.get_node(path)
        if node is None:
            return "550 Failed to list directory"
        if not isinstance(node, DirectoryNode):
            return "550 Not a directory"
        print(f"ftp_list: node: {node}")
        # check permission
        if not node.verify_permission(self.user, "read"):
            return "550 Permission denied"
        children = node.list_children()
        return "200 " + "\n".join(children)
    
