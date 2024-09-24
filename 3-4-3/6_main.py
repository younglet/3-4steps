from miniROS import *
import time
"""
需要第三方库：requests，
"""

####################################################代码功能注释#########################################
# 此代码的功能如下：运行后在终端中随便输入城市名字，然后回车；终端会打印出对应城市当天的天气情况               #                                  
# 节点运行顺序：input_node(输入城市)->weather_node(信息查询)->console_node(输出信息)                      #                               
#                 ↑ <———————————————————————————————————————————————— ↓                                #          
#                                                                                                      #
########################################################################################################



################################################输入节点的建立###############################################
input_node = Node('Input')

@set_task(input_node, loop=True)
def set_input():
    city_name = input('请输入城市名称：')
    # 往订阅了'data'主题的节点广播数据
    Bus.publish('city', city_name )
    time.sleep(2)
    
    

################################################天气查询节点建立############################################
import requests
import json

weather_node = Node('weather')

@initialize(weather_node)
def init():
    # 设置API URL
    weather_node.base_weather_url = "http://t.weather.itboy.net/api/weather/city/{}"

    with open('citycode.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        weather_node.city_dict = {item['city_name']: item['city_code'] for item in data if item['city_code']}

@subscribe(weather_node, 'city')
def handler(data):
    # 获取查询url
    if city_code:=weather_node.city_dict.get(data):
        url = weather_node.base_weather_url.format(city_code)
    else:
        Bus.publish('result', '城市不存在，无法查询')
        return
    try:
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功

        # 将JSON响应解析为字典
        weather_data = response.json()
        # 检查API返回是否成功
        if weather_data['status'] == 200:
            
            # 获取城市信息
            parent_city = ''
            if weather_data['cityInfo']['parent']  not in weather_data['cityInfo']['city']:
                parent_city = weather_data['cityInfo']['parent']
            city = weather_data['cityInfo']['city']

            # 获取天气信息
            info = weather_data['data']['forecast'][0]['type']
            max_temp = weather_data['data']['forecast'][0]['high'][:-1]
            min_temp = weather_data['data']['forecast'][0]['low'][:-1]
            humd = weather_data['data']['shidu']
            air_quality = weather_data['data']['quality']

            # 获取日期
            date = weather_data['date']
            time = f"{date[0:4]}年{date[4:6]}月{date[6:]}日"
            
            # 构建完整天气信息
            weather = f"天气{info}, 最高温{max_temp}度, 最低温{min_temp}度, 湿度{humd}, 空气质量{air_quality}"
            line = f'{parent_city}{city}：{weather}  【更新于{time}】'
            Bus.publish('result', line)
        
        else:
            Bus.publish('result', f"获取天气数据失败，状态码：{weather_data['status']}，消息：{weather_data['message']}")
    except requests.HTTPError as http_err:
        Bus.publish('result', f"HTTP error occurred: {http_err}")  # HTTP错误响应
    except Exception as err:
        Bus.publish('result', f"Other error occurred: {err}")  # 其他错误，如网络连接问题



################################################打印输出节点的建立###############################################

console_node = Node('Console')

# 订阅Console 节点的 result 主题并处理信息
@subscribe(console_node, 'result')
def handler(data):
    print(data)

 
#################################################注册要运行的节点###########################################
input_node.register()
weather_node.register()
console_node.register()

# 系统开始运行
miniROS.run()   