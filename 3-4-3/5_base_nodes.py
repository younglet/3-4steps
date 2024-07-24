from miniROS import *
import time


input_node = Node('Input')

@set_task(input_node, loop=True)
def set_input():
    city_name = input('请输入城市名称：')
    # 往订阅了'data'主题的节点广播数据
    Bus.publish('city', city_name )
    time.sleep(2) # 延迟2秒
    
    

weather_node = Node('Weather')
@subscribe(weather_node, 'city')
def handler(data):
    Bus.publish('result', data + '的天气是：晴天')  # 模拟天气

console_node = Node('Console')
# 订阅Console 节点的 result 主题并处理信息
@subscribe(console_node, 'result')
def handler(data):
    print(data)


# 注册所有节点
input_node.register()
weather_node.register()
console_node.register()

# 系统开始运行
miniROS.run()