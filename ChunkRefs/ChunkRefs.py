from DirectoryTree.ChunkHandle import ChunkHandle
import json
import threading

class ChunkRefs:

    def __init__(self):

        self.lock = threading.Lock()
        self.chunk_refs = {}
    
    def add_chunk(self, chunk_handle: ChunkHandle):
        with self.lock:
            self.chunk_refs[chunk_handle.name] = {
                "chunk_handle": chunk_handle,
                "filled": False
            }
    
    def remove_chunk(self, chunk_handle: ChunkHandle):
        with self.lock:
            del self.chunk_refs[chunk_handle.name]
    
    def set_filled(self, chunk_handle: ChunkHandle):
        with self.lock:
            self.chunk_refs[chunk_handle.name]["filled"] = True
    
    def get_filled(self, chunk_name: str):
        with self.lock:
            if chunk_name in self.chunk_refs:
                return self.chunk_refs[chunk_name]["filled"]
            else:
                return False
    
    def to_dict(self):
        with self.lock:
            chunk_refs_dict = {}
            for chunk_name, chunk_ref in self.chunk_refs.items():
                chunk_refs_dict[chunk_name] = {
                    "chunk_handle": chunk_ref["chunk_handle"].to_string(),
                    "filled": chunk_ref["filled"]
                }
        return chunk_refs_dict
    
    @staticmethod
    def from_dict(chunk_refs_dict):
        chunk_refs = ChunkRefs()
        for chunk_name, chunk_ref in chunk_refs_dict.items():
            chunk_refs.chunk_refs[chunk_name] = {
                "chunk_handle": ChunkHandle.from_string(chunk_ref["chunk_handle"]),
                "filled": chunk_ref["filled"]
            }
        return chunk_refs
    
    def save(self, filename):
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f)
    
    @staticmethod
    def load(filename):
        with open(filename, "r") as f:
            chunk_refs_dict = json.load(f)
        return ChunkRefs.from_dict(chunk_refs_dict)
        