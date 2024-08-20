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
for i in range(50):
    drone.step(thrust=100, dt=1)# 1秒内提供固定的10N升力
    drone.log()

# 固定的升力无法让无人机停在目标高度，需要使用PID控制来控制无人机的飞行
