from miniROS import *
import cv2
import time

display_node = Node('display')

@initialize(display_node)
def init():
    display_node.frame_generator = None  # 帧生成器
    display_node.monitor = None

@set_task(display_node, loop=True)
def process():
    if not display_node.frame_generator or display_node.monitor is None:
        display_node.node_continue()

    prev_frame_generator = display_node.frame_generator
    cv2.namedWindow('display', cv2.WND_PROP_FULLSCREEN)
    cv2.moveWindow('display', display_node.monitor.x, display_node.monitor.y)
    cv2.setWindowProperty('display', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)   
    
    for frame in display_node.frame_generator():
        if frame is None:
            display_node.frame_generator = None
            cv2.destroyAllWindows()
            break

        if frame is LOOPSTOP_FRAME:
            break

        if prev_frame_generator != display_node.frame_generator:
            break

        if cv2.waitKey(1) == ord('q'):
            display_node.frame_generator = None
            cv2.destroyAllWindows()
            break

        cv2.imshow('display', frame)
        
@subscribe(display_node, 'frame_gen')
def handler(frame_generator):
    display_node.frame_generator = frame_generator
        
@subscribe(display_node, 'display_setting')
def handler(monitor):
    display_node.monitor = monitor # 在屏幕创建一个全屏窗口, monitor是窗口信息


display_node.register()
miniROS.run()