import json

# 读取json文件
with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    print(data)

# 写入json文件
data = {"name": "斯斯", "age": 14, "city": "上海"}
with open('data.json', 'w', encoding='utf-8') as file:
    json.dump(data, file)