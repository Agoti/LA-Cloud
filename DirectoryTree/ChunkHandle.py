
class ChunkHandle:

    def __init__(self, location, name, fingerprint, size):
        self.location = location
        self.name = name
        self.fingerprint = fingerprint
        self.size = size
    
    def to_string(self):
        return '(' + self.location + ', ' + self.name + ', ' + self.fingerprint + ', ' + str(self.size) + ')'
    
    @staticmethod
    def from_string(string):
        string = string[1:-1]
        parts = string.split(', ')
        return ChunkHandle(parts[0], parts[1], parts[2], int(parts[3]))
