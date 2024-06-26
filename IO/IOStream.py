
import socket

# FIXME: A nicer implementation compared to 'if-elif-else' would be polymorphism. But that's too much for this project.
# NOTE: packet IO only supports 'socket' method.

class Knock:
    
    def __init__(self,
                 method = 'socket',
                 **kwargs):
        
        self.method = method
        if method == 'socket':
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((kwargs['host'], kwargs['port']))
            print(f"Knock: Connected to {kwargs['host']}:{kwargs['port']}")
            self.timeout = kwargs.get('timeout', None)
        elif method == 'zeromq':
            pass
        elif method == 'nanomq':
            pass
    
    def knock(self):
        if self.method == 'socket':
            return IOStream(method = 'socket', socket = self.socket, timeout = self.timeout)
        elif self.method == 'zeromq':
            raise NotImplementedError()
        elif self.method == 'nanomq':
            raise NotImplementedError()
    
    def close(self):
        if self.method == 'socket':
            pass
        elif self.method == 'zeromq':
            pass
        elif self.method == 'nanomq':
            pass
        

class Answer:

    def __init__(self,
                 method = 'socket',
                 **kwargs):
        
        self.method = method

        if method == 'socket':
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((kwargs['host'], kwargs['port']))
            self.socket.settimeout(1)
            self.socket.listen(5)
            self.timeout = kwargs.get('timeout', None)
            print(f"Answer: Listening on {kwargs['host']}:{kwargs['port']}")
        elif method == 'zeromq':
            pass
        elif method == 'nanomq':
            pass
    
    def accept(self): # throws socket.timeout
        if self.method == 'socket':
            client, address = self.socket.accept()
            print(f"Answer: Connection from {address} has been established!")
            return IOStream(method = 'socket', socket = client, timeout = self.timeout)
    
    def close(self):
        if self.method == 'socket':
            self.socket.close()
        elif self.method == 'zeromq':
            pass
        elif self.method == 'nanomq':
            pass

class IOStream:
    
    def __init__(self, 
                 method = 'stdio', 
                 **kwargs):
        
        self.input_stream = InputStream(method, **kwargs)
        self.output_stream = OutputStream(method, **kwargs)
    
    def send(self, data, is_byte = False):
        self.output_stream.send(data, is_byte)
    
    def receive(self, is_byte = False):
        return self.input_stream.receive(is_byte)
    
    def close(self):
        self.input_stream.close()
        self.output_stream.close()

class OutputStream:
    
    def __init__(self,
                method = 'socket',
                **kwargs):
            
        # FIXME: A nicer implementation would be polymorphism
        self.method = method
        if self.method == 'stdio':
            pass
        elif self.method == 'socket':
            self.socket = kwargs['socket']
        elif self.method == 'zeromq':
            pass
        elif self.method == 'nanomq':
            pass
    
    def send(self, data, is_byte = False):
        if self.method == 'stdio':
            print(data)
        elif self.method == 'socket':
            if is_byte:
                self.socket.send(data)
            else:
                self.socket.send(data.encode("utf-8"))
        elif self.method == 'zeromq':
            raise NotImplementedError()
        elif self.method == 'nanomq':
            print(data)
    
    def close(self):

        if self.method == 'stdio':
            pass
        elif self.method == 'socket':
            self.socket.close()
        elif self.method == 'zeromq':
            raise NotImplementedError()
        elif self.method == 'nanomq':
            pass


class InputStream:

    def __init__(self, 
                 method = 'stdio', 
                 **kwargs):
        
        self.method = method
        if self.method == 'stdio':
            pass
        elif self.method == 'socket':
            self.socket = kwargs['socket']
            self.timeout = kwargs.get('timeout', None)
        elif self.method == 'zeromq':
            pass
        elif self.method == 'nanomq':
            pass
    
    def receive(self, is_byte = False):
        if self.method == 'stdio':
            data = input()
        elif self.method == 'socket':
            if self.timeout:
                self.socket.settimeout(self.timeout)
            if is_byte:
                data = self.socket.recv(1024)
            else:
                data = self.socket.recv(1024).decode("utf-8")
        elif self.method == 'zeromq':
            raise NotImplementedError()
        elif self.method == 'nanomq':
            data = input()
        
        return data
    
    def close(self):
        if self.method == 'stdio':
            pass
        elif self.method == 'socket':
            self.socket.close()
        elif self.method == 'zeromq':
            raise NotImplementedError()
        elif self.method == 'nanomq':
            pass

