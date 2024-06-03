
import threading
from Scheduler.SlaveStates import SlaveStates, PiState
from Scheduler.Scheduler import Scheduler
from IO.IOStream import IOStream

class MSThread(threading.Thread):

    def __init__(self, scheduler: Scheduler, io_stream: IOStream):
        threading.Thread.__init__(self)
        self.scheduler = scheduler
        self.io_stream = io_stream

        self.pi_name = None
    
    def run(self):
        try:
            self.io_stream.send("Request")
            data = self.io_stream.receive()
            self.process_recv(data)
            while True:
                message = self.scheduler.get_message(self.pi_name)
                data_send = self.process_send(message)
                self.io_stream.send(data_send)
                response = self.io_stream.receive()
                message = self.process_recv(response)
                self.scheduler.put_message(self.pi_name, message)

        except Exception as e:
            print(f"MSThread: Error: {e}")
            self.io_stream.send("500 Internal server error")
    
    def process_recv(self, data: str) -> str:
        
        # PI_NAME:pi_name, CAPACITY:capacity
        if data.startswith("PI_NAME:"):
            self.pi_name = data.split(":")[1]
            self.scheduler.set_capacity(self.pi_name, int(data.split(":")[3]))
            return "200 OK"
        elif data == "ACK":
            return "200 OK"

        return "400 Bad Recv"
    
    def process_send(self, message: str) -> str:
        # message:
        # allocate: pi_name, chunks
        # deallocate: pi_name, chunks

        if message.startswith("allocate"):
            response = f"ALLOCATE: {self.pi_name},{message.split(':')[1]}"
        elif message.startswith("deallocate"):
            response = f"DEALLOCATE: {self.pi_name},{message.split(':')[1]}"
        else:
            response = "BAD MESSAGE"
        
        response = f"{response}"
