import tkinter as tk
import tkinter.ttk as ttk
import datetime

class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("智能机器人助手")
        self.window.geometry("600x400")
        
        self.login_frame_init()
        self.main_frame_init()
        
        self.PASSWORD = "123"

        self.func1_hook = None
        self.func2_hook = None

        self.show_login_frame()
    def log(self, message):
        if self.log_text:
            self.log_text.configure(state='normal')
            line = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} : {str(message)}\n"
            self.log_text.insert(tk.END, line)
            self.log_text.see(tk.END)
            self.log_text.configure(state='disabled')
    
    def func1(self):
        self.log("功能1运行")
        if self.func1_hook:
            self.func2_hook()
    
    def func2(self):
        self.log('功能2运行')
        if self.func2_hook:
            self.func1_hook()
    
    def login_frame_init(self):
        self.login_frame = ttk.Frame(self.window)
        ttk.Label(self.login_frame, text="密码").grid(row=0, column=0)
        self.password_entry = ttk.Entry(self.login_frame, show='*')
        self.password_entry.grid(row=0, column=1)
        self.login_button = ttk.Button(self.login_frame, text="登录", command=self.login)
        self.login_button.grid(row=1, column=1, columnspan=2)
    
    def show_login_frame(self):
        self.login_frame.pack(pady=100)
    
    def main_frame_init(self):
        self.notebook = ttk.Notebook(self.window)
        
        self.func1_frame = ttk.Frame(self.notebook)
        ttk.Button(self.func1_frame, text="功能1", command=lambda:self.func1()).pack()
        self.notebook.add(self.func1_frame, text="功能1")

        self.func2_frame = ttk.Frame(self.notebook)
        ttk.Button(self.func2_frame, text="功能2", command=lambda:self.func2()).pack()
        self.notebook.add(self.func2_frame, text="功能2")
        
        self.log_frame = ttk.Frame(self.notebook)
        self.log_text = tk.Text(self.log_frame, width=60, state='disabled')
        self.log_text.pack()
        self.notebook.add(self.log_frame, text="日志")

    def show_main_frame(self):
        self.login_frame.pack_forget()
        self.notebook.pack()


    
    def login(self):
        if self.password_entry.get() == self.PASSWORD:
            self.show_main_frame()
        else:
            self.login_button.configure(text="密码错误")

    def run(self):
        self.window.mainloop()
    
if __name__ == "__main__":
    def say_hi():
        print("hi")
    def say_bye():
        print("bye")

    app = App()
    app.func1_hook = say_hello
    app.func2_hook = say_bye
    app.run()