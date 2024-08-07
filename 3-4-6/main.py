from miniROS import *
"""
需要第三方库：easygui，requests，sounddevice，scipy，numpy，assemblyai，pyttsx3
"""

####################################################代码功能注释############################################################
# 此代码的功能如下： 运行后会有一个交互界面，按下“开始录音”，就可以开始对麦克风说话，再按下“结束录音”，即可将录音                   #
#                   保存, 保存后会调用assemblyai库进行语音转文字，之后这个文字会通过api发到大模型，之后接收到                    #
#                    返回的文字消息，会将这个消息通过pyttsx3库进行文字转语音通过扬声器播报出来                                  #               
# 节点运行顺序：gui_node(开始录音)->record_node(进行录音)->STT_node(进行语音转文字)->LLM_node(大模型交互)->TTS_node(文字转语音) #                                    
#                      ↑              gui_node(结束录音)↑                                                   ↓              #
#                      ↑ <———————————————————————————————————————————————————————————————————————————————— ↓              #
#                                                                                                                         #
###########################################################################################################################


############################################创建gui节点###############################
import easygui

# 用于生产gui界面控制开始和结束录音
gui_node = Node('gui')

@initialize(gui_node)
def init():
    gui_node.button_text = '开始录音'

@set_task(gui_node, loop=True)
def setup_gui():
    response = easygui.buttonbox("", choices=[gui_node.button_text]) 
    if response=='开始录音':
        Bus.publish('record_voice', True)
        gui_node.button_text = '结束录音'
    elif response=='结束录音':
        Bus.publish('record_voice', False)
        gui_node.button_text = '开始录音'
    # 点击了×
    elif response is None:
        if gui_node.button_text == '结束录音':
            Bus.publish('record_voice', False)
        gui_node.node_break()
        
################################################麦克风录音节点##################################
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import time

record_node = Node('record', fs=44100, filename='record.wav')

@initialize(record_node)
def init():
    record_node.is_recording = False

@set_task(record_node, loop=True)
def setup_record():
    # 等待开始录音
    while not record_node.is_recording:
        time.sleep(0.01)
    # 初始化录音缓存
    recording = []
    
    # 开始录音
    try:
        with sd.InputStream(samplerate=record_node.fs, channels=2, dtype='float32') as stream:
            while record_node.is_recording:
                data, _ = stream.read(1024)
                recording.append(data)
    except Exception as e:
        print(e)
    # 录音结束后处理和保存文件
    recording_array = np.concatenate(recording, axis=0)  # 合并数组
    wav_data = np.int16(recording_array / np.max(np.abs(recording_array)) * 32767)
    wav.write(record_node.filename, record_node.fs, wav_data)
    Bus.publish('STT', record_node.filename)

@subscribe(record_node, 'record_voice')
def handle(isstart):
    record_node.is_recording = isstart
    
    

###################################################语音转文字节点#########################################
import assemblyai as aai

STT_node = Node('STT')

@initialize(STT_node)
def init():
    # 此处的密钥需要自己登陆网址https://www.assemblyai.com/，注册即可获得，免费使用
    aai.settings.api_key = "59057d149d6a468b84b94a65ed646f7a"
    STT_node.config = aai.TranscriptionConfig(language_code='zh')
    STT_node.transcriber = aai.Transcriber()
    
@subscribe(STT_node, 'STT')
def handler(filename):
    # 通过assemblyai库将语音转文字
    transcript = STT_node.transcriber.transcribe(filename, config=STT_node.config)
    if transcript.status == aai.TranscriptStatus.error:
        print(transcript.error)
    else:
        print(transcript.text)
        Bus.publish('LLM', transcript.text)
    

################################################大模型节点#################################################
import requests
import json

# 此处的 API_Key 和 Secrete_Key 可从教程https://developer.baidu.com/article/detail.html?id=1089328 自己执行获得
# 此处调用的是文心一言的大模型，此处需要自己充值一些，以防余额不足
LLM_node = Node('LLM', API_Key='eC744Ly7FlJsGCKZRpTN1huz', Secrete_Key='VFTz1SXJqLD44MAVrnzneg3tNDk4450n')


@initialize(LLM_node)
def init():
    request_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={LLM_node.API_Key}&client_secret={LLM_node.Secrete_Key}"
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
    
    
@subscribe(LLM_node, 'LLM')
def handler(text):
    LLM_node.payload["messages"].append({
                "role": "user",
                "content": text
            })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", LLM_node.url, headers=headers, data=json.dumps(LLM_node.payload)).json()
    
    answer=response.get('error_msg')
    
    if not answer:
        answer=response.get('result')
        LLM_node.payload["messages"].append({
                    "role": "assistant",
                    "content": answer
                })
    else:
        answer = 'error: ' + answer
        LLM_node.payload["messages"].pop()
    
    Bus.publish('answer', answer)
    
###################################################文字转语音节点########################################
import pyttsx3

TTS_node = Node('TTS')
    
@subscribe(TTS_node, 'answer')
def handler(answer):
    print(answer)
    engine = pyttsx3.init()
    rate = engine.getProperty('rate') 
    engine.setProperty('rate', rate+50)
    engine.say(answer)
    engine.runAndWait()
    
    
#################################################注册要运行的节点###########################################
gui_node.register()
record_node.register()
STT_node.register()
LLM_node.register()
TTS_node.register()


# 系统开始运行
miniROS.run()   









    