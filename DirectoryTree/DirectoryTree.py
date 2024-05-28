from DirectoryTree.Node import Node, FileNode, DirectoryNode
from DirectoryTree.ChunkHandle import ChunkHandle
from DirectoryTree.Permission import Permission

class DiretoryTree:

    def __init__(self):
        self.root = DirectoryNode("/")
    
    def add_file(self, path, owner, permission_string, chunk_size, chunks):
        pass
