from miniROS import *

"""
需要第三方库: mediapipe, opencv-python
"""

####################################################代码功能注释############################
# 此代码的功能如下： 运行程序后，机器人的摄像头会自动跟随人脸动                                #
# 节点运行顺序：                                                                           #
# mediapipe_node(生成生成器)->show_node(显示人脸并识别人脸位置)->servo_node(用PID进行跟随)    #
#                                                                                         #
###########################################################################################

###############################################面部识别检测节点#####################################
import mediapipe as mp
import cv2

mediapipe_node = Node('mediapipe', device=1, width=1280, height=960)

@initialize(mediapipe_node)
def init():
    mediapipe_node.cap = cv2.VideoCapture(mediapipe_node.device)
    mediapipe_node.cap.set(cv2.CAP_PROP_FRAME_WIDTH, mediapipe_node.width)
    mediapipe_node.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, mediapipe_node.height) 
    
    # 初始化MediaPipe人脸检测
    mediapipe_node.mp_face_detection = mp.solutions.face_detection
    mediapipe_node.mp_drawing = mp.solutions.drawing_utils

    # 设置人脸检测的配置
    mediapipe_node.face_detection = mediapipe_node.mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

    
    mediapipe_node.mp_hands = mp.solutions.hands
    mediapipe_node.hands =mediapipe_node.mp_hands.Hands(static_image_mode=False,
                            max_num_hands=1,
                            min_detection_confidence=0.5,
                            min_tracking_confidence=0.5)
    mediapipe_node.mp_drawing = mp.solutions.drawing_utils
    
    Bus.publish('frame_gen', mediapipe_node.generate_frame)
    
@add_method(mediapipe_node)
def generate_frame():
    while mediapipe_node.cap.isOpened():
        ret, frame = mediapipe_node.cap.read()
        
        if ret:
            frame_center_x = frame.shape[1] // 2  # 计算帧中心
            # 将BGR帧转换为RGB帧
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 使用MediaPipe进行人脸检测
            results = mediapipe_node.face_detection.process(frame_rgb)

            # 将帧转换回BGR颜色以用于OpenCV渲染
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            # 检查是否有人脸被检测到
            if results.detections:
                for detection in results.detections:
                    # 获取人脸的边界框
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                        int(bboxC.width * iw), int(bboxC.height * ih)
                    
                    # 绘制矩形框
                    cv2.rectangle(frame_bgr, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 255, 0), 2)

                    # 计算并绘制人脸中心位置
                    center_x, center_y = bbox[0] + bbox[2] // 2, bbox[1] + bbox[3] // 2
                    cv2.circle(frame_bgr, (center_x, center_y), 5, (0, 0, 255), -1)
                    yield (center_x, frame_center_x, frame_bgr)
            else:
                yield (None, frame_center_x, frame_bgr)
        else:
            yield None, None, None
    yield None, None, None


#####################################################cv2显示节点###############################
import cv2
import time

display_node = Node('display')

@initialize(display_node)
def init():
    # 帧生成器
    display_node.frame_generator = None
    Bus.publish('camera_set', 'mediapipe_hand')


@set_task(display_node, loop=True)
def process_camera():
    while not display_node.frame_generator:
        time.sleep(0.001)
    prev_frame_generator = display_node.frame_generator
    for info in display_node.frame_generator():
        center_x, frame_center_x, frame = info[0], info[1], info[2]
        if frame is not None:
            cv2.imshow('mediapipe', frame)
            Bus.publish('move_to_face', (center_x, frame_center_x))
            # 按下q就直接退出显示
            key = cv2.waitKey(1) & 0xff
            if  key == ord('q') or key == ord('Q'):
                display_node.frame_generator = None
                cv2.destroyAllWindows()
                miniROS.stop()
                break
            # 如果相机生成器变化就跳出重新显示
            if prev_frame_generator != display_node.frame_generator:
                break
        else:
            display_node.frame_generator = None
            print('显示失败')
            cv2.destroyAllWindows()
            break
    
    
        
@subscribe(display_node, 'frame_gen')
def handler(frame_generator):
    if frame_generator is not None:
        display_node.frame_generator = frame_generator
        
        
################################################设定舵机节点#################################################
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

@add_method(servo_node)
def update_servo(center_x, frame_center_x):
    error = frame_center_x - center_x  # 计算偏差
    # 更新误差积分
    if 0 < servo_node.angle < 240:
        servo_node.integral += error
    else:
        servo_node.integral = 0  # 或者使用较小的积分值或按比例减少
    # 计算误差微分
    derivative = error - servo_node.last_error
    # 计算角度变化
    angle_delta = (servo_node.Kp * error) + (servo_node.Ki * servo_node.integral) + (servo_node.Kd * derivative)
    # 更新舵机角度
    new_angle = max(min(servo_node.angle + angle_delta, 240), 0)
    # 计算移动到新角度所需的时间
    angle_change = abs(angle_delta)
    time_to_move = angle_change / servo_node.angular_velocity
    # 发送新的角度和时间到舵机
    servo_node.servo.set_angle_time(new_angle, time_to_move)
    # 更新当前角度和上一次误差
    servo_node.angle = new_angle
    servo_node.last_error = error
        

@subscribe(servo_node, 'move_to_face')
def handler(pos):
    center_x, frame_center_x = pos[0], pos[1]
    if center_x is not None:
        servo_node.update_servo(center_x, frame_center_x)
           
        
        
#################################################注册要运行的节点###########################################
mediapipe_node.register()
display_node.register()
servo_node.register()



# 系统开始运行
miniROS.run()   