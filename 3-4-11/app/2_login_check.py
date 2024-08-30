import tkinter as tk
import tkinter.ttk as ttk

class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("智能机器人助手")
        self.window.geometry("600x400")
        
        self.PASSWORD = "123"
        self.login_frame_init()
        self.login_frame_show()

    def login_frame_init(self):
        self.login_frame = ttk.Frame(self.window)
        ttk.Label(self.login_frame, text="密码").grid(row=0, column=0)
        self.password_entry = ttk.Entry(self.login_frame, show='*')
        self.password_entry.grid(row=0, column=1)
        self.login_button = ttk.Button(self.login_frame, text="登录", command=self.login)
        self.login_button.grid(row=1, column=1, columnspan=2)
    
    def login_frame_show(self):
        self.login_frame.pack(pady=100)
    
    def login(self):
        if self.password_entry.get() == self.PASSWORD:
            self.login_button.config(text="密码正确")
        else:
            self.login_button.config(text="密码错误")

    def run(self):
        self.window.mainloop()
    
if __name__ == "__main__":
    app = App()
    app.run()