import tkinter as tk
import tkinter.ttk as ttk


window = tk.Tk()
window.title('斯坦星球')
window.geometry('200x200')

frame1 = ttk.Frame(master=window)
label1 = ttk.Label(master=frame1, text='标签1')
label1.pack()
button1 = ttk.Button(master=frame1, text='按钮1')
button1.pack()

frame2 = ttk.Frame(master=window)
label2 = ttk.Label(master=frame2, text='标签2')
label2.pack()
button2 = ttk.Button(master=frame2, text='按钮2')
button2.pack()


frame1.grid(row=0, column=0)
frame2.grid(row=1, column=1)

window.mainloop()