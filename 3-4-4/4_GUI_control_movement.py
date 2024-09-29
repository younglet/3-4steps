from miniROS import *


import easygui
import json
import time

gui_node = Node('GUI')
@initialize(gui_node)
def init():
    gui_node.messages = [] # 消息队列
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        config = { 'password':'123456' }
    password = easygui.passwordbox('请输入登录密码')
    if password ==  config['password']:
        easygui.msgbox('登录成功，欢迎进入机器人操作系统')    
    else:
        easygui.msgbox('登录失败')
        miniROS.stop()


@set_task(gui_node, loop=True, main=True)
def set_input():
    while gui_node.messages:
        message = gui_node.messages.pop(0)
        easygui.msgbox(message)

    choice = easygui.choicebox('请选择要控制的机器人', choices=['刷新','前进', '停止', '后退'])
    
    if choice == '刷新':
        pass

    else:
        if choice == '前进':
            Bus.publish('set_velocity', 10)
        elif choice == '停止':
            Bus.publish('set_velocity', 0)
        elif choice == '后退':
            Bus.publish('set_velocity', -10)

        while not gui_node.messages:
            pass

@subscribe(gui_node, 'message')
def handler(data):
    gui_node.messages.append(data)


    

movement_node = Node('Movement')
@initialize(movement_node)
def init():
    movement_node.velocity = 0
    Bus.publish('message', '移动模块初始化完毕')

@set_task(movement_node, loop=True)
def move():
    if movement_node.velocity == 0:
        print('移动模块正在等待指令')
    else:
        print(f'移动模块正在工作，速度为:{movement_node.velocity}')
    time.sleep(1)

@subscribe(movement_node, 'set_velocity')
def handler(data):
    movement_node.velocity = data
    Bus.publish('message', f'移动模块收到指令，现在速度为:{movement_node.velocity}')


gui_node.register()
movement_node.register()
miniROS.run()