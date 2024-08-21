from drone_simulator import Drone

drone = Drone(target_height=100) # 初始化无人机，目标高度为100


# 固定的升力让无人机停在目标高度，需要使用PID控制器来控制无人机的飞行

def init():
    global drone, dt, height_data, time_data
    height_data = [0]
    time_data = [0]
    return line, 

def  update(frame):
    global drone, dt, height_data, time_data
    error = drone.target_height - drone.height
    thrust = 0.1 * error
    drone.step(thrust, dt)
    height_data.append(drone.height)
    time_data.append(time_data[-1] + dt)
    line.set_data(time_data, height_data)
    return line,


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation



# 创建图形
fig, ax = plt.subplots()
ax.set_xlim(0, 200)
ax.set_ylim(0, 120)
line, = ax.plot([], [], lw=2)
dt = 1

# 初始化数据
height_data = [0]
time_data = [0]

# 创建动画
animation = FuncAnimation(fig, update, frames=200, init_func=init, interval=1, repeat=False)

plt.show()