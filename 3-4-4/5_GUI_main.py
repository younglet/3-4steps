from miniROS import *
import easygui
import json
import time


gui_node = Node('GUI')
@initialize(gui_node)
def init():
    gui_node.messages = [] # 用于存储别的节点发来的信息
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        config = { 'password':'123456' }
    password = easygui.passwordbox('请输入登录密码')
    if password ==  config['password']:
        easygui.msgbox('登录成功')
    else:
        easygui.msgbox('登录失败')
        miniROS.stop()
    easygui.msgbox('欢迎进入机器人操作系统')


@set_task(gui_node, loop=True, main=True)
def set_input():
    # 将阻塞时收到的信息全部显示出来
    while gui_node.messages:
        message = gui_node.messages.pop(0)
        easygui.msgbox(message)

    choice = easygui.buttonbox('请选择要控制的机器人', choices=['刷新状态','前进', '停止','后退', '天气查询'])

    if choice == '刷新状态':
        gui_node.node_continue()
    if choice == '前进':
        Bus.publish('set_velocity', 10)
    elif choice == '停止':
        Bus.publish('set_velocity', 0)
    elif choice == '后退':
        Bus.publish('set_velocity', -10)
    elif choice == '天气查询':
        city = easygui.enterbox('请输入城市', '天气查询')
        if not city:
            gui_node.node_continue()
        Bus.publish('weather',  city)

    while not gui_node.messages:
        pass



@subscribe(gui_node, 'message')
def handler(data):
    gui_node.messages.append(data)



#具有前进、后退和停止功能的模拟运动节点
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


from weather_node import weather_node

@subscribe(weather_node, 'weather')
def handler(data):
    print('收到天气查询指令')
    weather_node.query(data)


gui_node.register()
movement_node.register()
weather_node.register()
miniROS.run()