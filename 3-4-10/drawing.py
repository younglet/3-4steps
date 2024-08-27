import tkinter as tk
from tkinter import colorchooser, Canvas, messagebox, ttk, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import cv2
import fractions
import os
from copy import deepcopy
import time

class SpecialFrame:
    pass

LOOPSTOP_FRAME = SpecialFrame()

class DrawingApp:
    def __init__(self, canvas_width=800, canvas_height=600, video_width=800, video_height=600, video_frame=30):
        # 初始化画布宽度和高度
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        # 设置视频的分辨率
        self.video_width = video_width
        self.video_height = video_height
        # 设置要生产视频的帧率
        self.video_frame = video_frame
        
        self.root = TkinterDnD.Tk()
        self.root.title("画布")
        self.root.resizable(False, False)

        # 初始化颜色、橡皮擦状态、帧数和索引
        self.current_color = "#000000"
        self.eraser_on = False
        self.frames = {1: (Image.new("RGB", (self.canvas_width, self.canvas_height), "white"), "0.5")}
        self.current_frame_index = 1
        self.last_x, self.last_y = None, None

        # 和播放视频有关的参数
        self.output_file = None
        self.play_file = None
        self.choose_file = None
        self.generate_new_video = False
        # 播放视频按钮的钩子函数，外部设定
        self.play_video_hook = None
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 10))
        self.style.configure("TLabel", font=("Helvetica", 10))
        self.style.configure("TScale", troughcolor="gray", background="white")

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.on_closing_hook = None
        
        self.setup_widgets()
        self.setup_canvas()

        # 绑定Ctrl+O快捷键打开图像
        self.root.bind("<Control-o>", self.open_image)
        self.root.update_idletasks()
        self.center_canvas()

    def on_closing(self):
        if self.on_closing_hook is not None:
            self.on_closing_hook()
        self.root.destroy()
    
    def center_canvas(self):
        # 使画布居中
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        frame_width = self.canvas_frame.winfo_width()
        frame_height = self.canvas_frame.winfo_height()

        x_offset = (frame_width - canvas_width) // 2
        y_offset = (frame_height - canvas_height) // 2

        self.canvas.place(x=x_offset, y=y_offset)

    def setup_widgets(self):
        # 设置控制面板框架
        control_frame = ttk.LabelFrame(self.root, text="控制面板", padding=(10, 5))
        control_frame.pack(side="left", fill="y", padx=10, pady=10)

        # 中心框架，包含颜色选择、工具、设置等
        central_frame = ttk.Frame(control_frame)
        central_frame.pack(expand=True)

        # 颜色选择框架
        color_frame = ttk.Frame(central_frame)
        color_frame.pack(pady=(5, 5), anchor="center")
        self.color_label = ttk.Label(color_frame, text="当前颜色: #000000", background=self.current_color, foreground="white", width=20)
        self.color_label.pack(side="left", padx=(0, 5))
        self.color_btn = ttk.Button(color_frame, text="选择颜色", command=self.select_color)
        self.color_btn.pack(side="left")

        # 工具框架
        mid_frame = ttk.Frame(central_frame)
        mid_frame.pack(pady=(5, 5), fill="x", anchor="center")

        tool_frame = ttk.Frame(mid_frame)
        tool_frame.pack(pady=(5, 5), anchor="center")
        self.pen_btn = ttk.Button(tool_frame, text="画笔", command=self.select_pen)
        self.pen_btn.pack(side="left", padx=(5, 5), expand=True, fill="both")
        self.pen_btn.state(["pressed"])
        self.eraser_btn = ttk.Button(tool_frame, text="擦除", command=self.toggle_eraser)
        self.eraser_btn.pack(side="left", padx=(5, 5), expand=True, fill="both")
        self.clear_btn = ttk.Button(tool_frame, text="清空画布", command=self.clear_canvas)
        self.clear_btn.pack(side="left", padx=(5, 5), expand=True, fill="both")

        # 设置框架
        settings_frame = ttk.Frame(mid_frame)
        settings_frame.pack(pady=(5, 5), anchor="center")

        brush_frame = ttk.Frame(settings_frame)
        brush_frame.pack(side="left", padx=(5, 5))
        self.brush_size_label = ttk.Label(brush_frame, text=f"画笔大小: {5:.0f}")
        self.brush_size_label.pack()
        self.brush_slider = ttk.Scale(brush_frame, from_=1, to=50, orient="horizontal", command=lambda _: self.update_brush_size_labels())
        self.brush_slider.set(5)
        self.brush_slider.pack(pady=(0, 5))

        eraser_frame = ttk.Frame(settings_frame)
        eraser_frame.pack(side="left", padx=(5, 5))
        self.eraser_size_label = ttk.Label(eraser_frame, text=f"橡皮擦大小: {10:.0f}")
        self.eraser_size_label.pack()
        self.eraser_slider = ttk.Scale(eraser_frame, from_=1, to=50, orient="horizontal", command=lambda _: self.update_eraser_size_labels())
        self.eraser_slider.set(10)
        self.eraser_slider.pack(pady=(0, 5))

        # 插页时继承当前页的复选框
        self.inherit_var = tk.BooleanVar()
        self.inherit_check = ttk.Checkbutton(central_frame, text="添加页时复制当前页", variable=self.inherit_var)
        self.inherit_check.pack(pady=(5, 5), anchor="center")

        # 媒体框架，包含上传图片和生成视频按钮
        media_frame = ttk.Frame(central_frame)
        media_frame.pack(pady=(5, 5), anchor="center")

        self.upload_btn = ttk.Button(media_frame, text="上传图片", command=self.open_image)
        self.upload_btn.pack(side="left", padx=(5, 5))
        self.gen_video_btn = ttk.Button(media_frame, text="生成视频", command=self.generate_video)
        self.gen_video_btn.pack(side="left", padx=(5, 5))
        
        # 播放视频按钮和下拉箭头按钮
        play_button_frame = ttk.Frame(central_frame)
        play_button_frame.pack(pady=(5, 5), anchor="center")

        self.play_button = ttk.Button(play_button_frame, text="播放视频", command=self.play_video)
        self.play_button.pack(side="left", padx=(5, 0))

        self.dropdown_button = ttk.Button(play_button_frame, text="▼", width=2, command=self.choose_video_file) 
        self.dropdown_button.pack(side="left", padx=(0, 0))
        
        self.loop_var = tk.BooleanVar(value=True)
        self.loop_check = ttk.Checkbutton(play_button_frame, text="循环", variable=self.loop_var)
        self.loop_check.pack(side="left", padx=(5, 0))

    def setup_canvas(self):
        # 设置画布及其周围的框架
        canvas_frame_parent = ttk.Frame(self.root)
        canvas_frame_parent.pack(side="left", padx=10, pady=10, expand=True, fill="both")

        left_nav_frame = ttk.Frame(canvas_frame_parent)
        left_nav_frame.pack(side="left", padx=(0, 10))

        # 包含画布和底部组件的新框架
        canvas_with_bottom_frame = ttk.Frame(canvas_frame_parent)
        canvas_with_bottom_frame.pack(side="left", expand=True, fill="both")

        self.canvas_frame = ttk.Frame(canvas_with_bottom_frame)
        self.canvas_frame.pack(side="top", expand=True, fill="both")

        right_nav_frame = ttk.Frame(canvas_frame_parent)
        right_nav_frame.pack(side="left", padx=(10, 0))
        
        # 导航按钮
        self.left_nav_button = ttk.Button(left_nav_frame, text="⬅", command=self.previous_canvas, width=4)
        self.left_nav_button.pack(pady=(5, 5))
        self.left_insert_button = ttk.Button(left_nav_frame, text="➕", command=self.insert_before, width=4)
        self.left_insert_button.pack(pady=(5, 5))

        self.right_nav_button = ttk.Button(right_nav_frame, text="➡", command=self.next_canvas, width=4)
        self.right_nav_button.pack(pady=(5, 5))
        self.right_insert_button = ttk.Button(right_nav_frame, text="➕", command=self.insert_after, width=4)
        self.right_insert_button.pack(pady=(5, 5))

        # 画布设置
        self.canvas = Canvas(self.canvas_frame, width=self.canvas_width, height=self.canvas_height, bg='white')
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<Button-1>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.reset_last_position)
        self.canvas.bind("<Motion>", self.show_eraser_outline)
        self.canvas.pack(expand=True, fill="both")
        
        self.canvas.drop_target_register(DND_FILES)
        self.canvas.dnd_bind('<<Drop>>', self.on_drop)

        # 创建页面持续时间和页面编号组件的框架，位于画布下方
        bottom_frame = ttk.Frame(canvas_with_bottom_frame)
        bottom_frame.pack(side="top", pady=(5, 10))

        # 页面持续时间组件
        page_duration_frame = ttk.Frame(bottom_frame)
        page_duration_frame.pack(side="left", padx=(5, 5))
        ttk.Label(page_duration_frame, text="帧数设定(秒):").pack(side="left", padx=(5, 5))
        self.frame_duration = ttk.Entry(page_duration_frame, width=10)
        self.frame_duration.pack(side="left")
        self.frame_duration.insert(0, "0.5")
        self.frame_duration.bind("<Return>", lambda _: self.root.focus())
        self.frame_duration.bind("<FocusOut>", self.update_duration)

        # 页面编号显示
        self.page_number_label = ttk.Label(bottom_frame, text="", font=("Helvetica", 14))
        self.page_number_label.pack(side="left", padx=(5, 5))
        self.update_page_number()
        
        # 删除按钮设置
        self.delete_button = ttk.Button(canvas_frame_parent, text="删除", command=self.delete_frame)
        self.delete_button.place(relx=1.0, rely=0.0, anchor="ne")
        self.delete_button.config(width=4)
        
        self.load_frame(self.current_frame_index)

        self.canvas.drop_target_register(DND_FILES)
        self.canvas.dnd_bind('<<Drop>>', self.on_drop)
        
    def reset_last_position(self, event):
        # 重置最后位置
        self.last_x, self.last_y = None, None

    def on_drop(self, event):
        # 处理拖放事件
        file_path = event.data.strip('{}')
        if os.path.isfile(file_path):
            self.load_image(file_path)

    def load_image(self, file_path):
        # 加载图像并更新画布
        try:
            img = Image.open(file_path)
            img = img.resize((self.canvas_width, self.canvas_height), Image.Resampling.LANCZOS)
            self.image.paste(img)
            self.update_canvas()
        except Exception as e:
            messagebox.showerror("加载图像失败", f"由于以下原因加载图像失败: {str(e)}")

    def open_image(self, event=None):
        # 打开图像文件
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.load_image(file_path)

    def update_brush_size_labels(self):
        # 更新画笔大小标签
        self.brush_size_label.config(text=f"画笔大小: {self.brush_slider.get():.0f}")
        
    def update_eraser_size_labels(self):
        # 更新橡皮擦大小标签
        self.eraser_size_label.config(text=f"橡皮擦大小: {self.eraser_slider.get():.0f}")

    def draw(self, event):
        # 绘制方法
        if event.x > self.canvas_width or event.y > self.canvas_height or event.x < 0 or event.y < 0:
            return
        radius = self.eraser_slider.get() if self.eraser_on else self.brush_slider.get()
        fill_color = 'white' if self.eraser_on else self.current_color
        scale_x = self.image.width / self.canvas.winfo_width()
        scale_y = self.image.height / self.canvas.winfo_height()

        if self.last_x and self.last_y:
            self.draw_line(self.last_x, self.last_y, event.x, event.y, fill_color, radius)

        self.draw_obj.ellipse([(event.x * scale_x - radius, event.y * scale_y - radius),
                               (event.x * scale_x + radius, event.y * scale_y + radius)], fill=fill_color)
        self.update_canvas()
        self.last_x, self.last_y = event.x, event.y
        if self.eraser_on:
            self.show_eraser_outline(event)

    def draw_line(self, x1, y1, x2, y2, color, radius):
        # 绘制线条方法
        scale_x = self.image.width / self.canvas.winfo_width()
        scale_y = self.image.height / self.canvas.winfo_height()
        x1, y1 = x1 * scale_x, y1 * scale_y
        x2, y2 = x2 * scale_x, y2 * scale_y
        distance = max(abs(x2 - x1), abs(y2 - y1))
        for i in range(int(distance)):
            x = x1 + (x2 - x1) * i / distance
            y = y1 + (y2 - y1) * i / distance
            self.draw_obj.ellipse([(x - radius, y - radius), (x + radius, y + radius)], fill=color)

    def show_eraser_outline(self, event):
        # 显示橡皮擦轮廓
        if self.eraser_on:
            self.canvas.delete("eraser_outline")
            radius = self.eraser_slider.get()
            self.canvas.create_oval(event.x - radius, event.y - radius, event.x + radius, event.y + radius, outline='black', tags="eraser_outline")

    def select_color(self):
        # 选择颜色方法
        color_code = colorchooser.askcolor(title="选择颜色", initialcolor=self.current_color)
        if color_code[1]:
            self.current_color = color_code[1]
            self.color_label.config(text=f"当前颜色: {self.current_color}", background=self.current_color, foreground=self.get_contrast_text_color(self.current_color))
            self.eraser_on = False
            self.eraser_btn.state(["!pressed"])
            self.pen_btn.state(["pressed"])
            self.canvas.delete("eraser_outline")
            self.update_page_number()

    def toggle_eraser(self):
        # 切换橡皮擦状态
        self.eraser_on = True
        self.eraser_btn.state(["pressed"])
        self.pen_btn.state(["!pressed"])

    def select_pen(self):
        # 选择画笔
        self.eraser_on = False
        self.pen_btn.state(["pressed"])
        self.eraser_btn.state(["!pressed"])
        self.canvas.delete("eraser_outline")

    def next_canvas(self):
        # 下一帧
        self.save_current_frame()
        max_index = max(self.frames.keys())
        if self.current_frame_index < max_index:
            old_index = self.current_frame_index
            self.current_frame_index += 1
            self.load_frame(self.current_frame_index)
            self.animate_slide("left", old_index, self.current_frame_index)
        self.update_page_number()

    def previous_canvas(self):
        # 上一帧
        self.save_current_frame()
        if self.current_frame_index > 1:
            old_index = self.current_frame_index
            self.current_frame_index -= 1
            self.load_frame(self.current_frame_index)
            self.animate_slide("right", old_index, self.current_frame_index)
        self.update_page_number()

    def insert_before(self):
        # 在当前帧之前插入新帧
        self.save_current_frame()
        max_index = max(self.frames.keys())
        
        for index in range(max_index+1, self.current_frame_index, -1):
            self.frames[index] = deepcopy(self.frames[index - 1])

        if self.inherit_var.get():
            self.frames[self.current_frame_index] = (self.frames[self.current_frame_index +1][0].copy(), "0.5")
        else:
            self.frames[self.current_frame_index] = (Image.new("RGB", (self.canvas_width, self.canvas_height), "white"), "0.5")
        self.reorder_frames()
        self.current_frame_index = self.current_frame_index
        
        old_index = self.current_frame_index + 1
        self.load_frame(self.current_frame_index)
        self.animate_slide("right", old_index, self.current_frame_index)
        self.update_page_number()

    def insert_after(self):
        # 在当前帧之后插入新帧
        self.save_current_frame()
        max_index = max(self.frames.keys())
        new_index = self.current_frame_index + 1
        
        for index in range(max_index+1, new_index, -1):
            self.frames[index] = deepcopy(self.frames[index -1])
            
        if self.inherit_var.get():
            self.frames[new_index] = (self.frames[self.current_frame_index][0].copy(), "0.5")
        else:
            self.frames[new_index] = (Image.new("RGB", (self.canvas_width, self.canvas_height), "white"), "0.5")
        
        self.reorder_frames()
        
        old_index = self.current_frame_index
        self.current_frame_index = new_index
        self.load_frame(self.current_frame_index)
        self.animate_slide("left", old_index, self.current_frame_index)
        self.update_page_number()

    def animate_slide(self, direction, old_index, new_index, duration=100, steps=20):
        # 移动方向: "left" 或者 "right"
        # 平滑移动的时间: 单位 毫秒
        # 要移动多少步完成移动

        step_duration = duration // steps

        if direction == "left":
            start_x, end_x = 0, -self.canvas_width
            new_start_x, new_end_x = self.canvas_width, 0
        else:
            start_x, end_x = 0, self.canvas_width
            new_start_x, new_end_x = -self.canvas_width, 0

        delta_x = (end_x - start_x) / steps
        new_delta_x = (new_end_x - new_start_x) / steps

        # Create a new canvas to show the new frame
        new_canvas = Canvas(self.canvas_frame, width=self.canvas_width, height=self.canvas_height, bg='white')
        old_canvas_image = ImageTk.PhotoImage(self.frames[old_index][0].resize((self.canvas_width, self.canvas_height), Image.Resampling.LANCZOS))
        new_canvas_image = ImageTk.PhotoImage(self.frames[new_index][0].resize((self.canvas_width, self.canvas_height), Image.Resampling.LANCZOS))

        self.canvas.create_image(0, 0, image=old_canvas_image, anchor=tk.NW)
        new_canvas.create_image(0, 0, image=new_canvas_image, anchor=tk.NW)
        new_canvas.place(x=new_start_x, y=0)
        self.disable_controls()
        for _ in range(steps):
            self.canvas.place(x=start_x)
            new_canvas.place(x=new_start_x)
            self.root.update()
            start_x += delta_x
            new_start_x += new_delta_x
            self.root.after(step_duration)

        self.canvas.place(x=0)
        new_canvas.place_forget()
        new_canvas.destroy()
        self.enable_controls()

    def disable_controls(self):
        self.pen_btn.config(state="disabled")
        self.eraser_btn.config(state="disabled")
        self.color_btn.config(state="disabled")
        self.clear_btn.config(state="disabled")
        self.upload_btn.config(state="disabled")
        self.gen_video_btn.config(state="disabled")
        self.left_nav_button.config(state="disabled")
        self.left_insert_button.config(state="disabled")
        self.right_insert_button.config(state="disabled")
        self.right_nav_button.config(state="disabled")
        self.play_button.config(state="disabled")
        self.dropdown_button.config(state="disabled")
        self.delete_button.config(state="disabled")

    def enable_controls(self):
        self.pen_btn.config(state="normal")
        self.eraser_btn.config(state="normal")
        self.color_btn.config(state="normal")
        self.clear_btn.config(state="normal")
        self.upload_btn.config(state="normal")
        self.gen_video_btn.config(state="normal")
        self.left_nav_button.config(state="normal")
        self.left_insert_button.config(state="normal")
        self.right_insert_button.config(state="normal")
        self.right_nav_button.config(state="normal")
        self.play_button.config(state="normal")
        self.dropdown_button.config(state="normal")
        self.delete_button.config(state="normal")

    def reorder_frames(self):
        # 重新排序帧
        new_frames = {}
        for i, key in enumerate(sorted(self.frames.keys()), 1):
            new_frames[i] = self.frames[key]
        self.frames = new_frames

    def clear_canvas(self):
        # 清空画布
        self.frames[self.current_frame_index] = (Image.new("RGB", (self.image.width, self.image.height), "white"), self.frame_duration.get())
        self.load_frame(self.current_frame_index)

    def delete_frame(self):
        # 删除当前帧
        if len(self.frames) > 1 and self.current_frame_index in self.frames:
            del self.frames[self.current_frame_index]
            self.reorder_frames()
            self.current_frame_index = min(self.current_frame_index, max(self.frames.keys()))
            self.load_frame(self.current_frame_index)
            self.update_page_number()
        else:
            messagebox.showinfo("操作无效", "无法删除唯一的画布帧")

    def generate_video(self):
        self.save_current_frame()
        try:
            output_dir = "media"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            existing_files = [f for f in os.listdir(output_dir) if f.startswith("output") and f.endswith(".avi")]
            if existing_files:
                max_index = max([int(f.replace("output", "").replace(".avi", "")) for f in existing_files if f.replace("output", "").replace(".avi", "").isdigit()])
                new_index = max_index + 1
            else:
                new_index = 1
            self.output_file = os.path.abspath(os.path.join(output_dir, f"output{new_index}.avi"))

            out = cv2.VideoWriter(self.output_file, cv2.VideoWriter_fourcc(*'DIVX'), self.video_frame, (self.video_width, self.video_height))
            for index in sorted(self.frames.keys()):
                img, duration = self.frames[index]
                frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                resized_frame = cv2.resize(frame, (self.video_width, self.video_height), interpolation=cv2.INTER_LINEAR)
                frame_count = int(self.video_frame * float(fractions.Fraction(duration)))
                for _ in range(frame_count):
                    out.write(resized_frame)
            out.release()
            self.generate_new_video = True
            messagebox.showinfo("视频生成", f"视频{self.output_file}成功生成.")
        except Exception as e:
            messagebox.showerror("视频生成失败", f"由于以下原因生成视频失败: {str(e)}")

    def play_video(self):
        # 自动读取最新生成的视频文件并播放
        if self.generate_new_video:
            self.play_file = self.output_file
        elif self.choose_file is not None:
            self.play_file = self.choose_file
        elif self.output_file is not None:
            self.play_file = self.output_file
        else:
            messagebox.showerror("视频播放失败", "没有视频生成也没有选新视频")
            return
        # 执行钩子函数
        if self.play_video_hook is not None:
            self.play_video_hook()

    def choose_video_file(self):
        # 让用户选择视频文件
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
        if file_path:
            self.choose_file = file_path
            self.generate_new_video = False
            
    def video_generator(self, orientation):
        # orientation是旋转角度
        # 生成视频生成器
        cap = cv2.VideoCapture(self.play_file)
        def generator():
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    if orientation==1:
                        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    elif orientation==2:
                        frame = cv2.rotate(frame, cv2.ROTATE_180)
                    elif orientation==3:
                        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    else:
                        pass
                    frame = cv2.resize(frame, (self.video_width, self.video_height), interpolation=cv2.INTER_LINEAR)
                    yield frame
                elif self.loop_var.get():
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 重播
                elif not self.loop_var.get():
                    time.sleep(0.01)
                    yield LOOPSTOP_FRAME
            cap.release()
            yield None
            
        return generator
    
    def update_canvas(self):
        # 更新画布
        canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.photo = ImageTk.PhotoImage(self.image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS))
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

    def load_frame(self, index):
        # 加载指定帧
        self.image, duration = self.frames[index]
        self.draw_obj = ImageDraw.Draw(self.image)
        self.frame_duration.delete(0, tk.END)
        self.frame_duration.insert(0, duration)
        self.update_canvas()

    def save_current_frame(self):
        # 保存当前帧
        self.frames[self.current_frame_index] = (self.image.copy(), self.frame_duration.get())

    def update_duration(self, event=None):
        # 更新帧持续时间
        duration = self.frame_duration.get()
        try:
            evaluated_duration = float(fractions.Fraction(duration))
            if evaluated_duration <= 0:
                raise ValueError("Duration must be positive")
            img, _ = self.frames[self.current_frame_index]
            self.frames[self.current_frame_index] = (img, duration)
            self.frame_duration.config(background='green')
            self.root.focus()  # Remove focus from the entry widget
        except (ValueError, ZeroDivisionError):
            messagebox.showerror("无效输入", "请输入一个有效的正数或分数形式的持续时间.")
            self.frame_duration.focus_set()

    def update_page_number(self):
        # 更新页面编号显示
        total_pages = len(self.frames)
        self.page_number_label.config(text=f"{self.current_frame_index}/{total_pages}")
        
    def get_contrast_text_color(self, bg_color):
        """ 根据背景颜色计算对比文本颜色（黑/白） """
        bg_color = bg_color.lstrip('#')
        r, g, b = tuple(int(bg_color[i:i+2], 16) for i in (0, 2, 4))
        if (r*0.299 + g*0.587 + b*0.114) > 186:
            return 'black'
        else:
            return 'white'
        
    def run(self):
        self.root.mainloop()

if __name__=='__main__':
    x = DrawingApp()
    x.run()