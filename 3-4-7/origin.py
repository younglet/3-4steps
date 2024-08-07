from miniROS import *

"""
需要第三方库：opencv-python，fractions，numpy
"""

####################################################代码功能注释##################################################################  
# 此代码的功能如下： 运行后会显示摄像头画面，默认是是原图。在聊天框内可以输入原图，高斯模糊，边缘检测，锐化，输入这些摄像头就会      #
#                    显示相应的滤镜，其中YOLO是进行物体检测。也可以在聊天框输入卷积核，例如[1.2, 2,3;4,5,6]或 [1/12 2 3;4 5/16 6]或   #
#                    单独一个数字，比如2，就可以根据输入的卷积核对摄像头进行滤镜处理                                                 #
# 节点运行顺序：input_node(输入信息)->camera_node(设置新的摄像头生成器，产生不同的滤镜效果)->show_camera(使用新的生成器显示新滤镜)     #
#                     ↑ <———————————————————————————————————————————————————————————————————————————————— ↓                    #
# 要注意知识点: 生成器的概念，卷积核的概念                                                                                        #
#                                                                                                                              #
################################################################################################################################




############################################创建输入节点#######################################
input_node = Node('Input')

@set_task(input_node, loop=True)
def set_input():
    data = input("请输入相机选项，选项有[原图，高斯模糊，边缘检测，锐化]，也可以自定义输出卷积核，格式如[1,2,3;4,5,6]或 [1 2 3;4 5 6]:\n")
    # 往订阅了'camera'主题的节点广播数据
    Bus.publish('camera_set', data)


#####################################################摄像头显示节点###############################
import cv2
import time

display_node = Node('display')

@initialize(display_node)
def init():
    # 帧生成器
    display_node.frame_generator = None
    Bus.publish('camera_set', '原图')


@set_task(display_node, loop=True)
def process_camera():
    while not display_node.frame_generator:
        time.sleep(0.001)
    prev_frame_generator = display_node.frame_generator
    for frame in display_node.frame_generator():
        if frame is not None:
            cv2.imshow('camera', frame)
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

######################################################摄像头设置节点######################################
import cv2
import numpy as np
from fractions import Fraction


camera_node = Node('camera', device=0, width=1280, height=960)

@initialize(camera_node)
def init():
    camera_node.cap = cv2.VideoCapture(camera_node.device)
    camera_node.cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_node.width)
    camera_node.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_node.height) 
    camera_node.filter = None

@add_method(camera_node)
def frame_generator(frame_type):
    def parse_matrix_input(input_str):
        try:
            # 此函数用来判断一个字符串是否为矩阵形式，如果是就转换为numpy矩阵作为卷积核
            # 去除字符串两端的空格和方括号
            input_str = input_str.strip().strip('[]')
            
            # 按照分号来分割不同的行
            rows = input_str.split(';')
            
            # 对于每一行，再按照逗号或空格来分割元素
            matrix = []
            for row in rows:
                # 使用逗号或空格分割元素，同时过滤掉空字符串
                # 使用 Fraction 来处理分数输入，并将其转换为浮点数
                elements = [float(Fraction(x)) for x in row.replace(',', ' ').split() if x]
                matrix.append(elements)
            # 转换成 NumPy 数组
            return np.array(matrix)
        except Exception as e:
            return None
    
    camera_node.filter = parse_matrix_input(frame_type)
    # 先判断frame_type的输入正确与否
    if not (frame_type in ['原图', '高斯模糊', '边缘检测', '锐化'] or camera_node.filter is not None):
        print('输入格式不正确请重新输入')
        return None
    elif frame_type == '高斯模糊':
        camera_node.filter = np.array([
                        [1/273, 4/273, 7/273, 4/273, 1/273],
                        [4/273, 16/273, 26/273, 16/273, 4/273],
                        [7/273, 26/273, 41/273, 26/273, 7/273],
                        [4/273, 16/273, 26/273, 16/273, 4/273],
                        [1/273, 4/273, 7/273, 4/273, 1/273]
                    ])
    elif frame_type == '边缘检测':
        camera_node.filter = np.array([
                        [ 0,  1,  0],
                        [ 1, -4,  1],
                        [ 0,  1,  0]
                    ])
    elif frame_type == '锐化':
        camera_node.filter =  np.array([
                        [ 0,  1,  0],
                        [ 1, -4,  1],
                        [ 0,  1,  0]
                    ])
    elif frame_type == '原图':
        camera_node.filter = None

    # 根据frame_type生成不同的帧生成器
    def generator():
        while camera_node.cap.isOpened():
            ret, frame = camera_node.cap.read()
            if ret:
                if camera_node.filter is not None:
                    frame = cv2.filter2D(frame, -1, camera_node.filter)
                yield frame
            else:
                camera_node.cap.release()
                yield None
        camera_node.cap.release()
        yield None
            
    return generator

@subscribe(camera_node, 'camera_set')
def handler(data):
    Bus.publish('frame_gen', camera_node.frame_generator(data))
    
#################################################注册要运行的节点###########################################
input_node.register()
display_node.register()
camera_node.register()

# 系统开始运行
miniROS.run()  
    


    
        
        
    
        
    