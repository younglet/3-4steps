from miniROS import *

"""
需要第三方库：无
"""

####################################################代码功能注释#########################################
# 此代码的功能如下：运行后在终端中随便输入字符，然后回车；如果是整数会扩大两倍后输出；如果是小数，缩小两倍输出； #
#                 如果是不是数字，就前后分别添加“*****”和“####”再输出                                      #
#节点运行顺序：input_node(输入字符)->relay_node(处理字符)->console_node(显示字符)                          #
#                     ↑ <———————————————————————————————————— ↓                                        #
#                                                                                                      #
########################################################################################################



################################################输入节点的建立###############################################
input_node = Node('Input')

# 定义input_node节点的初始化函数，如节点不需要初始化，就可以不设定,在主线程运行
# 此装饰器有一个参数：要被装饰的节点实例
@initialize(input_node)
def init():
    pass

# 定义input_node节点设置函数，如节点不需要设置，就可以不设定
# 此装饰器有四个参数：
# 要被装饰的节点实例
# main参数，True为在主线程运行此节点set_task函数，False为在线程中运行，默认为False
# loop参数，是否需要无限循环
# index参数，设置节点set_task函数执行的顺序，默认为None代表无顺序要求。例如，0代表第一个执行，1代表第二个执行，-1代表最后一个
@set_task(input_node, loop=True)
def set_input():
    data = input('请输入：')
    # 往订阅了'data'主题的节点广播数据
    Bus.publish('data', data)
    

# 定义input_node节点退出时要执行的函数，如节点不需要设置停止行为，就可以不设定
# 此装饰器有一个参数：要被装饰的节点实例
@on_stop(input_node)
def stop():
    pass


################################################中继处理节点的建立###############################################

# 中继节点的作用是将input_node接收的数据进行处理，这个处理根据不同的数据处理的方法也不一样
relay_node = Node('Relay')

# 定义relay_node节点对'data'主题广播的数据进行处理
# 装饰器有两个参数：要被装饰的节点实例， 和订阅的主题
@subscribe(relay_node, 'data')
def handler(data):
    relay_node.data = data
    relay_node.data_handle()
    Bus.publish('console', relay_node.data)
    

# 定义relay_node节点特有的类方法 此装饰器有一个参数：要被装饰的节点实例
# 被修饰的函数会成为relay_node的方法属性
@add_method(relay_node)
def data_handle():
    try:
        # 尝试转换为整数
        converted_number = int(relay_node.data)
        # 整数我们将扩大两倍
        relay_node.data = 2*converted_number
    except ValueError:
        try:
            # 如果整数转换失败，尝试转换为浮点数
            converted_number = float(relay_node.data)
            # 浮点数我们将缩小两倍
            relay_node.data = converted_number/2
        except ValueError:
            # 如果不是数字就加上前后缀
            relay_node.data = '****'+relay_node.data+'####'


################################################打印输出节点的建立###############################################

console_node = Node('Console')

# 订阅'console'主题并处理信息
@subscribe(console_node, 'console')
def handler(data):
    print(data)
    
    
#################################################注册要运行的节点###########################################
input_node.register()
relay_node.register()
console_node.register()

# 系统开始运行
miniROS.run()