import requests

url = 'http://t.weather.itboy.net/api/weather/city/101020100'

response = requests.get(url) # 发送请求并获取响应

response.status_code # 响应状态码
response.text # 响应的文本
response.json() # 响应文本解析为字典


weather_data = response.json()

# 很多服务器会在数据中添加一个status字段来表示响应状态码，和response.status_code功能相同
# response.status_code 为200 表示服务器成功发送给你发回了数据，但是不保证数据是正确的
# 而响应数据中status如果是200 基本可以确保x数据是正确的
if weather_data['status'] == 200:
    # 获取城市信息
    parent_city = ''
    if 'parent' in weather_data['cityInfo']:
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

    print(line)