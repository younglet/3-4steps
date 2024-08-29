import tkinter as tk
import tkinter.ttk as ttk

def print_entry_content():
    print(entry.get())

window = tk.Tk()
window.title('斯坦星球')
window.geometry('200x200')

entry = ttk.Entry(master=window)
entry.pack()

button = ttk.Button(master=window, text="打印输入框内容", command=print_entry_content)
button.pack()

window.mainloop()

# Entry还有如下常用方法和属性：
# insert()：在指定位置插入文本, 参数：index表示插入位置，text表示插入的文本
# state：按钮的状态，默认为normal，即正常状态，可选值有normal、disabled、hidden
# font：设置输入框的字体，默认为("TkDefaultFont", 14)
# width：设置输入框的宽度，默认为16
# justify：设置输入框中内容对齐方式，默认为left，可选值有left、center、right
# show：设置输入框中显示的文本，默认为空，即显示输入框中的文本,若show="*"，则输入框中显示*号