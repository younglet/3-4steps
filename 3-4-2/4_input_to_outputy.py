# 节点信号的传递

from miniROS import *
import random
import time



console_node = Node('Console')

@set_task(console_node, loop = True)
def show_info():
    print(random.randint(1, 100))
    time.sleep(1)

@subscribe(console_node, 'input_data') # 控制台节点订阅【input_data】主题
def show_input_data(input_data): # 接收输入节点发布的【input_data】主题的数据
    print(f'\n收到用户输入数据：{input_data}')


input_node = Node('Input') 

@set_task(input_node, loop = True, index= -1)
def get_input():
    input_data = input('请在模拟输入数据:')
    Bus.publish('input_data', input_data) # 输入节点发布【input_data】主题的数据


console_node.register()
input_node.register()

Node.run()