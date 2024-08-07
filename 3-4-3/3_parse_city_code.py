import json

with open('citycode.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 方法一：遍历
city_dict = {}
for item in data:
    if item['city_code']:
        city_dict[item['city_name']] = item['city_code']
print(city_dict)

# 方法二：列表推导式
city_dict = {item['city_name']: item['city_code'] for item in data if item['city_code']}
print(city_dict)