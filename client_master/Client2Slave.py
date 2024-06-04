
class Client2Slave:
    # TODO  connect to the slave raspberry pi
    def __init__(self, slave):
        self.slave = slave
        self.c2s_log = open("client2slave_log.txt", "a")
        self.c2s_log.write(f"slave: {self.slave}\n")
        pass
    # Function to print the record to the user_log.txt file
    def print_record(self, message: str, print2console: bool = True):
        self.c2s_log.write(message+"\n")
        if print2console:
            print(message)
    
    def retrieve(self, recieved_chunk: list):
        self.print_record("HELO")
        received_250 = input().split()
        if received_250[0] != "250":
            self.print_record("Error: 250 not received", False)
            return False
        self.print_record(received_250, False)

        for chunk in recieved_chunk:
            self.print_record(chunk)
            file_block = input()
            received_226 = input().split()
            if received_226[0] != "226":
                self.print_record("Error: 226 not received", False)
                return False
            self.print_record(received_226, False)


    
