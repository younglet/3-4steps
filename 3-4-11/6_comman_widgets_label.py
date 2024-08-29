import tkinter as tk
import tkinter.ttk as ttk


def set_label_by_entry_content():
    entry_content = entry.get()
    label.config(text=entry_content) # 修改标签内容

window = tk.Tk()
window.title('斯坦星球')
window.geometry('200x200')

label = tk.Label(master=window, text="默认标签")
label.pack()

entry = tk.Entry(master=window)
entry.pack()

button = tk.Button(master=window, text="修改标签", command=set_label_by_entry_content)
button.pack()

window.mainloop()

# Label还有如下常用属性：
# anchor：标签文本的显示位置，默认为center, 可以设置为N, S, E, W, NE, NW, SE, SW，代表上下左右以及左上，左下，右上，右下
# width：标签的宽度，单位为字符
# text：显示在标签上的文本
# bg：标签的背景颜色, 可以是颜色名称，也可以是十六进制颜色代码
# fg：标签的前景色，即字体颜色
# font：标签的字体样式，如：font=("宋体", 20)
