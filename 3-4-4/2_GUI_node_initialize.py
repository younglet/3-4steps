from miniROS import *

import easygui
import json
gui_node = Node('GUI')
@initialize(gui_node)
def init():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        config = { 'password':'123456' }
    password = easygui.passwordbox('请输入登录密码')
    #TODO: 设置密码循环次数
    if password ==  config['password']:
        easygui.msgbox('登录成功')
    else:
        easygui.msgbox('登录失败')
        miniROS.stop()
    easygui.msgbox('欢迎进入机器人操作系统')

gui_node.register()
miniROS.run()