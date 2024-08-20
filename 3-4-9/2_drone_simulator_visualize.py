class Drone:
    """
    模拟无人机类
    """
    def __init__(self,  target_height):
        """
        初始化无人机
        :param initial_height: 初始高度
        :param target_height: 目标高度
        """
        self.target_height = target_height
        self.height = 0
        self.velocity = 0
        self.acceleration = 0
        self.weight = 100
    
    def step(self, thrust, dt):
        """
        计算无人机下一时刻的状态
        :param thrust: 推力
        :param dt: 时间间隔
        """
        self.acceleration = thrust / self.weight 
        self.velocity += self.acceleration * dt
        self.height += self.velocity * dt
    
    def log(self):
        """
        打印无人机当前状态
        """
        print(f"当前高度: {self.height}, 当前速度: {self.velocity}, 当前加速度: {self.acceleration}")


drone = Drone(target_height=100) # 初始化无人机，目标高度为100


# 固定的升力让无人机停在目标高度，需要使用PID控制器来控制无人机的飞行

def init():
    global drone, dt, height_data, time_data
    height_data = [0]
    time_data = [0]
    return line, 

def  update(frame):
    global drone, dt, height_data, time_data
    drone.step(20, dt)
    height_data.append(drone.height)
    time_data.append(time_data[-1] + dt)
    line.set_data(time_data, height_data)
    return line,


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation



# 创建图形
fig, ax = plt.subplots()
ax.set_xlim(0, 100)
ax.set_ylim(0, 140)
line, = ax.plot([], [], lw=2)
dt = 1

# 初始化数据
height_data = [0]
time_data = [0]

# 创建动画
ani = FuncAnimation(fig, update, frames=100, init_func=init, interval=10, repeat=False)

plt.show()