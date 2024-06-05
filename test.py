import tkinter as tk
from tkinter import ttk

root = tk.Tk()

# 创建一个Treeview组件
tree = ttk.Treeview(root)

# 加载图标
file_icon = tk.PhotoImage(file='file_icon.png')  # 你的文件图标路径

# 添加带有图标的文件
for i in range(10):
    tree.insert('', 'end', text='File {}'.format(i), image=file_icon)

tree.pack()

root.mainloop()