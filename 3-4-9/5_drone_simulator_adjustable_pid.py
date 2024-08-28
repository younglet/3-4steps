from drone import Drone  

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider

# 目标高度
target_height = 100
drone = Drone(target_height)

# 创建图形
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.3)
ax.set_xlim(0, 200)
ax.set_ylim(0, 120)
line, = ax.plot([], [], lw=2)
dt = 1
last_error = 0
integral = 0

# 滑块位置设置
ax_target_height = fig.add_axes([0.25, 0.2, 0.5, 0.03])
ax_Kp = fig.add_axes([0.25, 0.15, 0.5, 0.03], )
ax_Ki = fig.add_axes([0.25, 0.1, 0.5, 0.03],)
ax_Kd = fig.add_axes([0.25, 0.05, 0.5, 0.03], )

# 创建滑块
s_target_height = Slider(ax_target_height, 'H', 0, 120, valinit=target_height)
s_Kp = Slider(ax_Kp, 'P', 0.0, 1.0, valinit=0.1)
s_Ki = Slider(ax_Ki, 'I', 0.0, 0.001, valinit=0.0003)
s_Kd = Slider(ax_Kd, 'D', 0.0, 1.0, valinit=0.4)

def init():
    global drone, height_data, time_data
    height_data = [drone.height]
    time_data = [0]
    return line, 

def update(frame):
    global drone, dt, height_data, time_data, last_error, integral
    global s_Kp, s_Ki, s_Kd, s_target_height
    
    # 获取最新的滑块值
    Kp = s_Kp.val
    Ki = s_Ki.val
    Kd = s_Kd.val
    drone.target_height = s_target_height.val
     
    # PID控制
    error = drone.target_height - drone.height
    integral += error * dt
    derivative = (error - last_error) / dt
    thrust = (Kp * error + Kd * derivative + Ki * integral)
    drone.step(thrust, dt)
    last_error = error

    # 更新图形
    height_data.append(drone.height)
    time_data.append(time_data[-1] + dt)
    line.set_data(time_data, height_data)
    return line,


animation = FuncAnimation(fig, update, frames=200, init_func=init, interval=100, repeat=True)

plt.show()