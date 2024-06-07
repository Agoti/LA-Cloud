import threading
import socket
from IO.IOStream import Knock, Answer, IOStream
from Protocol.SCThread import SCThread
from DirectoryTree.ChunkHandle import ChunkHandle
from ChunkRefs.ChunkRefs import ChunkRefs
from Constants import *

class Slave:

    def __init__(self, 
                 slave_ip = "localhost", 
                 master_ip = "localhost",
                 master_port = 9998, 
                 client_port = 9997,
                 name = "pi1", 
                 path = ".",
                 disk_space = 1000):
        
        self.name = name
        print("ip: " + master_ip + ", port " + str(master_port))
        self.master_knock = Knock(method = 'socket', host = master_ip, port = master_port)
        self.master_io = self.master_knock.knock()
        self.msg_running = True
        self.ping_running = True
        self.msg_thread = threading.Thread(target = self.slave_start, daemon=True)
        # self.ping_thread = threading.Thread(target = self.slave_ping_start, daemon=True)
        self.client_thread = threading.Thread(target = self.handle_client, daemon=True)

        self.client_answer = Answer(method = 'socket', host = slave_ip, port = client_port)
        self.clients = []

        self.capicity = 0
        self.virtual_disk_space = disk_space

        self.chunk_refs = ChunkRefs()
        self.chunk_path = path

        print(f"Slave: {self.name} started")
    
    def start(self):
        self.chunk_refs = ChunkRefs.load(os.path.join(self.chunk_path, "chunk_refs.json"))
        self.msg_thread.start()
        # self.ping_thread.start()
        self.client_thread.start()

    def slave_start(self):
        while self.msg_running:
            try:
                data = self.master_io.receive().lower()
                print("Recv")
                if data.startswith("allocate"):
                    while self.msg_running:
                        if data.strip().endswith(".*."):
                            print("breaking")
                            break
                        data += self.master_io.receive().lower()
                        print("while loop")
                print(f"Slave: Received: {data}")
                if data.startswith("request"):
                    self.capicity = self.get_disk_space()
                    response = f"PI_NAME:{self.name} CAPACITY:{self.capicity}"
                elif data.startswith("allocate"):
                    print("allocating")
                    self.allocate(data)
                    response = "ACK"
                elif data.startswith("deallocate"):
                    self.deallocate(data)
                    response = "ACK"
                else:
                    response = "400 Bad Recv"
                print(f"Slave: Sending: {response}")
                self.master_io.send(response)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Slave-Master: Error: {e}")
                import traceback
                traceback.print_exc()
                break
    
    def slave_ping_start(self):
        while self.ping_running:
            try:
                data = self.master_io.receive()
                if data.startswith("PING"):
                    self.capicity = self.get_disk_space()
                    self.master_io.send(f"PONG: {self.capicity}")
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Slave: Error: {e}")
                break
    
    def handle_client(self):
        while True:
            try:
                io_stream = self.client_answer.accept()
                print(f"Slave: Client connected")
                thread = SCThread(io_stream, self.chunk_path, self.chunk_refs)
                thread.start()
                self.clients.append(thread)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Slave: Error: {e}")
                import traceback
                traceback.print_exc()
                break
        
    def allocate(self, data: str):
        chunks = data.split('\n')[1:-1]
        for chunk in chunks:
            chunk = ChunkHandle.from_string(chunk.strip())
            self.virtual_disk_space -= chunk.size
            self.chunk_refs.add_chunk(chunk)
            print(f"Slave: Allocated: {chunk}")
        # self.master_io.send("ACK")
    
    def deallocate(self, data: str):

        chunks = data.split('\n')[1:-1]
        for chunk in chunks:
            chunk = ChunkHandle.from_string(chunk.strip())

            # Remove chunk from disk
            if self.chunk_refs.get_filled(chunk.name):
                os.remove(os.path.join(self.chunk_path, chunk.name))

            self.chunk_refs.remove_chunk(chunk)
            self.virtual_disk_space += chunk.size
            print(f"Slave: Deallocated: {chunk}")
        # self.master_io.send("ACK")
    
    def get_disk_space(self):
        return self.virtual_disk_space
    
    def stop(self):

        self.chunk_refs.save(os.path.join(self.chunk_path, "chunk_refs.json"))
        print("Slave: Saving chunk_refs.json")
        self.msg_running = False
        self.ping_running = False
        print("Slave: Stopping...")
        self.master_io.close()
        self.client_answer.close()
        print("Slave: Stopped")


if __name__ == "__main__":
    import sys, os
    name = sys.argv[1]
    slave = Slave(name=name,
                  master_ip=MASTER_IP, 
                  slave_ip=SLAVE_IP_PORT[name]["ip"],
                  master_port=MASTER_SLAVE_PORT, 
                  client_port=SLAVE_IP_PORT[name]["port"],
                  path=DISK[name]["path"],
                  disk_space=DISK[name]["capacity"])
    import time
    try:
        slave.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Slave: Stopping...")
        slave.stop()

