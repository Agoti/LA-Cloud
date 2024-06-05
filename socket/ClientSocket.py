import socket
import struct
import os

class TCPClient:
    # 初始化客户端TCP连接
    def __init__(self, host='101.200.241.54', port=54325):  # 101.200.241.54
        self.host = host
        self.port = port
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))

    # 与服务端建立连接并收发数据
    def send_recieve_data(self, data_type, file_path):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            print(f"Attempting to connect to {self.host}:{self.port}")
            client_socket.connect((self.host, self.port))
            # 发送数据
            self.send_data(client_socket, data_type, file_path)
            # 接受服务器端返回的数据
            data_type, data = self.recive_data(client_socket)
            return data_type, data
    # 将文件转换为字节流并发送给服务端
    def send_data(self,client_socket, data_type, file_path):
        data_type_encoded = data_type.encode('ascii')
        data_type_length = len(data_type_encoded)
        file_size = os.path.getsize(file_path)
        header = struct.pack('!II', data_type_length, file_size)
        client_socket.sendall(header)
        client_socket.sendall(data_type_encoded)
        with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(1024)
                if not chunk:
                    break
                client_socket.sendall(chunk)

    # 接受服务端返回的字节流
    def recive_data(self, client_socket):
        header = client_socket.recv(8)
        data_type_length, data_size = struct.unpack('!II', header)
        data_type = client_socket.recv(data_type_length).decode('ascii')
        data = b''
        while True:
            packet = client_socket.recv(data_size)
            data += packet
            if len(data) == data_size:
                break
        return data_type, data

    # 将接受的字节流保存为文件
    def save_response(self, response, file_path):
        with open(file_path, 'wb') as file:
            file.write(response)
        print(f"Received response and saved as {file_path}")

if __name__ == "__main__":
    client = TCPClient()
    while True:
        input_type =  input("Enter 'text' or 'image' or 'audio' or 'music' or 'video': ") 
        if input_type == 'text':
            data_type = 'text'
            file_path = 'FTP.txt'
        elif input_type == 'image':
            data_type = 'image'
            file_path = 'image.png'
        elif input_type == 'audio':
            data_type = 'audio'
            file_path = 'output_0.wav'
        elif input_type == 'music':
            data_type = 'music'
            file_path = 'music.mp3'
        elif input_type == 'video':
            data_type = 'video'
            file_path = 'movie_003.mp4'
        else:
            print("Unsupported data type")
            continue
        data_type, data = client.send_recieve_data(data_type, file_path)
        backed = {'text':'.txt', 'image':'.png', 'audio':'.wav', 'music':'.mp3', 'video':'.mp4'}
        client.save_response(data, f'response_{data_type}{backed[data_type]}')
