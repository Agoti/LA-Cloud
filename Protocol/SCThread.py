
import threading
import os
from IO.IOStream import Knock, Answer, IOStream
from ChunkRefs.ChunkRefs import ChunkRefs
from DirectoryTree.ChunkHandle import ChunkHandle

class SCThread(threading.Thread):

    def __init__(self, 
                 io_stream: IOStream,
                 chunk_path: str,
                 chunk_refs: ChunkRefs):
        threading.Thread.__init__(self)
        self.io_stream = io_stream
        self.chunk_path = chunk_path
        self.chunk_refs = chunk_refs
        self.state = "init"

        self.chunk_handle = None
        self.bytes_received = b""

        print(f"SCThread: {self.name} started")
    
    def run(self):
        while True:
            try:
                data = self.io_stream.receive()
                print(f"SCThread: Received: {data}")
                response = self.process(data)
                if response:
                    self.io_stream.send(response)
                if response == "221 Goodbye":
                    self.io_stream.close()
                    break

            except Exception as e:
                print(f"SCThread: Error: {e}")
                self.io_stream.send("500 Internal Error")

                import traceback
                traceback.print_exc()
                break

    def process(self, data):

        if data.startswith("quit"):
            response = "221 Goodbye"
        if self.state == "stor":
            response = self.ftp_bytes(data)

        else:
            if data.startswith("hello"):
                response = self.ftp_hello()
            elif data.startswith("stor"):
                ch = data[5:]
                if not ChunkHandle.validate_string(ch):
                    return "503 Invalid Chunk Handle Syntax"
                response = self.ftp_store(ch)
            elif data.startswith("retr"):
                ch = data[5:]
                if not ChunkHandle.validate_string(ch):
                    return "503 Invalid Chunk Handle Syntax"
                response = self.ftp_retrieve(ch)
            else:
                response = "501 Invalid Command"
        
        return response

    def ftp_hello(self):
        response = "200 Hello"
        self.state = "hello"
        return response
    
    def ftp_store(self, chunk_handle: str):
        if self.state != "hello":
            return "503 Bad Sequence"
        
        self.chunk_handle = ChunkHandle.from_string(chunk_handle)

        if self.chunk_handle.name in self.chunk_refs.chunk_refs:
            if self.chunk_handle == self.chunk_refs.chunk_refs[self.chunk_handle.name]["chunk_handle"]:
                self.state = "stor"
                self.bytes_received = b""
                response = "300 Waiting for data"
            else:
                response = "503 Chunk Handle Mismatch"
        else:
            response = "503 Chunk Handle Not Allocated"

        return response
    
    def ftp_bytes(self, data: str):
        self.bytes_received += data.encode("utf-8")

        if len(self.bytes_received) >= self.chunk_handle.size:
            with open(os.path.join(self.chunk_path, self.chunk_handle.name), "wb") as f:
                self.bytes_received = self.bytes_received[:self.chunk_handle.size]
                f.write(self.bytes_received)
            
            self.state = "hello"
            self.chunk_refs.set_filled(self.chunk_handle)
            response = "200 Stored" if len(self.bytes_received) == self.chunk_handle.size else "201 Truncated"
        
        else:
            response = None
        
        return response
    
    def ftp_retrieve(self, chunk_handle: str):

        if self.state != "hello":
            return "503 Bad Sequence"

        chunk_handle = ChunkHandle.from_string(chunk_handle)
        if chunk_handle.name not in self.chunk_refs.chunk_refs:
            return "503 Chunk Handle Not Allocated"
        elif chunk_handle != self.chunk_refs.chunk_refs[chunk_handle.name]["chunk_handle"]:
            return "503 Chunk Handle Mismatch"
        
        with open(os.path.join(self.chunk_path, chunk_handle.name), "rb") as f:
            data = f.read()
        
        response = f"200 {len(data)}\n {data}"
        return response


