class Client2Master:
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.c2m_log = open("cliet2master_log.txt", "a")
        self.c2m_log.write(f"User: {self.user}\n")

    # Function to print the record to the user_log.txt file
    def print_record(self, message: str, print2console: bool = True):
        self.c2m_log.write(message+"\n")
        if print2console:
            print(message)

    # Function to login to the server
    def login(self):
        # send the username
        self.print_record(f"USER {self.user}")
        received_331 = input().split()
        if received_331[0] != "331":
            self.print_record("Error: 331 not received", False)
            return False
        self.print_record(received_331, False)

        # send the password
        self.print_record(f"PASS {self.password}")
        received_230 = input().split()
        if received_230[0] != "230":
            self.print_record("Error: 230 not received", False)
            return False
        self.print_record(received_230, False)
        return True
    
    # Function to execute the orders
    def orders(self, order: str):
        order_ls = order.split()
        if len(order_ls) == 0:
            self.print_record("Invalid order", False)
            return False
        elif len(order_ls) == 1:
            order = order.lower()
        else:
            order = order_ls[0].lower() + " " + order_ls[1]
        # check the directory
        if order == "pwd":
            self.print_record("PWD")
            received_257 = input().split()
            if received_257[0] != "257":
                self.print_record("Error: 257 not received", False)
                return False
            self.print_record(received_257, False)
            pwd = received_257[1]
        
        # list the files
        elif order == "list":
            self.print_record("LIST")
            received_150 = input().split()
            if received_150[0] != "150":
                self.print_record("Error: 150 not received", False)
                return False
            self.print_record(received_150, False)
            # print the files
            while True:
                received = input()
                self.print_record(received, False)
                if received == ".*.":
                    break
            received_226 = input().split()
            if received_226[0] != "226":
                self.print_record("Error: 226 not received", False)
                return False
            self.print_record(received_226, False)

        # quit the server
        elif order == "quit":
            self.print_record("QUIT")
            received_221 = input().split()
            if received_221[0] != "221":
                self.print_record("Error: 221 not received", False)
                return False
            self.print_record(received_221, False)

        # retrieve the file
        elif order[:4] == "retr":
            self.print_record(f"RETR {order[5:]}")
            received_150 = input().split()
            if received_150[0] != "150":
                self.print_record("Error: 150 not received", False)
                return False
            self.print_record(received_150, False)
            chunk_block = []
            while True:
                received_chunk = input()
                if received_chunk == ".*.":
                    break
                chunk_block.append(received_chunk)



        else:
            self.print_record("Invalid order", False)
            return False



