# 节点信号的传递


from miniROS import *
import random
import time



console_node = Node('Console')


@set_task(console_node, loop = True)
def show_info():
    print(random.randint(1, 100))
    time.sleep(1)

@subscribe(console_node, 'input_data')
def show_input_data(input_data):
    print(f'\n收到用户输入问题：{input_data}')


input_node = Node('Input')

@set_task(input_node, loop = True)
def get_input():
    input_data = input('你有什么问题？')
    Bus.publish('input_data', input_data)


console_node.register()
input_node.register()

Node.run()