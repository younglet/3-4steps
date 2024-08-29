from miniROS import *
from app import App

gui_node = Node('GUI')

@initialize(gui_node)
def init():
    gui_node.app = App()
    gui_node.app.log('启动成功')
@set_task(gui_node, main=True)
def process():
    gui_node.app.run()

@subscribe(gui_node, 'input')
def handler(data):
    gui_node.app.log(data)

input_node = Node('Input')
@set_task(input_node)
def process():
    input_text = input('输入信息: ')
    Bus.publish('input', input_text)
    

gui_node.register()
input_node.register()

miniROS.run()