import json

# 读取json文件
with open('data.json', 'r') as file:
    data = json.load(file)
    print(data)

# 写入json文件
data = {"name": "斯斯", "age": 14, "city": "上海"}
with open('data.json', 'w') as file:
    json.dump(data, file)