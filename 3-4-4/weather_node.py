from miniROS import *
import json
import requests


weather_node = Node('weather')

@initialize(weather_node)
def init():
    # 设置API URL
    weather_node.base_weather_url = "http://t.weather.itboy.net/api/weather/city/{}"

    with open('citycode.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        weather_node.city_dict = {item['city_name']: item['city_code'] for item in data if item['city_code']}
    
    Bus.publish('message', '天气节点初始化完成')

@add_method(weather_node)
def query(data):
    # 获取查询url
    if city_code:=weather_node.city_dict.get(data):
        url = weather_node.base_weather_url.format(city_code)
    else:
        Bus.publish('message', '城市不存在，无法查询')
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
            message = line
        
        else:
            message =  f"获取天气数据失败，状态码：{weather_data['status']}，消息：{weather_data['message']}"
    except requests.HTTPError as http_err:
        message = f"HTTP error occurred: {http_err}"
    except Exception as err:
        message = f"Other error occurred: {err}"
    Bus.publish('message', message)