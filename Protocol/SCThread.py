
import threading
import struct
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
                if self.state == "stor":
                    header = self.io_stream.receive(is_byte = True)
                else:
                    data = self.io_stream.receive()

                print(f"SCThread: Received: {data}")
                response = self.process(data)

                if response:
                    print(f"SCThread: Sending: {response}")
                    self.io_stream.send(response, is_byte = isinstance(response, bytes))
                else:
                    self.io_stream.send("500 Empty response")
                if response == "221 Goodbye":
                    break

            except Exception as e:
                print(f"SCThread: Error: {e}")
                self.io_stream.send("500 Internal Error")

                import traceback
                traceback.print_exc()
                break
        
        self.io_stream.close()

    def process(self, data: str | bytes) -> str | bytes:

        if isinstance(data, str) and data.startswith("quit"):
            response = "221 Goodbye"

        elif self.state == "stor":
            if isinstance(data, str):
                data = data.encode("utf-8")
            response = self.ftp_bytes(data)

        else:
            if isinstance(data, bytes):
                data = data.decode("utf-8")
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
    
    def ftp_bytes(self, data: bytes):

        self.bytes_received = data

        response = "200 Stored" if len(self.bytes_received) <= self.chunk_handle.size else "201 Truncated"
        with open(os.path.join(self.chunk_path, self.chunk_handle.name), "wb") as f:
            self.bytes_received = self.bytes_received[:self.chunk_handle.size]
            f.write(self.bytes_received)
        
        self.state = "hello"
        self.chunk_refs.set_filled(self.chunk_handle)
        
        return response
    
    def ftp_retrieve(self, chunk_handle: str) -> bytes:

        if self.state != "hello":
            return b"503 Bad Sequence"

        chunk_handle = ChunkHandle.from_string(chunk_handle)
        if chunk_handle.name not in self.chunk_refs.chunk_refs:
            print('scthread:', chunk_handle.name, self.chunk_refs.chunk_refs)
            return b"503 Chunk Handle Not Allocated"
        elif chunk_handle != self.chunk_refs.chunk_refs[chunk_handle.name]["chunk_handle"]:
            return b"503 Chunk Handle Mismatch"
        elif not self.chunk_refs.get_filled(chunk_handle.name):
            return b"204 Empty Chunk"
        
        with open(os.path.join(self.chunk_path, chunk_handle.name), "rb") as f:
            data = f.read()
        
        code = "200"
        file_size = len(data)
        header = struct.pack("!II", code, file_size)
        self.io_stream



