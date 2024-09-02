import tkinter as tk
import tkinter.ttk as ttk
import datetime

class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("智能机器人助手")
        self.window.geometry("600x400")
        
        self.PASSWORD = "123"

        self.get_weather_hook = None

        self.login_frame_init()
        self.main_frame_init()
        self.login_frame_show()
    def log(self, message):
        self.log_text.config(state='normal')
        line = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} : {str(message)}\n"
        self.log_text.insert(tk.END, line)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def get_weather(self):
        city_name = self.city_name_input.get()
        self.get_weather_hook(city_name)
        self.log(f"查询{city_name}天气功能运行")


    def login_frame_init(self):
        self.login_frame = ttk.Frame(self.window)
        ttk.Label(self.login_frame, text="密码").grid(row=0, column=0)
        self.password_entry = ttk.Entry(self.login_frame, show='*')
        self.password_entry.grid(row=0, column=1)
        self.login_button = ttk.Button(self.login_frame, text="登录", command=self.login)
        self.login_button.grid(row=1, column=1, columnspan=2)
    
    def login_frame_show(self):
        self.login_frame.pack(pady=100)
    
    def main_frame_init(self):
        self.notebook = ttk.Notebook(self.window)
        
        self.weather_frame = ttk.Frame(self.notebook)

        # 城市输入框提示文字
        ttk.Label(self.weather_frame, text="城市").pack()
        # 城市输入框
        self.city_name_input = ttk.Entry(self.weather_frame)
        self.city_name_input.pack()
        # 查询按钮
        ttk.Button(self.weather_frame, text="查询", command=lambda:self.get_weather()).pack()
        # 天气查询结果
        self.weather_result = ttk.Label(self.weather_frame)
        self.weather_result.pack()
        self.update_weather_result = lambda res: self.weather_result.config(text=res)

        self.notebook.add(self.weather_frame, text="天气")

        

        self.log_frame = ttk.Frame(self.notebook)
        self.log_text = tk.Text(self.log_frame, width=60, state='disabled')
        self.log_text.pack()
        self.notebook.add(self.log_frame, text="日志")

    def main_frame_show(self):
        self.login_frame.pack_forget()
        self.notebook.pack()
  
    def login(self):
        if self.password_entry.get() == self.PASSWORD:
            self.main_frame_show()
        else:
            self.login_button.config(text="密码错误")

    def run(self):
        self.window.mainloop()
    
if __name__ == "__main__":

    app = App()
    app.run()