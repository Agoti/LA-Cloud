
import socket

class Knock:

    def __init__(self,
                 method = 'socket',
                 **kwargs):
        
        self.method = method

        if method == 'socket':
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((kwargs['host'], kwargs['port']))
        elif method == 'zeromq':
            pass
        elif method == 'nanomq':
            pass
    
    def accept(self):
        if self.method == 'socket':
            self.socket.listen(5)
            client, address = self.socket.accept()
            return client, address

class IOStream:
    
    def __init__(self, 
                 method = 'socket', 
                 **kwargs):
        
        self.input_stream = InputStream(method, **kwargs)
        self.output_stream = OutputStream(method, **kwargs)
    
    def send(self, data):
        self.output_stream.send(data)
    
    def receive(self):
        return self.input_stream.receive()

class OutputStream:
    
    def __init__(self,
                method = 'socket',
                **kwargs):
            
        self.method = method
        if self.method == 'socket':
            self.socket = kwargs['socket']
        elif self.method == 'zeromq':
            pass
        elif self.method == 'nanomq':
            pass
    
    def send(self, data):
        if self.method == 'socket':
            self.socket.send(bytes(data, "utf-8"))
        elif self.method == 'zeromq':
            raise NotImplementedError()
        elif self.method == 'nanomq':
            print(data)


class InputStream:

    def __init__(self, 
                 method = 'socket', 
                 **kwargs):
        
        self.method = method
        if self.method == 'socket':
            self.socket = kwargs['socket']
        elif self.method == 'zeromq':
            pass
        elif self.method == 'nanomq':
            pass
    
    def receive(self):
        if self.method == 'socket':
            data = self.socket.recv(1024).decode("utf-8")
        elif self.method == 'zeromq':
            raise NotImplementedError()
        elif self.method == 'nanomq':
            data = input()
        
        return data

