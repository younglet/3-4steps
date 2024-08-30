import tkinter as tk


window = tk.Tk()
window.title('斯坦星球')
window.geometry('200x200')

# 创建一个按钮， 放置于主窗口， 按钮的文字是“点击我”
button = tk.Button(master=window, text="点击我") 
# 将按钮添加到主窗口
button.pack()

# 如果组件不需要被引用，可以这样创建
# tk.Button(master=window, text="点击我").pack() 


# button.pack_forget() # 隐藏按钮

window.mainloop()