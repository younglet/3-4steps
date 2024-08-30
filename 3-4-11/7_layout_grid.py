import tkinter as tk
import tkinter.ttk as ttk


window = tk.Tk()
window.title('斯坦星球')
window.geometry('200x200')

button1 = ttk.Button(master=window, text="按钮1")
button2 = ttk.Button(master=window, text="按钮2")
button3 = ttk.Button(master=window, text="按钮3")
button4 = ttk.Button(master=window, text="按钮4")

button1.grid(row=0, column=0) 
button2.grid(row=0, column=1)
button3.grid(row=1, column=0)
button4.grid(row=1, column=1)

button5 = ttk.Button(window, text="按钮5")
# columnspan表示占用多少列， sticky表示对齐方式, ew表示东西两个方向
button5.grid(row=2, column=0, columnspan=2, sticky="ew") 
# button5.grid_forget() # 隐藏按钮

window.mainloop()
