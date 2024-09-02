from miniROS import *
from app import App


################################################天气查询节点建立############################################

gui_node = Node('GUI')

@initialize(gui_node)
def init():
    gui_node.app = App()
    gui_node.app.log('启动成功')
    gui_node.app.get_weather_hook = gui_node.get_weather

    
@set_task(gui_node, main=True)
def process():
    gui_node.app.run()

@add_method(gui_node)
def get_weather(city_name):
    Bus.publish('city', city_name)

@subscribe(gui_node, 'result')
def handler(data):
    print(data)
    gui_node.app.update_weather_result(data)



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
            weather = f"天气{info},\n最高温{max_temp}度,\n最低温{min_temp}度,\n湿度{humd}, \n空气质量{air_quality}"
            line = f'{parent_city}{city}：{weather}  \n【更新于{time}】'
            Bus.publish('result', line)
        
        else:
            Bus.publish('result', f"获取天气数据失败，状态码：{weather_data['status']}，消息：{weather_data['message']}")
    except requests.HTTPError as http_err:
        Bus.publish('result', f"HTTP error occurred: {http_err}")  # HTTP错误响应
    except Exception as err:
        Bus.publish('result', f"Other error occurred: {err}")  # 其他错误，如网络连接问题


    

gui_node.register()
weather_node.register()

miniROS.run()