
from DirectoryTree.ChunkHandle import ChunkHandle

class ChunkTable:

    def __init__(self):
        self.chunks = {}
    
    def __contains__(self, backup):
        return backup in self.chunks
    
    # iterate over all backups
    def __iter__(self):
        for backup in self.chunks:
            yield self.chunks[backup]
    
    def __getitem__(self, backup):
        return self.chunks[backup]
    
    def get_items(self):
        for backup in self.chunks:
            yield backup, self.chunks[backup]
    
    def get_size(self):
        if len(self.chunks) == 0:
            return 0
        # Assume all backups have the same number of chunks
        first_backup = list(self.chunks.keys())[0]
        return sum([chunk.size for chunk in self.chunks[first_backup]])
    
    def get_occupied(self):
        if len(self.chunks) == 0:
            return 0
        # Assume all backups have the same number of chunks, and all chunks have the same size
        return len(self.chunks) * len(self.chunks[list(self.chunks.keys())[0]]) * self.chunks[list(self.chunks.keys())[0]][0].size
    
    def __str__(self) -> str:

        builder = ""
        for backup in self.chunks:
            builder += f"Backup {backup}:\n"
            for chunk in self.chunks[backup]:
                builder += f"{chunk}\n"
            
        return builder

    def to_dict(self, dtype = str):
        chunks_dict = {}
        for backup in self.chunks:
            if dtype == ChunkHandle:
                chunks_dict[backup] = self.chunks[backup]
            else:
                chunks_dict[backup] = [chunk.to_string() for chunk in self.chunks[backup]]
        return chunks_dict
    
    @staticmethod
    def from_dict(dict):
        chunk_table = ChunkTable()
        for backup in dict:
            chunk_table.chunks[backup] = [ChunkHandle.from_string(chunk) if isinstance(chunk, str) else chunk for chunk in dict[backup]]
        return chunk_table
