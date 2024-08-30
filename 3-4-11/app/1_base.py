import tkinter as tk
import tkinter.ttk as ttk

class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("智能机器人助手")
        self.window.geometry("600x400")
    
    def run(self):
        self.window.mainloop()
    
if __name__ == "__main__":
    app = App()
    app.run()