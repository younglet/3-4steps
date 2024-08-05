# 填充API Key与Secret Key

import requests
import json


headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
    }
def main():
    url = "https://aip.baidubce.com/oauth/2.0/token?client_id=【API Key】&client_secret=【Secret Key】&grant_type=client_credentials"
    payload = json.dumps("")

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")

  
  
if __name__ == '__main__':
    access_token = main()
    print(access_token)