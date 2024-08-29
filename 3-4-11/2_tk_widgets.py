import tkinter as tk


window = tk.Tk()
window.title('斯坦星球')
window.geometry('200x200')

button = tk.Button(master=window, text="点击我") # 创建一个按钮
button.pack() # 将按钮添加到主窗口

# button.pack_forget() # 隐藏按钮

# 创建一个按钮并添加到主窗口
# tk.Button(master=window, text="点击我").pack() 

window.mainloop()