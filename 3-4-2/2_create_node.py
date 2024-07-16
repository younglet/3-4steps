# 控制台节点创建

from miniROS import *
import random


console_node = Node('Console')

@set_task(console_node)
def show_info():
    print(random.randint(1, 100))


console_node.register()
Node.run()