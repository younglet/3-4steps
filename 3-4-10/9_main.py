from miniROS import *

"""
需要第三方库：tkinter, tkinterdnd2, Pillow, opencv-python, screeninfo, numpy
"""

####################################################代码功能注释##########################################################################################
# 此代码的功能如下： 运行后，会产生一个画布界面，在这个界面可以用鼠标进行绘画，画完之后可以生成视频，然后点击播放视频就可以在小电视的屏幕上进行播放                  #
#                  可以调节画笔和橡皮擦的粗细，右上角有一个当前帧的删除按钮，画布的左右两边有移动和添加画布的按钮                                               #
#                  在画布正下方可以设置每一个画布在视频中的持续时间，也可以直接拖入或者上传外部的图片进行编辑。                                                 #
#                  在播放视频旁边还有一个箭头可以直接选择视频进行播放，在右边还有一个循环播放的勾选，勾选以后会循环播放视频                                      #
#                  "添加页复制当前页"可以再添加页的时候复制当前页面，这样可以在创作相隔帧的时候避免重复劳动                                                    #
#                                                                                                                                                      #
########################################################################################################################################################


###############################################绘画表情节点#########################################
from drawing import DrawingApp, LOOPSTOP_FRAME
# 参数分别表示画布的尺寸，生成的视频的分辨率还有帧数
draw_node = Node('Draw', canvas_width=800, canvas_height=600, video_width=800, video_height=600, video_frame=30)

@initialize(draw_node)
def init():
    draw_node.darwapp = DrawingApp(canvas_width=draw_node.canvas_width, canvas_height=draw_node.canvas_height)
    # 设置点击“播放按钮”的钩子函数
    draw_node.darwapp.play_video_hook = draw_node.play_generate
    # 设置关闭按钮的钩子函数
    draw_node.darwapp.on_closing_hook = lambda :miniROS.stop()
    draw_node.orientation = None

# darwapp的run方法本身有无限循环，我们定义在最后一个实行
@set_task(draw_node, main=True, loop=False, index=-1)
def start_draw():
    draw_node.darwapp.run()
    
@add_method(draw_node)
def play_generate():
    if draw_node.orientation is not None:
        # 将视频生成器广播给'frame_generator'
        Bus.publish('frame_generator', draw_node.darwapp.video_generator(draw_node.orientation))
    
@subscribe(draw_node, 'orientation')
def set_orientation(orientation):
    draw_node.orientation = orientation
    
    
    
    
#####################################################cv2显示节点#######################################
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
        
@subscribe(display_node, 'frame_generator')
def handler(frame_generator):
    display_node.frame_generator = frame_generator
        
@subscribe(display_node, 'display_setting')
def handler(monitor):
    display_node.monitor = monitor # 在屏幕创建一个全屏窗口, monitor是窗口信息


#################################################显示屏设置节点###########################################
from screen import *

# device是屏幕序号，这里1是副屏的意思
# res_width,res_height设置的是屏幕的分辨率
# orientation指的是显示视频时候要旋转的角度
# orientaion取值有 NO_ROTATE，ROTATE_90，ROTATE_180，ROTATE_270 这里的旋转是顺时针
# orientaion参数的设置是因为有的屏幕装的方向有问题
screen_node = Node('Screen', device=1, res_width=800, res_height=600, orientation=ROTATE_180)

@initialize(screen_node)
def init():
    # 设置屏幕尺寸
    monitor = set_screen_size(device=screen_node.device, res_width=screen_node.res_width, res_height=screen_node.res_height)
    Bus.publish('orientation', screen_node.orientation)
    Bus.publish('display_setting', monitor)
    
    
    
#################################################注册要运行的节点###########################################
draw_node.register()
display_node.register()
screen_node.register()


# 系统开始运行
miniROS.run()   
    
    