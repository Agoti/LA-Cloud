
import threading
import time
from Scheduler.SlaveStates import SlaveStates, PiState
from Scheduler.Scheduler import Scheduler
from IO.IOStream import IOStream, Knock
from Constants import *

class MSThread(threading.Thread):

    def __init__(self, scheduler: Scheduler, io_stream: IOStream):
        threading.Thread.__init__(self)

        self.scheduler = scheduler
        self.io_stream = io_stream
        self.pi_name = None
        self.running = True
        self.debug = True
    
    def debug_print(self, message: str):
        if self.debug:
            print(message)
    
    def run(self):
        try:
            self.io_stream.send("Request")
            self.debug_print(f"MSThread {self.getName()}: Request sent")
            data = self.io_stream.receive()
            self.process_recv(data)
            self.debug_print(f"MSThread: data: {data}")
            while self.running:
                message = self.scheduler.get_message_slave(self.pi_name)
                data_send = self.process_send(message)
                self.debug_print(f"MSThread: send: {data_send}")
                self.io_stream.send(data_send)
                response = self.io_stream.receive()
                message = self.process_recv(response)
                self.scheduler.put_message_slave(self.pi_name, message)
                self.debug_print(f"MSThread: response: {response}")

        except Exception as e:
            print(f"MSThread: Error: {e}")
            # Print Backtrace
            import traceback
            traceback.print_exc()
        
        self.io_stream.close()
    
    def process_recv(self, data: str) -> str:
        
        # PI_NAME:pi_name CAPACITY:capacity
        if data.startswith("PI_NAME:"):
            self.pi_name = data.split(" ")[0].split(":")[1]
            self.scheduler.add_pi(self.pi_name)
            self.scheduler.set_capacity(self.pi_name, int(data.split(" ")[1].split(":")[1]))
            threading.Thread(target = self.heartbeat, daemon = True).start()
            if self.debug:
                self.scheduler._print_state()
            return "200 OK"
        elif data == "ACK":
            return "200 OK"

        return "400 Bad Recv"
    
    def heartbeat(self):
        self.heartbeat_io = Knock(method = 'socket', host = SLAVE_IP_PORT[self.pi_name]['ip'], port = SLAVE_IP_PORT[self.pi_name]['heartbeat'], timeout = HEARTBEAT_INTERVAL).knock()
        while self.running:
            try:
                self.heartbeat_io.send("Heartbeat")
                print(f"Heartbeat to {self.pi_name}")
                response = self.heartbeat_io.receive().lower()
                print(f"Heartbeat to {self.pi_name}: {response}")
                if response.startswith("alive"):
                    capacity = int(response.split(" ")[2])
                    self.scheduler.set_capacity(self.pi_name, capacity)
                else:
                    self.scheduler.remove_pi(self.pi_name)
                    self.heartbeat_io.close()
                    self.running = False
                    break
                time.sleep(HEARTBEAT_INTERVAL)
            except Exception as e:
                print(f"Heartbeat: Error: {e}")
                # Print Backtrace
                import traceback
                traceback.print_exc()

    
    def process_send(self, message: str) -> str:
        # message:
        # allocate: pi_name, chunks
        # deallocate: pi_name, chunks

        if message.lower().startswith("allocate"):
            response = message + ".*."
        elif message.lower().startswith("deallocate"):
            response = message + ".*."
        else:
            response = "BAD MESSAGE"
        
        return response
