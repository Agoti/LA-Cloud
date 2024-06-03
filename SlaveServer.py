import threading
from IO.IOStream import Knock, Answer, IOStream
from Protocol.MSThread import MSThread

class Slave:

    def __init__(self, ip = "localhost", port = 9998):
        
        self.master_knock = Knock(method = 'socket', host = ip, port = 9999)
        self.master_io = self.master_knock.knock()
        self.msg_thread = threading.Thread(target = self.slave_start, daemon = True)
        self.ping_thread = threading.Thread(target = self.slave_ping_start, daemon = True)

        self.client_answer = Answer(method = 'socket', host = ip, port = 9997)
        self.clients = []

        self.capicity = 0
        self.virtual_disk_space = 1000

    
    def start(self):
        self.msg_thread.start()
        self.ping_thread.start()


    def slave_start(self):
        while True:
            try:
                data = self.master_io.receive()
                if data.startswith("allocate"):
                    self.allocate(data)
                    response = "ACK"
                elif data.startswith("deallocate"):
                    self.deallocate(data)
                    response = "ACK"
                else:
                    self.master_io.send("400 Bad Request")
            except Exception as e:
                print(f"Slave: Error: {e}")
                break
    
    def slave_ping_start(self):
        while True:
            try:
                data = self.master_io.receive()
                if data.startswith("PING"):
                    self.capicity = self.get_disk_space()
                    self.master_io.send(f"PONG: {self.capicity}")
            except Exception as e:
                print(f"Slave: Error: {e}")
                break
        
    def allocate(self, data: str):
        chunks = int(data.split(':')[1])
        self.virtual_disk_space -= chunks
        self.master_io.send("ACK")
    
    def deallocate(self, data: str):
        chunks = int(data.split(':')[1])
        self.virtual_disk_space += chunks
        self.master_io.send("ACK")
    
    def get_disk_space(self):
        return self.virtual_disk_space
