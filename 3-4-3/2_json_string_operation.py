import json

# json字符串转字典
json_string = '{"name": "斯斯", "age": 14, "city": "上海"}'
data = json.loads(json_string)
print(data)

# 字典转json字符串
data = {"name": "斯斯", "age": 14, "city": "上海"}
json_string = json.dumps(data)
print(json_string)