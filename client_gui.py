# 这个文件是用来构建一个云盘客户端的界面，用tkinter实现
# 作者：阿拉帕提
# 创建时间：2024.6.4

import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk
from IO.IOStream import *
from Constants import *

# 定义一个界面类
class Cloud_GUI:
    def __init__(self, host: str, port: int):
        self.window = tk.Tk()
        self.window.title('云盘客户端')
        self.window.geometry('800x600')
        self.window.resizable(0, 0)

        self.host = host
        self.port = port
        self.io_stream = Knock(method='socket', host=host, port=port).knock()
    
    def send(self, data):
        self.io_stream.send(data)
    
    def recv(self):
        return self.io_stream.receive()

    def close(self):
        self.io_stream.close()



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
        self.send('user' + ' ' + username)
        usr_response = self.recv()
        self.send('pass' + ' ' + password)
        pwd_response = self.recv()
        if usr_response.startswith('331') and pwd_response.startswith('230'):
            # 登录成功，创建主界面
            self.create_main()
            # 关闭登录界面
            self.login_frame.destroy()
        else:
            messagebox.showinfo("Error", usr_response+'\n'+pwd_response)

        
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
        self.send('ls')
        ls_response = self.recv().split('\n')
        print(ls_response)
        if ls_response[0].startswith('200'):
            ls_response[0] = '..'
            file_list = ls_response
            # 将文件列表显示在界面上
            self.file_listbox.delete(0, tk.END)
            for file in file_list:
                self.file_listbox.insert(tk.END, file)
                print(file)
        else :
            messagebox.showinfo("Error", ls_response)
        
        pass

    def upload(self):
        pass

    def download(self):
        pass

    def delete(self):
        pass
    
    def create_folder(self):
        # 弹出一个对话框，获取新建文件夹的名字
        folder_name = simpledialog.askstring('新建文件夹', '请输入文件夹名字')
        self.send('mkdir' + ' ' + folder_name)
        mkdir_response = self.recv()
        if mkdir_response.startswith('257'):
            # 将新添加的目录显示在界面上
            self.refresh()
        else:
            messagebox.showinfo("Error", mkdir_response)
        pass

    def open_folder(self, event):
        # 获取当前选中的文件名
        selected_file = self.file_listbox.get(self.file_listbox.curselection())
        self.send('cd' + ' ' + selected_file)
        cd_response = self.recv()
        if cd_response.startswith('250'):
            # 进入文件夹成功，刷新文件列表
            self.refresh()
        else:
            messagebox.showinfo("Error", cd_response)
        pass

    

if __name__ == '__main__':
    cloud_gui = Cloud_GUI(MASTER_IP, MASTER_CLIENT_PORT)
    cloud_gui.create_login()
    cloud_gui.window.mainloop()