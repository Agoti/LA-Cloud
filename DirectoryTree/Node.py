from DirectoryTree.ChunkHandle import ChunkHandle
from DirectoryTree.Permission import Permission

class Node:
    
    def __init__(self, name, owner = None):

        self.name = name
        self.owner = owner
        self.permission = Permission()
    
    def permission_string(self):
        raise NotImplementedError("CB: subclass must implement __str__ method")
    
    def set_permission(self, permission_string):
        self.permission.set_permission(permission_string[1:])
    
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
        self.chunks = []
        self.chunk_size = chunk_size
        self.size = 0
        self.occupied = 0

    def permission_string(self):
        return "-" + str(self.permission)
    
    def add_chunk(self, chunk):
        assert isinstance(chunk, ChunkHandle), "chunk must be of type ChunkHandle"
        assert chunk.size <= self.chunk_size, "chunk size must be less than or equal to chunk_size"
        self.chunks.append(chunk)
        self.size += chunk.size
        self.occupied += self.chunk_size
    
    def get_size(self):
        return self.size
    
    def to_dict(self):
        return {
            "name": self.name,
            "owner": self.owner,
            "permission": str(self.permission),
            "chunks": [chunk.to_string() for chunk in self.chunks],
            "chunk_size": self.chunk_size,
            "size": self.size,
            "occupied": self.occupied
        }
    
    @staticmethod
    def from_dict(dict):
        file_node = FileNode(dict["name"], dict["owner"], dict["chunk_size"])
        file_node.set_permission(dict["permission"])
        for chunk in dict["chunks"]:
            file_node.add_chunk(ChunkHandle.from_string(chunk))
        file_node.size = dict["size"]
        file_node.occupied = dict["occupied"]
        return file_node

class DirectoryNode(Node):

    def __init__(self, name, owner = None):
        super().__init__(name, owner)
        self.children = []
    
    def permission_string(self):
        return "d" + str(self.permission)
    
    def add_child(self, child):
        assert isinstance(child, Node), "child must be of type CB"
        self.children.append(child)
    
    def remove_child(self, child):
        self.children.remove(child)
    
    def get_size(self):
        size = 0
        for child in self.children:
            size += child.get_size()
        return size
    
    def to_dict(self):
        return {
            "name": self.name,
            "owner": self.owner,
            "permission": str(self.permission),
            "children": [child.to_dict() for child in self.children]
        }
    
    @staticmethod
    def from_dict(dict):
        directory_node = DirectoryNode(dict["name"], dict["owner"])
        directory_node.set_permission(dict["permission"])
        for child in dict["children"]:
            directory_node.add_child(Node.from_dict(child))
        return directory_node

                
if __name__ == "__main__":
    
    pass

