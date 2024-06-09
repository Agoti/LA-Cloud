
import threading
from DirectoryTree.ChunkHandle import ChunkHandle
from DirectoryTree.ChunkTable import ChunkTable
from DirectoryTree.Permission import Permission
from User.User import User

class Node:
    
    def __init__(self, 
                 name: str,
                 owner: User = None, 
                 parent: 'DirectoryNode' = None):

        self.name = name
        self.owner = owner
        self.permission = Permission()
        self.parent = parent
        self.lock = threading.Lock()
    
    def __str__(self):
        return self.name
    
    def permission_string(self) -> str:
        raise NotImplementedError("CB: subclass must implement __str__ method")
    
    def set_owner(self, owner: User):
        with self.lock:
            self.owner = owner
    
    def set_permission(self, permission_string: str):
        with self.lock:
            self.permission.set_permission(permission_string)
    
    def verify_permission(self, user: User, operation = None):
        return self.permission.verify_permission(owner = self.owner, user = user, operation = operation)
    
    def get_size(self):
        raise NotImplementedError("CB: subclass must implement get_size method")
    
    def to_dict(self):
        raise NotImplementedError("CB: subclass must implement to_string method")

    @staticmethod
    def from_dict(dict):
        raise NotImplementedError("CB: subclass must implement from_string method")


class FileNode(Node):

    def __init__(self, name, owner = None, chunk_size = 1024):
        super().__init__(name, owner)
        self.chunk_table = ChunkTable()
        self.chunk_size = chunk_size
        self.size = 0
        self.occupied = 0

    def permission_string(self):
        return "-" + str(self.permission)
    
    # def add_chunk(self, chunk):
    #     assert isinstance(chunk, ChunkHandle), "chunk must be of type ChunkHandle"
    #     assert chunk.size <= self.chunk_size, "chunk size must be less than or equal to chunk_size"
    #     self.chunks.append(chunk)
    #     self.size += chunk.size
    #     self.occupied += self.chunk_size

    def set_chunks(self, chunks: ChunkTable | dict):
        with self.lock:
            if isinstance(chunks, dict):
                self.chunk_table = ChunkTable.from_dict(chunks)
            else:
                self.chunk_table = chunks
            self.size = self.chunk_table.get_size()
            self.occupied = self.chunk_table.get_occupied()
    
    def get_size(self):
        return self.size
    
    def get_chunks(self):
        return self.chunk_table
    
    def to_dict(self):
        return {
            "name": self.name,
            "owner": self.owner.to_dict() if self.owner is not None else None,
            "permission": "-" + str(self.permission),
            "chunks": self.chunk_table.to_dict(),
            "chunk_size": self.chunk_size,
            "size": self.size,
            "occupied": self.occupied
        }
    
    @staticmethod
    def from_dict(dict):
        name = dict["name"]
        owner = User.from_dict(dict["owner"])
        file_node = FileNode(name, owner, dict["chunk_size"])
        file_node.set_permission(dict["permission"])
        file_node.set_chunks(dict["chunks"])
        file_node.size = dict["size"]
        file_node.occupied = dict["occupied"]
        return file_node

class DirectoryNode(Node):

    def __init__(self, name, owner = None):
        super().__init__(name, owner)
        self.children = []
    
    def permission_string(self):
        return "d" + str(self.permission)
    
    def list_children(self) -> list[str]:
        return [child.name for child in self.children]
    
    def list_children_details(self) -> list[dict]:
        return [child.to_dict() for child in self.children]
    
    def add_child(self, child):
        assert isinstance(child, Node), "child must be of type CB"
        with self.lock:
            self.children.append(child)
            child.parent = self
    
    def get_child(self, name) -> Node:
        for child in self.children:
            if child.name == name:
                return child
        return None
    
    def remove_child(self, child):
        with self.lock:
            self.children.remove(child)
    
    def get_size(self):
        size = 0
        for child in self.children:
            size += child.get_size()
        return size
    
    def to_dict(self):
        return {
            "name": self.name,
            "owner": self.owner.to_dict() if self.owner is not None else None,
            "permission": "d" + str(self.permission),
            "children": [child.to_dict() for child in self.children]
        }
    
    @staticmethod
    def from_dict(dict):
        name = dict["name"]
        owner = User.from_dict(dict["owner"])
        directory_node = DirectoryNode(name, owner)
        directory_node.set_permission(dict["permission"])
        for child in dict["children"]:
            child_cls = FileNode if "chunks" in child else DirectoryNode
            directory_node.add_child(child_cls.from_dict(child))
        return directory_node

                
if __name__ == "__main__":
    
    pass

