
import threading
import struct
import os
from IO.IOStream import Knock, Answer, IOStream
from ChunkRefs.ChunkRefs import ChunkRefs
from DirectoryTree.ChunkHandle import ChunkHandle
from RawClient import RawClient
from Constants import *

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
        self.invalid_count = 0

        print(f"SCThread: {self.name} started")
    
    def run(self):
        while True:
            try:
                if self.state == "stor":
                    header = self.io_stream.receive(is_byte = True)
                    file_size = struct.unpack("!I", header)[0]
                    print(f"SCThread: File size: {file_size}")
                    data = b""
                    while len(data) < file_size:
                        data += self.io_stream.receive(is_byte = True)
                    print(f"SCThread: Received: {data[:10]}...")
                else:
                    data = self.io_stream.receive()
                    print(f"SCThread: Received: {data}")

                response = self.process(data)

                if response:
                    if isinstance(response, bytes):
                        print(f"SCThread: Sending: {response[:10]}...")
                    else:
                        print(f"SCThread: Sending: {response}")
                    self.io_stream.send(response, is_byte = isinstance(response, bytes))
                else:
                    self.io_stream.send("500 Empty response")
                if response == "221 Goodbye":
                    break

                if response == "501 Invalid Command":
                    if self.invalid_count >= 3:
                        self.io_stream.send("221 Goodbye")
                        break
                    else:
                        self.invalid_count += 1
                else:
                    self.invalid_count = 0

            except Exception as e:
                print(f"SCThread: Error: {e}")
                self.io_stream.send("500 Internal Error")

                import traceback
                traceback.print_exc()
                break
        
        self.io_stream.close()

    def process(self, data):

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
        
        self.chunk_handle = ChunkHandle.from_string(chunk_handle.strip())

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

        # if a chunk has backups, spawn a thread as a FakeClient to stor backups
        for backup in self.chunk_refs.get_backups(self.chunk_handle):
            fake_client_thread = threading.Thread(target=self.fake_client, args=(self.chunk_handle, backup))
            fake_client_thread.start()
            fake_client_thread.join()
        
        return response

    def fake_client(self, chunk_handle: ChunkHandle, backup: ChunkHandle):
        location = backup.location
        rc = RawClient(SLAVE_IP_PORT[location]["ip"], SLAVE_IP_PORT[location]["port"])
        rc.send("hello")
        if rc.recv() == "200 Hello":
            rc.send(f"stor {backup.to_string()}")
            if rc.recv() == "300 Waiting for data":
                rc.send(struct.pack("!I", len(self.bytes_received)), is_byte=True)
                rc.send(self.bytes_received, is_byte=True)
                if rc.recv().startswith("2"):
                    rc.send("quit")
                    if rc.recv() == "221 Goodbye":
                        print(f"SCThread: Backup {backup} stored")
                        rc.close()
                        return

        print(f"SCThread: Backup {backup} failed")
        rc.close()
    
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
        
        code = b"200 "
        header = struct.pack("!4sI", code, len(data))
        self.io_stream.send(header, is_byte = True)
        print(f"SCThread: Sending: {header}")

        return data



