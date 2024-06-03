import threading
import socket
from IO.IOStream import Knock, Answer, IOStream
from Protocol.MSThread import MSThread
from DirectoryTree.ChunkHandle import ChunkHandle

class Slave:

    def __init__(self, ip = "localhost", port = 9998, name = "pi1"):
        
        self.name = name
        self.master_knock = Knock(method = 'socket', host = ip, port = port)
        self.master_io = self.master_knock.knock()
        self.msg_running = True
        self.ping_running = True
        self.msg_thread = threading.Thread(target = self.slave_start, daemon=True)
        self.ping_thread = threading.Thread(target = self.slave_ping_start, daemon=True)

        # self.client_answer = Answer(method = 'socket', host = ip, port = 9997)
        # self.clients = []

        self.capicity = 0
        self.virtual_disk_space = 1000

        print(f"Slave: {self.name} started")
    
    def start(self):
        self.msg_thread.start()
        # self.ping_thread.start()

    def slave_start(self):
        while self.msg_running:
            try:
                data = self.master_io.receive().lower()
                print(f"Slave: Received: {data}")
                if data.startswith("request"):
                    self.capicity = self.get_disk_space()
                    response = f"PI_NAME:{self.name} CAPACITY:{self.capicity}"
                elif data.startswith("allocate"):
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
    
    def handle_client(self, client):
        while True:
            try:
                data = client.receive().lower()
                print(f"Slave: Received: {data}")
                if data.startswith("allocate"):
                    self.allocate(data)
                    response = "ACK"
                elif data.startswith("deallocate"):
                    self.deallocate(data)
                    response = "ACK"
                else:
                    response = "400 Bad Recv"
                print(f"Slave: Sending: {response}")
                client.send(response)
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
            chunk = ChunkHandle.from_string(chunk)
            self.virtual_disk_space -= chunk.size
            print(f"Slave: Allocated: {chunk}")
        self.master_io.send("ACK")
    
    def deallocate(self, data: str):
        chunks = data.split('\n')[1:-1]
        for chunk in chunks:
            chunk = ChunkHandle.from_string(chunk)
            self.virtual_disk_space += chunk.size
            print(f"Slave: Deallocated: {chunk}")
        self.master_io.send("ACK")
    
    def get_disk_space(self):
        return self.virtual_disk_space
    
    def stop(self):
        self.msg_running = False
        self.ping_running = False
        self.master_io.close()

if __name__ == "__main__":
    import sys
    slave = Slave(name=sys.argv[1])
    import time
    try:
        slave.start()
        while True:
            time.sleep(1)
            pass
    except KeyboardInterrupt:
        slave.stop()

