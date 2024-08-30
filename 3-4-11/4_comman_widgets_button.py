import tkinter as tk
import tkinter.ttk as ttk


window = tk.Tk()
window.title('斯坦星球')
window.geometry('200x200')

def function():
    print("点击了function按钮")

# 通过回调函数设置按钮功能
function_button = ttk.Button(master=window, text="function按钮", command=function) 
function_button.pack()


# 通过lambda表达式设置按钮功能
lambda_button = ttk.Button(master=window, text="lambda按钮", command=lambda: print("点击了lambda按钮")) 
lambda_button.pack()

window.mainloop()

# Button还有如下常用方法和属性：
# invoke()方法：模拟点击按钮
# state：按钮的状态，默认为normal，即正常状态，可选值有normal、disabled、hidden
# width：按钮的宽度，默认为0，即自动调整大小
# padding：按钮的内边距，默认为(0,0),形式为 (x, y) 或 (left, top, right, bottom) 来分别指定不同方向的内边距。