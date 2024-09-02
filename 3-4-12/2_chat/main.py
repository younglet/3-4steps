from miniROS import *
from app import App


################################################天气查询节点建立############################################

gui_node = Node('GUI')

@initialize(gui_node)
def init():
    gui_node.app = App()
    gui_node.app.log('启动成功')
    gui_node.app.get_weather_hook = gui_node.get_weather
    gui_node.app.send_user_message_hook = gui_node.send_user_message

    
@set_task(gui_node, main=True)
def process():
    gui_node.app.run()

@add_method(gui_node)
def get_weather(city_name):
    Bus.publish('city', city_name)

@add_method(gui_node)
def send_user_message(message):
    if not message:
        return Bus.publish('start_chat', None)
    return Bus.publish('continue_chat', message)


@subscribe(gui_node, 'result')
def handler(data):
    gui_node.app.update_weather_result(data)


@subscribe(gui_node, 'message')
def handler(data):
    gui_node.app.update_bot_reply(data)


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



################################################提示词节点#################################################
import json
prompt_node = Node('Prompt')

@initialize(prompt_node)
def init():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    prompt_node.character = config['character']
    prompt_node.talk_manner = config['talk_manner']
    
@subscribe(prompt_node, 'start_chat')
def handler(data):
    prompt = f"请完全重置你自己的性格和说话方式，接下来我和你的对话, 请你的性格是：{prompt_node.character}，\
        你和我的对话方式是：{prompt_node.talk_manner}。回答必须限定60字以内。如果明白，用符合人设的10个字以内的回答回复。"
    Bus.publish('prompt', {'prompt':prompt, 'is_first':True})

@subscribe(prompt_node, 'continue_chat')
def handler(data):
    Bus.publish('prompt', {'prompt':data, 'is_first':False})
     
@subscribe(prompt_node, 'setting')
def handler(data):
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    with open('config.json', 'w', encoding='utf-8') as f:
        config['character'] = data['character']
        config['talk_manner'] = data['talk_manner']
        json.dump(config, f)
    Bus.publish('message','设置成功')
    prompt_node.character = data['character']
    prompt_node.talk_manner = data['talk_manner']


################################################大模型节点#################################################
import requests
import json

# 此处的 API_Key 和 Secrete_Key 可从教程https://developer.baidu.com/article/detail.html?id=1089328 自己执行获得
# 此处调用的是文心一言的大模型，此处需要自己充值一些，以防余额不足
LLM_node = Node('LLM')


@initialize(LLM_node)
def init():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    request_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={config['API_Key']}&client_secret={config['Secret_Key']}"
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    try:
        response = requests.request("POST", request_url, headers=headers, data=payload)
    except Exception as e:
        print(e)
    LLM_node.url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-4.0-turbo-8k?access_token=" + response.json().get("access_token")

    LLM_node.payload = {"messages":[]}
    
    
@subscribe(LLM_node, 'prompt')
def handler(data):
    if data['is_first']:
        LLM_node.payload = {"messages":[]}
    LLM_node.payload["messages"].append({
                "role": "user",
                "content": data['prompt']
            })

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", LLM_node.url, headers=headers, data=json.dumps(LLM_node.payload)).json()
    error=response.get('error_msg')
    
    if not error:
        answer=response.get('result')
        LLM_node.payload["messages"].append({
                    "role": "assistant",
                    "content": answer
                })
    else:
        answer = 'error: ' + error
        LLM_node.payload["messages"].pop()
    
    Bus.publish('message', answer)
    
    

gui_node.register()
weather_node.register()
prompt_node.register()
LLM_node.register()


miniROS.run()