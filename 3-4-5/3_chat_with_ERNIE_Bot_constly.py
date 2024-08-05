# 填充API Key与Secret Key

import requests
import json


headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
    }

def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token?client_id=【API Key】&client_secret=【Secret Key】&grant_type=client_credentials"
    payload = json.dumps("")
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")

LLM_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-4.0-turbo-8k?access_token=" + get_access_token()

payload = {'messages': []}


while True:
    question = input("请输入问题（输入'exit'退出对话）：")
    if question.lower() == 'exit':
        break
    payload['messages'].append({'role': 'user', 'content': question})
    response = requests.request("POST", LLM_url, headers=headers, data=json.dumps(payload)).json()
    print("ERNIE Bot: ", response['result'])
    payload['messages'].append({'role': 'assistant', 'content': response['result']})