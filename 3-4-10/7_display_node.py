from miniROS import *
    
import cv2
import time

display_node = Node('display')

@initialize(display_node)
def init():
    # 帧生成器
    display_node.frame_generator = None
    display_node.monitor = None

@set_task(display_node, loop=True)
def process():
    while not display_node.frame_generator:
        time.sleep(0.001)
    prev_frame_generator = display_node.frame_generator
    # display_node.gen = display_node.frame_generator()
    
    while display_node.monitor is None:
        time.sleep(0.001)
    cv2.namedWindow('display', cv2.WND_PROP_FULLSCREEN)
    cv2.moveWindow('display', display_node.monitor.x, display_node.monitor.y)
    cv2.setWindowProperty('display', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)   
    
    for frame in display_node.frame_generator():
        if frame is not None and frame is not LOOPSTOP_FRAME:
            cv2.imshow('display', frame)
            # 按下q就直接退出显示
            key = cv2.waitKey(1) & 0xff
            if  key == ord('q') or key == ord('Q'):
                display_node.frame_generator = None
                cv2.destroyAllWindows()
                break
            # 如果相机生成器变化就跳出重新显示
            if prev_frame_generator != display_node.frame_generator:
                break
        elif frame is LOOPSTOP_FRAME:
            if prev_frame_generator != display_node.frame_generator:
                break
        elif frame is None:
            display_node.frame_generator = None
            print('显示失败')
            cv2.destroyAllWindows()
            break
    
    
        
@subscribe(display_node, 'frame_gen')
def handler(frame_generator):
    if frame_generator is not None:
        display_node.frame_generator = frame_generator
        
@subscribe(display_node, 'display_setting')
def handler(monitor):
    # 在屏幕创建一个全屏窗口, monitor是窗口信息
    display_node.monitor = monitor


display_node.register()
miniROS.run()