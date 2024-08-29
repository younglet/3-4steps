import tkinter as tk
import tkinter.ttk as ttk


window = tk.Tk()
window.title('斯坦星球')
window.geometry('200x200')

button1 = tk.Button(master=window, text='点击我')
button1.pack()

button2 = ttk.Button(master=window, text='点击我')
button2.pack()

window.mainloop()