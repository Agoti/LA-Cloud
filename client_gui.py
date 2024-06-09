import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
import os
from PIL import Image, ImageTk  # 导入PIL
from IO.IOStream import *
from Constants import *
import struct
import time
import threading

class RawClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.knock = Knock(method='socket', host=host, port=port)
        self.io_stream = self.knock.knock()

    def send(self, data, is_byte = False):
        print(f"Sending: {data[:100]}")
        self.io_stream.send(data, is_byte = is_byte)

    def recv(self, is_byte = False):
        data = self.io_stream.receive(is_byte=is_byte)
        print(f"Received: {data[:100]}")
        return data

    def close(self):
        self.io_stream.close()


class Cloud_GUI(RawClient):
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('云盘客户端')
        self.window.geometry('800x600')
        self.window.resizable(0, 0)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        try:
            self.client2m = RawClient(MASTER_IP, MASTER_CLIENT_PORT)
        except Exception as e:
            messagebox.showinfo("Error", 'could not connect to master server')
            exit(1)

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.is_login_frame = False
        self.is_main_frame = False

        self.selected_file = None
        # 加载并缩放文件夹图标
        self.folder_icon_image = Image.open("Icons/folder_icon.png")
        self.folder_icon_image = self.folder_icon_image.resize((25, 25), Image.Resampling.LANCZOS)
        self.folder_icon = ImageTk.PhotoImage(self.folder_icon_image)
        self.file_icon_image = Image.open("Icons/file_icon.png")
        self.file_icon_image = self.file_icon_image.resize((25, 25), Image.Resampling.LANCZOS)
        self.file_icon = ImageTk.PhotoImage(self.file_icon_image)

    def create_login(self):
        self.is_login_frame = True
        self.login_frame = ttk.Frame(self.window, width=800, height=600)
        self.login_frame.pack()

        ttk.Label(self.login_frame, text='用户名：').place(x=200, y=200)
        ttk.Label(self.login_frame, text='密码：').place(x=200, y=250)

        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.place(x=300, y=200)
        self.password_entry = ttk.Entry(self.login_frame, show='*')
        self.password_entry.place(x=300, y=250)

        login_button = ttk.Button(self.login_frame, text='登录', command=self.login)
        login_button.place(x=300, y=300)

    def login(self):
        if self.is_login_frame:
            username = self.username_entry.get()
            password = self.password_entry.get()
        self.client2m.send('user' + ' ' + username)
        usr_response = self.client2m.recv()
        self.client2m.send('pass' + ' ' + password)
        pwd_response = self.client2m.recv()
        if usr_response.startswith('331') and pwd_response.startswith('230'):
            if not self.is_main_frame:
                self.create_main()
            if self.is_login_frame:
                self.login_frame.destroy()
                self.is_login_frame = False
        else:
            messagebox.showinfo("Error", usr_response + '\n' + pwd_response)

    def on_closing(self):
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            try:
                self.client2m.knock.socket.settimeout(2)
                self.client2m.send('quit')
                quit_response = self.client2m.recv()
                if not quit_response.startswith('221'):
                    messagebox.showinfo("Error", 'the Master server is not responding')  
            except Exception as e:
                print(e)
            finally:
                self.client2m.close()
                self.window.destroy()

    def create_main(self):
        self.is_main_frame = True
        self.main_frame = ttk.Frame(self.window, width=800, height=600)
        self.main_frame.pack()

        self.canvas = tk.Canvas(self.main_frame, width=800, height=450, bg='white')
        self.canvas.place(x=0, y=100)

        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.place(x=780, y=100, height=450)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')

        self.refresh_button = ttk.Button(self.main_frame, text='刷新', command=self.refresh)
        self.refresh_button.place(x=50, y=50)
        self.upload_button = ttk.Button(self.main_frame, text='上传', command=self.upload)
        self.upload_button.place(x=150, y=50)
        self.download_button = ttk.Button(self.main_frame, text='下载', command=self.download)
        self.download_button.place(x=250, y=50)
        self.delete_button = ttk.Button(self.main_frame, text='删除', command=self.delete)
        self.delete_button.place(x=350, y=50)
        self.create_folder_button = ttk.Button(self.main_frame, text='新建文件夹', command=self.create_folder)
        self.create_folder_button.place(x=450, y=50)

        self.inner_frame.bind("<Configure>", self.on_frame_configure)

        self.refresh()

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def refresh_file_ls(self, file_list):
        for widget in self.inner_frame.winfo_children():
                widget.destroy()
        for file in file_list:
            if file == '':
                continue

            if file == self.selected_file:
                frame = ttk.Frame(self.inner_frame, borderwidth=5, relief="solid")
            else:
                frame = ttk.Frame(self.inner_frame, borderwidth=1, relief="solid")
            frame.pack(fill="x", expand=True, padx=10, pady=5)
            
            if ".." in file:
                icon_label = tk.Label(frame)
            elif "." in file:
                icon_label = tk.Label(frame, image=self.file_icon)
            else:
                icon_label = tk.Label(frame, image=self.folder_icon)
            icon_label.pack(side="left")

            text_label = tk.Label(frame, text=file, font=('Arial', 16), anchor='w',width=60, height=1)
            text_label.pack(side="left", fill="x", expand=True)

            text_label.bind('<Double-Button-1>', lambda e, f=file: self.open_folder(f))
            icon_label.bind('<Button-1>', lambda e, f=file, fl=file_list: self.select_file(f, fl))

    def refresh(self):
        self.client2m.send('ls')
        ls_response = self.client2m.recv().split('\n')
        if ls_response[0].startswith('200'):
            ls_response[0] = '..'
            file_list = ls_response
        
            self.refresh_file_ls(file_list)

        else:
            messagebox.showinfo("Error", ls_response)

    def select_file(self, file, file_list):
        self.selected_file = file
        self.refresh_file_ls(file_list)


    def open_folder(self, folder_name):
        self.client2m.send('cd' + ' ' + folder_name)
        cd_response = self.client2m.recv()
        if cd_response.startswith('250'):
            self.refresh()
        else:
            messagebox.showinfo("Error", cd_response)

    def select_pi(self, chunk):
        pi = self.pi_from_chunk_string(chunk)
        is_pi1_connected = False
        is_pi2_connected = False
        is_pi3_connected = False
        if pi == 'pi1' :
            if is_pi1_connected == False:
                try:
                    client2pi1 = RawClient(SLAVE_IP_PORT["pi1"]["ip"], SLAVE_IP_PORT["pi1"]["port"])
                    client2pi1.send('hello')
                    hello_response = client2pi1.recv()
                    if not hello_response.startswith('200'):
                        messagebox.showinfo("HELLO Error", hello_response)
                        return
                    is_pi1_connected = True
                except Exception as e:
                    messagebox.showinfo("Error", 'PI1 Error')
                    return None

            return client2pi1

        elif pi == 'pi2':
            if is_pi2_connected == False:
                try:
                    client2pi2 = RawClient(SLAVE_IP_PORT["pi2"]["ip"], SLAVE_IP_PORT["pi2"]["port"])
                    client2pi2.send('hello')
                    hello_response = client2pi2.recv()
                    if not hello_response.startswith('200'):
                        messagebox.showinfo("HELLO Error", hello_response)
                        return
                    is_pi2_connected = True
                except Exception as e:
                    messagebox.showinfo("Error", 'PI1 Error')
                    return None
                
            return client2pi2
        
        elif pi == 'pi3' :
            if is_pi3_connected == False:
                try:
                    client2pi3 = RawClient(SLAVE_IP_PORT["pi3"]["ip"], SLAVE_IP_PORT["pi3"]["port"])
                    client2pi3.send('hello')
                    hello_response = client2pi3.recv()
                    if not hello_response.startswith('200'):
                        messagebox.showinfo("HELLO Error", hello_response)
                        return
                    is_pi3_connected = True
                except Exception as e:
                    messagebox.showinfo("Error", 'PI1 Error')
                    return None
            return client2pi3

        else:
            messagebox.showinfo("Error", 'PI Error')
            return None


    def pi_from_chunk_string(self, string):
        string = string[1:-1]
        parts = string.split(', ')
        return parts[0]
    
    def progress_bar(self, progress_name='upload'):
        # 创建进度窗口
        progress_window = tk.Toplevel(self.window)
        progress_window.title(progress_name)
        progress_window.geometry('400x150')
        progress_var = tk.DoubleVar()

        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=300)
        progress_bar.pack(pady=20, padx=20)

        progress_label = tk.Label(progress_window, text=f"{progress_name}ing...")
        progress_label.pack(pady=10)

        return progress_var, progress_window
    
    def upload(self):
        # 打开本机文件选择对话框
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        # 异步上传
        threading.Thread(target=self.upload_file, args=(file_path,)).start()
    
    def upload_file(self, file_path):
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        file_name = file_name.replace(' ', '_')
        stor_chunk_list = []
        self.client2m.send('stor' + ' ' + file_name  + ' ' + str(file_size))
        stor_response = ""
        while True:
            stor_res = self.client2m.recv()
            stor_response += stor_res
            if stor_res.endswith('.*.'):
                break
        stor_response = stor_response.split('\n')
        if not stor_response[0].startswith('200'):
            messagebox.showinfo("Error", stor_response)
            return
        stor_chunk_list = stor_response[2:-1]
        # 与从机建立连接
        time.sleep(1)    
        # 上传文件
        progress_var, progress_window = self.progress_bar('upload')
        progress_var.set(0)  # 进度条初始化为 0
        with open(file_path, 'rb') as f:
            upload_size = 0
            for i, chunk in enumerate(stor_chunk_list): 
                client2s = self.select_pi(chunk)
                if not client2s:
                    return
                client2s.send('stor' + ' ' + chunk)
                stor_response = client2s.recv()
                if not stor_response.startswith('300'):
                    messagebox.showinfo("STOR Error", stor_response)
                    return
                data = f.read(CHUNK_SIZE)
                header = struct.pack('!I', len(data))
                client2s.send(header, is_byte=True)
                client2s.send(data, is_byte=True)
                data_response = client2s.recv()
                if not data_response.startswith('200'):
                    messagebox.showinfo("UPLOAD Error", data_response)
                    return
                # 更新进度条
                upload_size = upload_size + len(data)
                progress_var.set((upload_size / file_size) * 100)
                progress_window.update_idletasks()
        # 上传完成后关闭进度窗口
        progress_window.destroy()  
        client2s.send('quit')
        quit_response = client2s.recv()
        if not quit_response.startswith('221'):
            messagebox.showinfo("CS QUIT Error", quit_response)
            return
        client2s.close()
        
        self.refresh()

    def download(self):
        selected_file = self.selected_file
        if not selected_file:
            messagebox.showinfo("Error", '请选择文件')
            return
        # 打开本地文件存储对话框
        local_file = filedialog.asksaveasfilename(initialfile=selected_file)
        if not local_file:
            return
        # 异步下载
        threading.Thread(target=self.download_file, args=(local_file,selected_file)).start()

    def download_file(self, local_file, selected_file):
        retr_chunk_list = []
        self.client2m.send('retr' + ' ' + selected_file)
        retr_response = ""
        while True:
            retr_res = self.client2m.recv()
            retr_response += retr_res
            if retr_res.endswith('.*.'):
                break
            elif not retr_res:
                break
        if not retr_response.startswith('200'):
            messagebox.showinfo("Error", retr_response)
            return
        retr_chunk_list = retr_response.split('\n')[2:-1]
        # 创建进度窗口
        progress_var, progress_window = self.progress_bar('download')
        progress_var.set(0)  # 进度条初始化为 0
        # 下载文件
        with open(local_file, 'wb') as f:
            download_size = 0
            for chunk in retr_chunk_list:
                client2s = self.select_pi(chunk)
                if not client2s:
                    return
                client2s.send('retr' + ' ' + chunk)
                header = client2s.recv(is_byte=True)
                code= struct.unpack('!4s', header[:4])[0]
                if code != b'200 ':
                    messagebox.showinfo("Error", header.decode(encoding='utf-8'))
                    return
                length = struct.unpack('!I', header[4:8])[0]
                data = b''
                while len(data) < length:
                    data += client2s.recv(is_byte=True)
                    # 更新进度条
                    download_size = download_size + 1024
                    progress_var.set((download_size / (len(retr_chunk_list)*CHUNK_SIZE)) * 100)
                    progress_window.update_idletasks()
                f.write(data)
        # 上传完成后关闭进度窗口
        progress_window.destroy() 
                
        client2s.send('quit')
        quit_response = client2s.recv()
        if not quit_response.startswith('221'):
            messagebox.showinfo("Error", quit_response)
            return
        client2s.close()
        self.refresh()
        

    def delete(self):
        selected_file = self.selected_file
        if not selected_file:
            messagebox.showinfo("Error", '请选择文件')
            return
        if messagebox.askokcancel("删除文件", "确定要删除文件吗？"):
            if "." not in selected_file:
                self.client2m.send('rmdir' + ' ' + selected_file)
            else:
                self.client2m.send('del' + ' ' + selected_file)
                
            dele_response = self.client2m.recv()
            if dele_response.startswith('200'):
                self.refresh()
            else:
                messagebox.showinfo("Error", dele_response)
        pass

    def create_folder(self):
        folder_name = simpledialog.askstring('新建文件夹', '请输入文件夹名字')
        if not folder_name:
            return
        folder_name = folder_name.replace(' ', '_')
        self.client2m.send('mkdir' + ' ' + folder_name)
        mkdir_response = self.client2m.recv()
        if mkdir_response.startswith('257'):
            self.refresh()
        else:
            messagebox.showinfo("Error", mkdir_response)

if __name__ == '__main__':
    cloud_gui = Cloud_GUI()
    cloud_gui.create_login()
    cloud_gui.window.mainloop()
