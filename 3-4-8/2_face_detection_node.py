
from miniROS import *
################################################GUI节点#################################################

import json 
import easygui
import time



gui_node = Node('GUI')
@initialize(gui_node)
def init():
    gui_node.messages = [] 


@set_task(gui_node, loop=True, main=True)
def set_input():
    while gui_node.messages:
        message = gui_node.messages.pop(0)
        easygui.msgbox(message)

    choice = easygui.buttonbox('请选择操作', choices=['刷新状态', '开启（关闭）摄像头', '开启（关闭）人脸检测', ])

    if choice == '刷新状态':
        gui_node.node_continue()
    
    if choice == '开启（关闭）人脸检测':
        Bus.publish('set_face_detect_status', None)

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
    camera_node.height = camera_node.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
    camera_node.width = camera_node.camera.get(cv2.CAP_PROP_FRAME_WIDTH)    
    camera_node.current_frame = None
    camera_node.camera_status = False
    camera_node.face_bboxC = None



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

    camera_node.current_frame = frame
    if camera_node.face_bboxC:
        x_min = int(camera_node.face_bboxC.xmin * camera_node.width)
        y_min = int(camera_node.face_bboxC.ymin * camera_node.height)
        box_width = int(camera_node.face_bboxC.width * camera_node.width)
        box_height = int(camera_node.face_bboxC.height * camera_node.height)
        cv2.rectangle(frame, (x_min, y_min), (x_min + box_width, y_min + box_height), (0, 255, 0), 2)
    
    cv2.imshow('camera', frame)

@subscribe(camera_node, 'set_camera_status')
def set_camera_status(data):
    camera_node.camera_status =  not camera_node.camera_status
    status = '打开' if camera_node.camera_status else '关闭'
    Bus.publish('message', f'摄像头已{status}')

############################################### 人脸检测节点 #################################################
import mediapipe as mp
face_detect_node = Node('FaceDetect')
@initialize(face_detect_node)
def init():
    face_detect_node.face_detection = mp.solutions.face_detection.FaceDetection(
        model_selection = 0, min_detection_confidence = 0.5)
    face_detect_node.is_active = False

@subscribe(face_detect_node, 'set_face_detect_status')
def set_face_detect_status(data):
    face_detect_node.is_active = not face_detect_node.is_active
    status = '打开' if face_detect_node.is_active else '关闭'
    Bus.publish('message', f'人脸检测已{status}')

@subscribe(face_detect_node, 'camera_frame')
def process_frame(data):
    if not face_detect_node.is_active:
        return Bus.publish('face_bboxC', None)
    rgb_frame = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
    result = face_detect_node.face_detection.process(rgb_frame)
    if result.detections:
        bboxC = result.detections[0].location_data.relative_bounding_box
        Bus.publish('face_bboxC', bboxC)
    else:
        Bus.publish('face_bboxC', None)

gui_node.register()
camera_node.register()
face_detect_node.register()
miniROS.run()