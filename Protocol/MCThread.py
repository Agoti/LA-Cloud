
import threading
from User.User import User
from DirectoryTree.DirectoryTree import DirectoryTree
from DirectoryTree.Node import FileNode, DirectoryNode
from DirectoryTree.ChunkHandle import ChunkHandle
from User.Cipher import MD5Cipher
from IO.IOStream import IOStream

class MCThread(threading.Thread):
        
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
        elif data.startswith("ls"):
            if len(args) < 2:
                response = self.ftp_list()
            else:
                response = self.ftp_list(args[1])
        elif data.startswith("cd"):
            if len(args) < 2:
                return "501 Syntax error in parameters or arguments"
            response = self.ftp_cd(args[1])
        elif data.startswith("mkdir"):
            if len(args) < 2:
                return "501 Syntax error in parameters or arguments"
            response = self.ftp_mkdir(args[1])
        elif data.startswith("retr"):
            if len(args) < 2:
                return "501 Syntax error in parameters or arguments"
            response = self.ftp_retr(args[1])
        elif data.startswith("stor"):
            if len(args) < 3:
                return "501 Syntax error in parameters or arguments"
            response = self.ftp_stor(args[1], int(args[2]))
        elif data.startswith("del"):
            if len(args) < 2:
                return "501 Syntax error in parameters or arguments"
            response = self.ftp_delete(args[1])
        elif data.startswith("rmdir"):
            if len(args) < 2:
                return "501 Syntax error in parameters or arguments"
            response = self.ftp_rmdir(args[1])
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
        return "200 \n" + "\n".join(children)
    
    def ftp_cd(self, path):
        if self.state != "password":
            return "530 Not logged in"
        node = self.directory_tree.get_node(path, node = self.node)
        if node is None:
            return "550 Failed to change directory"
        if not isinstance(node, DirectoryNode):
            return "550 Not a directory"
        if not node.verify_permission(self.user, "execute"):
            return "550 Permission denied"
        self.node = node
        return "250 Directory changed to " + self.directory_tree.get_path(self.node)
    
    def ftp_mkdir(self, path):
        if self.state != "password":
            return "530 Not logged in"
        node = self.directory_tree.get_node(path, node = self.node)
        if node is not None:
            return "550 Directory already exists"
        parent = self.directory_tree.get_node(path, node = self.node, get_parent = True)
        if not parent.verify_permission(self.user, "write"):
            return "550 Permission denied"
        absolute_path = self.directory_tree.get_path(parent) + "/" + path.split("/")[-1]
        print(f"ftp_mkdir: absolute_path: {absolute_path}")
        self.directory_tree.add_directory(absolute_path, self.user, "drwxr-xr--")
        return "257 Directory created"
    
    def ftp_retr(self, path):
        if self.state != "password":
            return "530 Not logged in"
        node = self.directory_tree.get_node(path, node = self.node)
        if node is None:
            return "550 File not found"
        if not isinstance(node, FileNode):
            return "550 Not a file"
        if not node.verify_permission(self.user, "read"):
            return "550 Permission denied"
        return "200 \n" + "\n".join([chunk.to_string() for chunk in node.chunks])
    
    def ftp_stor(self, path, size):
        if self.state != "password":
            return "530 Not logged in"
        node = self.directory_tree.get_node(path, node = self.node)
        if node is not None:
            return "550 File already exists"
        parent = self.directory_tree.get_node(path, node = self.node, get_parent = True)
        if not parent.verify_permission(self.user, "write"):
            return "550 Permission denied"
        chunks = self._allocate_chunks(size)
        absolute_path = self.directory_tree.get_path(parent) + "/" + path.split("/")[-1]
        print(f"ftp_stor: absolute_path: {absolute_path}")
        self.directory_tree.add_file(absolute_path, self.user, "-rwxr-xr--", chunks, 10)
        return "200 \n" + "\n".join([chunk.to_string() for chunk in chunks])
    
    def _allocate_chunks(self, size):
        n_chunks = size // 10
        chunks = []
        for i in range(n_chunks):
            chunk = ChunkHandle("pi1", "chunk" + str(i), "fingerprint", 10)
            chunks.append(chunk)
        if size % 10 != 0:
            chunk = ChunkHandle("pi1", "chunk" + str(n_chunks), "fingerprint", size % 10)
            chunks.append(chunk)
        return chunks
    
    def _deallocate_chunks(self, node):
        if isinstance(node, FileNode):
            for chunk in node.chunks:
                print(f"Deallocating chunk: {str(chunk)}")
        elif isinstance(node, DirectoryNode):
            for child in node.children:
                self._deallocate_chunks(child)
        

    def ftp_delete(self, path):
        if self.state != "password":
            return "530 Not logged in"
        node = self.directory_tree.get_node(path, node = self.node)
        if node is None:
            return "550 File not found"
        if not isinstance(node, FileNode):
            return "550 Not a file"
        if not node.verify_permission(self.user, "write"):
            return "550 Permission denied"
        self._deallocate_chunks(node)
        absolute_path = self.directory_tree.get_path(node)
        self.directory_tree.remove(absolute_path)
        return "200 File deleted"

    
    def ftp_rmdir(self, path):
        if self.state != "password":
            return "530 Not logged in"
        node = self.directory_tree.get_node(path, node = self.node)
        if node is None:
            return "550 Directory not found"
        if not isinstance(node, DirectoryNode):
            return "550 Not a directory"
        if not node.verify_permission(self.user, "write"):
            return "550 Permission denied"
        self._deallocate_chunks(node)
        absolute_path = self.directory_tree.get_path(node)
        self.directory_tree.remove(absolute_path)
        return "200 Directory deleted"
    
