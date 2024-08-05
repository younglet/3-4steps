from miniROS import *

################################################GUI节点#################################################

import json 
import easygui
import time
gui_node = Node('GUI')
@initialize(gui_node)
def init():
    gui_node.messages = [] # 用于存储别的节点发来的信息
    with open('config.json', 'r') as f:
        config = json.load(f)
    print(config)
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

    choice = easygui.buttonbox('请选择操作', choices=['刷新状态','设定角色'])

    if choice == '刷新状态':
        gui_node.node_continue()

    if choice == '设定角色':
        character = easygui.enterbox('请输入角色性格', '角色性格')
        talk_manner = easygui.enterbox('请输入说话方式', '说话方式')
        if not character or not talk_manner:
            gui_node.node_continue()
        else:
            Bus.publish('setting', {'character':character, 'talk_manner':talk_manner})

    while not gui_node.messages:
        pass


@subscribe(gui_node, 'message')
def handler(data):
    gui_node.messages.append(data)


################################################提示词节点#################################################
import json
prompt_node = Node('Prompt')

@initialize(prompt_node)
def init():
    with open('config.json', 'r') as f:
        config = json.load(f)
    prompt_node.character = config['character']
    prompt_node.talk_manner = config['talk_manner']
    

@subscribe(prompt_node, 'setting')
def handler(data):
    with open('config.json', 'r') as f:
        config = json.load(f)
    with open('config.json', 'w') as f:
        config['character'] = data['character']
        config['talk_manner'] = data['talk_manner']
        json.dump(config, f)
    Bus.publish('message','设置成功')
    prompt_node.is_first = True
    prompt_node.character = data['character']
    prompt_node.talk_manner = data['talk_manner']

    
#################################################注册要运行的节点###########################################
gui_node.register()
prompt_node.register()

miniROS.run()