# 节点的生命周期

from miniROS import *
import random
import time



console_node = Node('Console')

@initialize(console_node)
def initialize():
    console_node.count = 0
    print('Console节点初始化')

"""
等效写法
@initialize(console_node)
def initialize(count = 0):
    print('Console节点初始化')
"""

@subscribe(console_node, 'input_data') 
def show_input_data(input_data): 
    if input_data == 'STOP':
        print(f'控制台节点停止运行,总共收到{console_node.count}条数据')
        console_node.stop()

    console_node.count += 1
    print(f'\n收到用户输入数据：{input_data}')




input_node = Node('Input') 

@set_task(input_node, loop = True, index= -1)
def get_input():
    input_data = input('请在模拟输入数据:')
    Bus.publish('input_data', input_data) 


console_node.register()
input_node.register()

Node.run()