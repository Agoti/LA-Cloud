# 这个文件是用来构建一个云盘客户端的界面，用tkinter实现
# 作者：阿拉帕提
# 创建时间：2024.6.4

import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import os
import time
import threading
import socket
import json
from tkinter import ttk

# 定义一个界面类
class Cloud_GUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('云盘客户端')
        self.window.geometry('800x600')
        self.window.resizable(0, 0)
        self.server_ip = '101.200.241.54'
        self.server_port = 8888

    # 创建登录界面
    def create_login(self):
        # 创建登录界面
        self.login_frame = tk.Frame(self.window, width=800, height=600)
        self.login_frame.pack()
        # 创建登录界面的控件
        tk.Label(self.login_frame, text='用户名：').place(x=200, y=200)
        tk.Label(self.login_frame, text='密码：').place(x=200, y=250)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.place(x=300, y=200)
        self.password_entry = tk.Entry(self.login_frame, show='*')
        self.password_entry.place(x=300, y=250)
        login_button = tk.Button(self.login_frame, text='登录', command=self.login)
        login_button.place(x=300, y=300)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        """
        # 创建一个socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 连接服务器
        self.client_socket.connect((self.server_ip, self.server_port))
        # 发送登录请求
        login_info = {
            'type': 'login',
            'username': username,
            'password': password
        }
        self.client_socket.send(json.dumps(login_info).encode())
        # 接收服务器返回的登录结果
        result = self.client_socket.recv(1024).decode()
        """
        result = 'success'
        if result == 'success':
            # 登录成功，创建主界面
            self.create_main()
            # 关闭登录界面
            self.login_frame.destroy()
        else:
            messagebox.showinfo('登录失败', '用户名或密码错误！')

        
    # 创建主界面
    def create_main(self):
        # 创建主界面
        self.main_frame = tk.Frame(self.window, width=800, height=600)
        self.main_frame.pack()
        # 创建主界面的控件
        self.file_listbox = tk.Listbox(self.main_frame, width=100, height=30)
        self.file_listbox.place(x=50, y=50)
        self.refresh_button = tk.Button(self.main_frame, text='刷新', command=self.refresh)
        self.refresh_button.place(x=50, y=500)
        self.upload_button = tk.Button(self.main_frame, text='上传', command=self.upload)
        self.upload_button.place(x=150, y=500)
        self.download_button = tk.Button(self.main_frame, text='下载', command=self.download)
        self.download_button.place(x=250, y=500)
        self.delete_button = tk.Button(self.main_frame, text='删除', command=self.delete)
        self.delete_button.place(x=350, y=500)
        self.create_folder_button = tk.Button(self.main_frame, text='新建文件夹', command=self.create_folder)
        self.create_folder_button.place(x=450, y=500)
        self.file_listbox.bind('<Double-Button-1>', self.open_folder)
        # 刷新文件列表
        self.refresh()  
    
    def refresh(self):
        pass

    def upload(self):
        pass

    def download(self):
        pass

    def delete(self):
        pass
    
    def create_folder(self):
        pass

    def open_folder(self):
        pass

    

if __name__ == '__main__':
    cloud_gui = Cloud_GUI()
    cloud_gui.create_login()
    cloud_gui.window.mainloop()