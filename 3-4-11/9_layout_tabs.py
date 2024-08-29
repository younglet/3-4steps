import tkinter as tk
from tkinter import ttk

window = tk.Tk()
window.title('斯坦星球')
window.geometry('200x200')

notebook = ttk.Notebook( master=window)

# 创建第一个Tab页面
tab1 = ttk.Frame(master=notebook)
ttk.Label(master=tab1, text="这是第1个页面").pack()

# 创建第二个Tab页面
tab2 = ttk.Frame(master=notebook)
ttk.Label(master=tab2, text="这是第2个月面").pack()

# 将Tab页面添加到Notebook
notebook.add(tab1, text="页面1")
notebook.add(tab2, text="页面2")

# 将Notebook添加到主窗口
notebook.pack(expand=True, fill="both")

# 启动主循环
window.mainloop()