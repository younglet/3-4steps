from drone import Drone
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# 无人机基本设定
drone = Drone(target_height=100) # 初始化无人机，目标高度为100
dt = 1 # 设置模拟的时间间隔为1秒
last_error = 0 # 上一次误差
integral = 0 # 误差累积值

# 图表基本设定
fig, ax = plt.subplots() # 创建图形
ax.set_xlim(0, 200) # 设置x轴范围
ax.set_ylim(0, 120) # 设置y轴范围
line, = ax.plot([], [], lw=2) # 创建线， lw为线宽

# 初始化图标数据
height_data = [drone.height] # 0时刻的高度为无人机的高度
time_data = [0] # 0时刻


def init():
    global drone, height_data, time_data
    height_data = [drone.height]
    time_data = [0]
    return line, 


def update(frame):
    global drone, dt, height_data, time_data, last_error, integral

    error = drone.target_height - drone.height
    integral += error
    derivative = (error - last_error) / dt
    thrust =(0.1 * error   + 0.1 *  derivative +  0.00035 * integral)
    drone.step(thrust, dt)
    last_error = error

    height_data.append(drone.height)
    time_data.append(time_data[-1] + dt)
    line.set_data(time_data, height_data)
    return line,

# 创建动画
animation = FuncAnimation(fig, update, frames=200, init_func=init, interval=1, repeat=False)

plt.show()