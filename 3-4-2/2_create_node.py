# 控制台节点创建
from miniROS import *
import random


# 创建控制台节点，并命名为Console
console_node = Node('Console')

# 通过@set_task装饰器，将show_info函数注设为控制台节点的任务
@set_task(console_node)
def show_info():
    print(random.randint(1, 100))
    console_node.stop()


# 注册控制台节点
console_node.register()

# 系统开始运行
miniROS.run()