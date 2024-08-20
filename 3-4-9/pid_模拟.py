import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.last_error = 0
        self.integral = 0

    def update(self, error, dt):
        self.integral += error * dt
        derivative = (error - self.last_error) / dt
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.last_error = error
        return output

class DroneSimulator:
    def __init__(self, initial_height, target_height):
        self.height = initial_height
        self.target_height = target_height
        self.velocity = 0
        self.acceleration = 0

    def step(self, thrust, dt):
        self.acceleration = thrust - 9.8  
        self.velocity += self.acceleration * dt
        self.height += self.velocity * dt
        return self.height

def update(frame):
    global drone, pid_controller, target_height, height_data, time_data

    # 读取当前高度
    current_height = drone.height
    # 计算误差
    error = target_height - current_height

    # PID控制器计算推力
    thrust = pid_controller.update(error, dt)

    # 更新无人机的高度
    new_height = drone.step(thrust, dt)

    # 更新数据
    height_data.append(new_height)
    time_data.append(time_data[-1] + dt)

    # 更新图形
    line.set_xdata(time_data)
    line.set_ydata(height_data)

    return line,

def init():
    line.set_data([], [])
    return line,

# 初始参数
initial_height = 0
target_height = 20
kp = 0.5
ki = 0.01
kd = 0.1
dt = 0.1  # 时间步长

# 创建PID控制器
pid_controller = PIDController(kp, ki, kd)

# 创建无人机模拟器
drone = DroneSimulator(initial_height, target_height)

# 创建图形
fig, ax = plt.subplots()
ax.set_xlim(0, 100)
ax.set_ylim(0, 20)
line, = ax.plot([], [], lw=2)

# 初始化数据
height_data = [initial_height]
time_data = [0]

# 创建动画
ani = FuncAnimation(fig, update, frames=np.arange(0, 100, dt), init_func=init, blit=True, interval=20)

plt.show()