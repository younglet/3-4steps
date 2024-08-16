
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

    choice = easygui.buttonbox('请选择操作', choices=['刷新状态', '开启（关闭）摄像头', '开启（关闭）人脸检测', '开启（关闭）手势检测'])

    if choice == '刷新状态':
        gui_node.node_continue()

    if choice == '开启（关闭）摄像头':
        Bus.publish('set_camera_status', None)
    
    if choice == '开启（关闭）手势检测':
        Bus.publish('set_hand_detect_status', None)

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
    camera_node.hand_detection = None

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

    # 绘制识别结果图形方法一： 在摄像头节点处理数据
    if camera_node.face_bboxC:
        x_min = int(camera_node.face_bboxC.xmin * camera_node.width)
        y_min = int(camera_node.face_bboxC.ymin * camera_node.height)
        box_width = int(camera_node.face_bboxC.width * camera_node.width)
        box_height = int(camera_node.face_bboxC.height * camera_node.height)
        cv2.rectangle(frame, (x_min, y_min), (x_min + box_width, y_min + box_height), (0, 255, 0), 2)
    
    # 绘制识别结果图形方法二： 调用识别节点封装的函数
    if camera_node.hand_detection:
        draw = camera_node.hand_detection['draw']
        land_marks = camera_node.hand_detection['landmarks']
        draw(frame, land_marks)
    
    cv2.imshow('camera', frame)

@subscribe(camera_node, 'set_camera_status')
def set_camera_status(data):
    camera_node.camera_status =  not camera_node.camera_status
    status = '打开' if camera_node.camera_status else '关闭'
    Bus.publish('message', f'摄像头已{status}')

@subscribe(camera_node, 'face_bboxC')
def get_face_bboxC(data):
    camera_node.face_bboxC = data

@subscribe(camera_node, 'hand_detection')
def get_hand_landmarks(data):
    camera_node.hand_detection = data


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


############################################### 手势检测节点 #################################################
import mediapipe as mp


hand_detect_node = Node('HandDetect')
@initialize(hand_detect_node)
def init():
    hand_detect_node.hand_detection = mp.solutions.hands.Hands(
                            static_image_mode=False,
                            max_num_hands=1,
                            min_detection_confidence=0.5,
                            min_tracking_confidence=0.5)
    hand_detect_node.is_active = False
    def draw_hand_landmarks(image, landmarks):
        mp.solutions.drawing_utils.draw_landmarks(
            image,
            landmarks,
            mp.solutions.hands.HAND_CONNECTIONS,
            )
    hand_detect_node.draw_hand_landmarks = draw_hand_landmarks

@subscribe(hand_detect_node, 'set_hand_detect_status')
def set_hand_detect_status(data):
    hand_detect_node.is_active = not hand_detect_node.is_active
    status = '打开' if hand_detect_node.is_active else '关闭'
    Bus.publish('message', f'手势检测已{status}')
    
@subscribe(hand_detect_node, 'camera_frame')
def process_frame(data):
    if not hand_detect_node.is_active:
        return Bus.publish('hand_detection', None)
    rgb_frame = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
    result = hand_detect_node.hand_detection.process(rgb_frame)
    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]
        Bus.publish('hand_detection', {
            'landmarks': hand_landmarks,
            'draw': hand_detect_node.draw_hand_landmarks,
        })
        
        # 检查食指是否抬起
        index_tip_y = hand_landmarks.landmark[8].y
        index_tip_x = hand_landmarks.landmark[8].x
        index_base_x = hand_landmarks.landmark[5].x

        thumb_tip_y = hand_landmarks.landmark[4].y
        middle_tip_y = hand_landmarks.landmark[12].y
        ring_tip_y = hand_landmarks.landmark[16].y
        pinky_tip_y = hand_landmarks.landmark[20].y
        
        # 检查食指是否是最高的，并且指尖和指根的X轴坐标差是否小于某一阈值（例如0.05）
        if index_tip_y < min(thumb_tip_y, middle_tip_y, ring_tip_y, pinky_tip_y) \
            and abs(index_tip_x - index_base_x) < 0.15:
            print('食指指抬起')
            Bus.publish('message', 'index_up')
        
    else:
        Bus.publish('hand_detection', None)
        


gui_node.register()
camera_node.register()
face_detect_node.register()
hand_detect_node.register()
miniROS.run()