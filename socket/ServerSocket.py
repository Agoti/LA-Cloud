import socket
import struct
import threading

class TCPServer:
    # 初始化TCP连接的IP地址和端口号
    def __init__(self, host='127.0.0.1', port=54321):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 启动TCP服务
    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Server listening on {self.host}:{self.port}")
        # 循环监听客户端连接
        while True:
            conn, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()
    # 处理客户端请求
    def handle_client(self, conn, addr):
        print(f"Connected by {addr}")
        with conn:
            try:
                # 接收客户端请求
                data_type, data = self.recieve_data(conn)
                print(f'have recieved data {data_type} {len(data)}...')
                print(f"begin to return response...")
                # 处理请求并返回响应
                res_data_type, res_data = self.handle_data(data_type, data)
                # 发送响应
                self.send_data(conn, res_data_type, res_data)
            except Exception as e:
                print(f"Error: {e}")
                exit(1)
    # 接收客户端发送的字节流
    def recieve_data(self, conn):
        header = conn.recv(8)
        data_type_length, file_size = struct.unpack('!II', header)
        data_type = conn.recv(data_type_length).decode('ascii')
        data = b''
        while True:
            packet = conn.recv(1024)
            data += packet
            # print(file_size, data_type, packet)
            if len(data) == file_size:
                break
        return data_type, data
    # 发送字节流给客户端
    def send_data(self, conn, res_data_type, res_data):
        data_type_encoded = res_data_type.encode('ascii')
        data_type_length = len(data_type_encoded)
        file_size = len(res_data)
        header = struct.pack('!II', data_type_length, file_size)
        conn.sendall(header)
        conn.sendall(data_type_encoded)
        sent_size = 0
        while sent_size < file_size:
            chunk = res_data[sent_size:sent_size+1024]
            sent_size += len(chunk)
            conn.sendall(chunk)


    # 对用户发过来的数据进行处理
    # NOTE : 这里只是一个简单的例子，模型的处理逻辑应该在这里
    def handle_data(self, data_type, data):
        if data_type == 'text':
            return data_type, data.upper()
        elif data_type in ['image', 'audio', 'video']:
            return data_type, data
        else:
            return data_type, b'Unsupported data type'

if __name__ == "__main__":
    server = TCPServer()
    server.start()
