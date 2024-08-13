import cv2
import numpy as np
from miniROS import *


def init():
    camera_node.camera = cv2.VideoCapture(0)
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
    cv2.imshow('camera', frame)

@subscribe(camera_node, 'set_camera_status')
def set_camera_status(data):
    camera_node.camera_status =  not camera_node.camera_status
    status = '打开' if camera_node.camera_status else '关闭'
    Bus.publish('message', f'摄像头已{status}')

@subscribe(camera_node, 'set_filter')
def set_filter(data):
    camera_node.filter = data['data']
    Bus.publish('message', f'滤镜已设置为【{data["name"]}】')