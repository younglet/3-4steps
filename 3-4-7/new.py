
from miniROS import *
################################################GUI节点#################################################

import json 
import easygui
import time



gui_node = Node('GUI')
@initialize(gui_node)
def init():
    gui_node.messages = [] # 用于存储别的节点发来的信息
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    gui_node.filters = config['filters']
    # print(config)
    # password = easygui.passwordbox('请输入登录密码')
    # if password ==  config['password']:
    #     easygui.msgbox('登录成功，欢迎进入机器人操作系统')    
    # else:
    #     easygui.msgbox('登录失败')
    #     miniROS.stop()


@set_task(gui_node, loop=True, main=True)
def set_input():
    # 将阻塞时收到的信息全部显示出来
    while gui_node.messages:
        message = gui_node.messages.pop(0)
        easygui.msgbox(message)

    choice = easygui.buttonbox('请选择操作', choices=['刷新状态', '开启（关闭）摄像头', '设置滤镜', '截取画面'])

    if choice == '刷新状态':
        gui_node.node_continue()

    if choice == '开启（关闭）摄像头':
        Bus.publish('set_camera_status', None)

    if choice == '设置滤镜':
        choices =[f['name'] for f in  gui_node.filters]
        choice = easygui.buttonbox('请选择操作', choices=choices)
        Bus.publish('set_filter', [f for f in  gui_node.filters if f['name'] == choice][0])
    
    if choice == '截取画面':
        Bus.publish('shoot_frame', None)

    while not gui_node.messages:
        pass

###############################################摄像头节点#################################################
import cv2
import numpy as np
@subscribe(gui_node, 'message')
def handler(data):
    gui_node.messages.append(data)

camera_node = Node('Camera')
@initialize(camera_node)
def init():
    camera_node.camera = cv2.VideoCapture(0)
    camera_node.current_frame = None
    camera_node.camera_status = False
    camera_node.filter = None

@set_task(camera_node, loop=True)
def process_camera():
    if not camera_node.camera_status:
        cv2.destroyAllWindows()
        camera_node.node_continue()

    ret, frame = camera_node.camera.read()
    cv2.waitKey(30)

    if ret:
        Bus.publish('camera_frame', frame)
    else:
        Bus.publish('message', '摄像头读取失败')

    if camera_node.filter:
        frame = cv2.filter2D(frame, -1, np.array(camera_node.filter))
    camera_node.current_frame = frame
    cv2.imshow('camera', frame)

@subscribe(camera_node, 'set_camera_status')
def set_camera_status(data):
    camera_node.camera_status =  not camera_node.camera_status
    status = '打开' if camera_node.camera_status else '关闭'
    Bus.publish('message', f'摄像头已{status}')

@subscribe(camera_node, 'set_filter')
def set_filter(data):
    camera_node.filter = data['data']
    Bus.publish('message', f'滤镜已设置为【{data['name']}】')


@subscribe(camera_node, 'shoot_frame')
def shoot_frame(data):
    if camera_node.camera_status:
        Bus.publish('frame_to_save', camera_node.current_frame)
    else:
        Bus.publish('message', '请先打开摄像头')


###############################################图像保存节点#################################################

import datetime
from pathlib import Path

album_node = Node('Album')

@initialize(album_node)
def init():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    album_node.path = Path(config['save_path'])
    album_node.path.mkdir(exist_ok=True)



@subscribe(album_node, 'frame_to_save')
def handler(data):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    cv2.imwrite(album_node.path/f"{timestamp}.jpg", data)
    Bus.publish('message', f'{timestamp}.jpg 已保存')


gui_node.register()
camera_node.register()
album_node.register()
miniROS.run()