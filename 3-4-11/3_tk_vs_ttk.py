import tkinter as tk
import tkinter.ttk as ttk


window = tk.Tk()
window.title('斯坦星球')
window.geometry('200x200')

button1 = tk.Button(master=window, text='点击我')
button1.pack()

# 相较于tk, ttk的样式更好，功能更强
button2 = ttk.Button(master=window, text='点击我') 
button2.pack()

window.mainloop()