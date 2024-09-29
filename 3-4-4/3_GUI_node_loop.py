from miniROS import *


import easygui
import json
import time
gui_node = Node('GUI')
@initialize(gui_node)
def init():
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
    choice = easygui.buttonbox('请选择要控制的机器人', choices=['前进', '停止', '后退'])
    easygui.msgbox('任务：' + choice + '开始')
    time.sleep(1)
    easygui.msgbox('任务： ' + choice + '已完成')


gui_node.register()
miniROS.run()