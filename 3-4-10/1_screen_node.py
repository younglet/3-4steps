from miniROS import *


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

screen_node.register()
miniROS.run()