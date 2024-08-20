
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

    choice = easygui.buttonbox('请选择操作', choices=['刷新状态', '开启（关闭）摄像头', '开启（关闭）人脸检测', 'PID参数设置'])

    if choice == '刷新状态':
        gui_node.node_continue()

    if choice == '开启（关闭）摄像头':
        Bus.publish('set_camera_status', None)

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
    

############################################### 舵机节点 #################################################
from servo import ServoController

servo_node = Node('Servo')

@initialize(servo_node)
def init():
    servo_node.servo = ServoController()
    servo_node.angle = servo_node.servo.read_angle()
    # 角速度, 单位度每秒
    servo_node.angular_velocity = 120
    # PID参数
    servo_node.Kp = 0.01
    servo_node.Ki = 0.00005  # 积分增益
    servo_node.Kd = 0.005  # 微分增益
    servo_node.last_error = 0  # 上一次的误差，用于微分计算
    servo_node.integral = 0  # 误差的积分

@subscribe(servo_node, 'face_bboxC')
def update_servo(face_bboxC):
    if not face_bboxC:
        return
    error = (face_bboxC.xmin + face_bboxC.width ) / 2 - 0.5
    if 0 < servo_node.angle < 240:
        servo_node.integral += error
    else:
        servo_node.integral = 0
    
    derivative = error - servo_node.last_error

    angle_delta = (servo_node.Kp * error) + (servo_node.Ki * servo_node.integral) + (servo_node.Kd * derivative)
    # 更新舵机角度
    new_angle = max(min(servo_node.angle + angle_delta, 240), 0)
    angle_change = abs(angle_delta)
    time_to_move = angle_change / servo_node.angular_velocity
    # 发送新的角度和时间到舵机
    servo_node.servo.set_angle_time(new_angle, time_to_move)
    # 更新当前角度和上一次误差
    servo_node.angle = new_angle
    servo_node.last_error = error




###############################################PID控制节点 #################################################
class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.last_error = 0
        self.integral = 0

    def update(self, error, dt):
        self.integral += error * dt
        derivative = (error - self.last_error) / dt
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.last_error = error
        return output

