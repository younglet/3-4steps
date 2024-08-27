from miniROS import *
from Drawing import DrawingApp, LOOPSTOP_FRAME
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
        # 将视频生成器广播给'frame_gen'
        Bus.publish('frame_gen', draw_node.darwapp.video_generator(draw_node.orientation))
    
@subscribe(draw_node, 'orientation')
def set_orientation(orientation):
    draw_node.orientation = orientation
    
draw_node.register()
miniROS.run()