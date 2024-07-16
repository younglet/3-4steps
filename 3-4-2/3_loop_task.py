# 控制台节点循环

from miniROS import *
import random
import time


console_node = Node('Console')


@set_task(console_node, loop = True)
def show_info():
    print(random.randint(1, 100))
    time.sleep(1)


console_node.register()
Node.run()