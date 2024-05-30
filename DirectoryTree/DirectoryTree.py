import json
from User.User import User
from DirectoryTree.Node import DirectoryNode, FileNode
from DirectoryTree.Permission import Permission
from DirectoryTree.ChunkHandle import ChunkHandle

class DirectoryTree:

    def __init__(self):
        self.root = DirectoryNode("/")
        self.root.add_child(DirectoryNode("home"))
    
    def initialize_tree(self, users):
        self.root.set_owner(User.get_root(users))
        self.root.set_permission("drwxr-xr--")
        self.root.get_child("home").set_permission("drwxr-xr--")
        self.root.get_child("home").set_owner(User.get_root(users))
        for user in users:
            self.add_directory("/home/" + user.name, user, "drwxr-xr--")
    
    def _draw_tree(self, node, indent = 0):
        string = ""
        if indent > 0:
            string += " " * (indent - 4) + "L" + "---"
        print(string + str(node))
        for child in node.children:
            self._draw_tree(child, indent + 4)
    
    def print_tree(self):
        self._draw_tree(self.root)

    @staticmethod
    def parse_path(path):
        # path = "/a/b/c"
        # returns ["a", "b", "c"]
        return path.split("/")[1:]
    
    def get_path(self, node):
        # node = node at path "/a/b/c"
        # returns "/a/b/c"
        current = node
        path = ""
        while current is not self.root:
            path = "/" + current.name + path
            current = current.parent
        return path
    
    def get_node(self, path: str):
        # path = "/a/b/c"
        # returns node at path "/a/b/c"
        current = self.root
        if path == "/":
            return current
        for name in self.parse_path(path):
            current = current.get_child(name)
            if current is None:
                return None
        return current
    
    def get_home(self, user: User):
        # user = user node
        # returns home directory node of user
        return self.get_node("/home/" + user.name)
    
    def add_file(self, 
                 path: str, 
                 owner: str, 
                 permission: str,
                 chunks: list, 
                 chunk_size: int):
        # path = "/a/b/c"
        # chunks = [ChunkHandle("a", "a", "a", 1), ChunkHandle("b", "b", "b", 2)]
        # chunk_size = 3
        # adds file node at path "/a/b/c"
        current = self.root
        for name in self.parse_path(path):
            if current.get_child(name) is None:
                current.add_child(DirectoryNode(name, owner))
            current = current.get_child(name)
        file_node = FileNode(path.split("/")[-1], owner, chunk_size)
        file_node.set_permission(permission)
        for chunk in chunks:
            file_node.add_chunk(chunk)
        current.add_child(file_node)

        return file_node
    
    def add_directory(self, 
                      path: str, 
                      owner: str, 
                      permission: str):
        # path = "/a/b/c"
        # adds directory node at path "/a/b/c"
        current = self.root
        for name in self.parse_path(path):
            if current.get_child(name) is None:
                directory_node = DirectoryNode(name, owner)
                directory_node.set_permission(permission)
                current.add_child(directory_node)
            current = current.get_child(name)

        return current
    
    def remove(self, 
               path: str):
        # path = "/a/b/c"
        # removes node at path "/a/b/c"
        current = self.root
        for name in self.parse_path(path):
            if current.get_child(name) is None:
                return False
            current = current.get_child(name)

        current.parent.remove_child(current)
        return True
    
    def to_dict(self):
        return self.root.to_dict()
    
    @staticmethod
    def from_dict(dict):
        if "chunks" in dict:
            return FileNode.from_dict(dict)
        return DirectoryNode.from_dict(dict)
    
    @staticmethod
    def load_tree(path):
        with open(path, "r") as file:
            data = json.load(file)
        tree = DirectoryTree()
        tree.root = DirectoryTree.from_dict(data)
        return tree
    
    def save_tree(self, path):
        with open(path, "w") as file:
            json.dump(self.to_dict(), file, indent=4)

# if __name__ == "__main__":
#     tree = DiretoryTree()
#     User.load_users("Data/users.txt")
#     tree.initialize_tree()
#     tree.save_tree("Data/tree.json")
#     tree2 = DiretoryTree()
#     tree2.load_tree("Data/tree.json")
#     print(tree2.to_dict())
