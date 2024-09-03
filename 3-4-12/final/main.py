from miniROS import *

"""
需要第三方库：tkinter, tkinterdnd2, Pillow, opencv-python, screeninfo, numpy, mediapipe, requests, assemblyai, pyttsx3, sounddevice, scipy, ultralytics, fractions
"""

####################################################代码功能注释#########################################################################################
# 此代码的功能如下： 现在一共有四个界面，第一个界面：                                                                                                      #
#                      运行后，会产生一个画布界面，在这个界面可以用鼠标进行绘画，画完之后可以生成视频，然后点击播放视频就可以在小电视的屏幕上进行播放             #
#                      可以调节画笔和橡皮擦的粗细，右上角有一个当前帧的删除按钮，画布的左右两边有移动和添加画布的按钮                                          #
#                      在画布正下方可以设置每一个画布在视频中的持续时间，也可以直接拖入或者上传外部的图片进行编辑。                                            #
#                      在播放视频旁边还有一个箭头可以直接选择视频进行播放，在右边还有一个循环播放的勾选，勾选以后会循环播放视频                                 #
#                      "添加页复制当前页"可以再添加页的时候复制当前页面，这样可以在创作相隔帧的时候避免重复劳动                                               #
#                 第二个界面                                                                                                                           # 
#                       可以选择打开或关闭摄像头，可以设置不同的视频滤镜效果，也可以选择进行人脸追踪，还可以自定义卷积核                                       #
#                 第三个界面                                                                                                                           #
#                       可以自定义AI的人设，留白直接点击确定就是跳过设计人设                                                                               #
#                       在对话界面中，有“重置人设”的按钮，点击会回到人设设置界面；有“录音”的按钮，可以通过录音来与AI对话；有"语音"选项，可以选择AI是否要发出语音  #
#                       也可以直接选择在聊天框打字，回车输入，与AI进行对话                                                                                 #
#                 第四个界面                                                                                                                            #
#                       天气查询界面，可以直接在聊天框输入要查询的天气，会有文字信息和语音播报                                                               #
#                                                                                                                                                      #
#                                                                                                                                                      #
########################################################################################################################################################


###############################################APP节点#########################################
from UltimateApp import *

# 参数分别表示画布的尺寸，生成的视频的分辨率还有帧数
APP_node = Node('Draw', canvas_width=800, canvas_height=600, video_width=800, video_height=600, video_frame=30)

@initialize(APP_node)
def init():
    APP_node.app = UltimateApp(device=0, canvas_width=APP_node.canvas_width, canvas_height=APP_node.canvas_height, 
                                   video_width=APP_node.video_width, video_height=APP_node.video_height, video_frame=APP_node.video_frame)
    # 设置点击“播放按钮”的钩子函数
    APP_node.app.play_video_hook = APP_node.play_generate
    # 设置点击摄像头设置中的按钮的钩子函数
    APP_node.app.camera_state["hook"] = APP_node.play_generate
    # 设置关闭按钮的钩子函数
    APP_node.app.on_closing_hook = lambda :miniROS.stop()
    # 设置天气设置中的文本框的钩子函数
    APP_node.app.weather_state["hook"] = APP_node.weather_check
    # 设置AI功能的钩子函数
    APP_node.app.ai_state["hook"] = APP_node.ask_ai
    # 设置录音功能的钩子函数
    APP_node.app.record_hook = lambda is_start: Bus.publish("record_voice", is_start)
    
    APP_node.orientation = None
    # 判断是否有剩余正在播放
    APP_node.is_saying = False

# darwapp的run方法本身有无限循环，我们定义在最后一个实行
@set_task(APP_node, main=True, loop=False, index=-1)
def start_draw():
    APP_node.app.run()
    
@add_method(APP_node)
def play_generate():
    if APP_node.orientation is not None:
        # 将视频生成器广播给'frame_gen'
        Bus.publish('frame_gen', APP_node.app.video_generator(APP_node.orientation))
    
@add_method(APP_node)
def weather_check(city):
    if city != "":
        Bus.publish('city', city)   
        
@add_method(APP_node)
def ask_ai(ai_state):
    # ai_state["chat_mode"]为False代表在设置人设阶段
    if not ai_state["chat_mode"] and (ai_state['personality'] != "" or ai_state['speaking_style'] != ""):
        # 发送给提示词节点
        Bus.publish('prompt', (ai_state['personality'], ai_state['speaking_style'])) 
    elif not ai_state["chat_mode"] and ai_state['personality'] == "" and ai_state['speaking_style'] == "":
        # 什么人设都不设置，就传一个空答案
        Bus.publish("ai_answer", (PROMPT, ""))
    # ai_state["chat_mode"]为True代表在正常聊天阶段
    elif ai_state["chat_mode"]:
        # 第一个False代表是不是设置性格模式，因为设置性格模式的对话是不会显示的
        if APP_node.app.ai_voice_on:
            Bus.publish("LLM", (WITH_VOICE, ai_state["question"][-1]))
        else:
            Bus.publish("LLM", (NO_VOICE, ai_state["question"][-1]))
        
#  负责接收显示器相关信息
@subscribe(APP_node, 'orientation')
def set_orientation(orientation):
    APP_node.orientation = orientation
    
# 负责接收天气相关信息
@subscribe(APP_node, 'weather_show')
def show_weather(msg):
    Bus.publish("TTS_message", msg)
    APP_node.app.weather_info_queue.put(msg)

# 负责接收AI的回答的
@subscribe(APP_node, 'ai_answer')
def get_ai_answer(data):
    text_type, text = data[0], data[1]
    if text_type is WITH_VOICE:
        Bus.publish("TTS_message", text)
    APP_node.app.ai_answer_queue.put(data)
    
# 负责接收STT的答案在进一步处理
@subscribe(APP_node, 'SST_answer')
def get_stt_answer(data):
    APP_node.app.record_queue.put(data)
    
    
################################################麦克风录音节点##################################
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import time

record_node = Node('record', fs=44100, filename='record.wav')

@initialize(record_node)
def init():
    record_node.out_dir = 'media/record'
    if not os.path.exists(record_node.out_dir):
        os.makedirs(record_node.out_dir)
    record_node.filename = record_node.out_dir + "/" + record_node.filename
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
        Bus.publish('SST_answer', transcript.text)
         
    
#####################################################cv2显示节点#######################################
import cv2
import time

display_node = Node('display')

@initialize(display_node)
def init():
    # 帧生成器
    display_node.frame_generator = None
    display_node.monitor = None
    display_node.gen = None

@set_task(display_node, loop=True)
def process_camera():
    while not display_node.frame_generator:
        time.sleep(0.001)
    prev_frame_generator = display_node.frame_generator
    
    while display_node.monitor is None:
        time.sleep(0.001)
    cv2.namedWindow('display', cv2.WND_PROP_FULLSCREEN)
    cv2.moveWindow('display', display_node.monitor.x, display_node.monitor.y)
    cv2.setWindowProperty('display', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)   
    start_time = time.time()
    try:
        for info in display_node.frame_generator():
            center_x, frame_center_x, frame = info[0], info[1], info[2]
            if frame is not None and frame is not LOOPSTOP_FRAME:
                cv2.imshow('display', frame)
                if time.time()-start_time>0.01:
                    Bus.publish('move_to_face', (center_x, frame_center_x))
                # 按下q就直接退出显示
                key = cv2.waitKey(1) & 0xff
                if  key == ord('q') or key == ord('Q'):
                    display_node.frame_generator = None
                    cv2.destroyAllWindows()
                    break
                # 如果相机生成器变化就跳出重新显示
                if prev_frame_generator != display_node.frame_generator:
                    break
            elif frame is LOOPSTOP_FRAME:
                Bus.publish('move_to_face', (center_x, frame_center_x))
                if prev_frame_generator != display_node.frame_generator:
                    break
            elif frame is None:
                display_node.frame_generator = None
                # print('显示失败')
                cv2.destroyAllWindows()
                break
    except Exception as e:
        print(e)
    
    
        
@subscribe(display_node, 'frame_gen')
def handler(frame_generator):
    if frame_generator is not None:
        display_node.frame_generator = frame_generator
        
@subscribe(display_node, 'display_setting')
def handler(monitor):
    # 在屏幕创建一个全屏窗口, monitor是窗口信息
    display_node.monitor = monitor

#################################################显示屏设置节点###########################################
from screen import *

# device是屏幕序号，这里1是副屏的意思
# res_width,res_height设置的是屏幕的分辨率
# orientation指的是显示视频时候要旋转的角度
# orientaion取值有 NO_ROTATE，ROTATE_90，ROTATE_180，ROTATE_270 这里的旋转是顺时针
# orientaion参数的设置是因为有的屏幕装的方向有问题
screen_node = Node('Screen', device=1, res_width=800, res_height=600, orientation=NO_ROTATE)

@initialize(screen_node)
def init():
    # 设置屏幕尺寸
    monitor = set_screen_size(device=screen_node.device, res_width=screen_node.res_width, res_height=screen_node.res_height)
    Bus.publish('orientation', screen_node.orientation)
    Bus.publish('display_setting', monitor)
    

################################################设定舵机节点#################################################
from servo import ServoController

servo_node = Node('Servo')

@initialize(servo_node)
def init():
    servo_node.servo = ServoController()
    servo_node.angle = servo_node.servo.read_angle()
    # 角速度, 单位度每秒
    servo_node.angular_velocity = 120
    # PID参数
    servo_node.Kp = 0.01
    servo_node.Ki = 0.00005  # 积分增益
    servo_node.Kd = 0.005  # 微分增益
    servo_node.last_error = 0  # 上一次的误差，用于微分计算
    servo_node.integral = 0  # 误差的积分

@add_method(servo_node)
def update_servo(center_x, frame_center_x):
    error = frame_center_x - center_x  # 计算偏差
    # 更新误差积分
    if 0 < servo_node.angle < 240:
        servo_node.integral += error
    else:
        servo_node.integral = 0  # 或者使用较小的积分值或按比例减少
    # 计算误差微分
    derivative = error - servo_node.last_error
    # 计算角度变化
    angle_delta = (servo_node.Kp * error) + (servo_node.Ki * servo_node.integral) + (servo_node.Kd * derivative)
    # 更新舵机角度
    new_angle = max(min(servo_node.angle + angle_delta, 240), 0)
    # 计算移动到新角度所需的时间
    angle_change = abs(angle_delta)
    time_to_move = angle_change / servo_node.angular_velocity
    # 发送新的角度和时间到舵机
    servo_node.servo.set_angle_time(new_angle, time_to_move)
    # 更新当前角度和上一次误差
    servo_node.angle = new_angle
    servo_node.last_error = error
        

@subscribe(servo_node, 'move_to_face')
def handler(pos):
    center_x, frame_center_x = pos[0], pos[1]
    if center_x is not None:
        servo_node.update_servo(center_x, frame_center_x)
 
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
        Bus.publish('weather_show', '城市不存在，无法查询')
        return
    try:
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功

        # 将JSON响应解析为字典
        weather_data = response.json()
        # 检查API返回是否成功
        if weather_data['status'] == 200:
            # 获取日期
            date = weather_data['date']
            
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
            time = f"{date[0:4]}年{date[4:6]}月{date[6:]}日"
            
            # 构建完整天气信息
            weather = f"天气{info}, 最高温{max_temp}度, 最低温{min_temp}度, 湿度{humd}, 空气质量{air_quality}"
            line = f'{parent_city}{city}：{weather}  【更新于{time}】'
            Bus.publish('weather_show', line)
        else:
            Bus.publish('weather_show', f"获取天气数据失败，状态码：{weather_data['status']}，消息：{weather_data['message']}")
    except requests.HTTPError as http_err:
        Bus.publish('weather_show', f"HTTP error occurred: {http_err}")  # HTTP错误响应
    except Exception as err:
        Bus.publish('weather_show', f"Other error occurred: {err}")  # 其他错误，如网络连接问题


################################################提示词节点#################################################
prompt_node = Node('Prompt')

@initialize(prompt_node)
def init():
    prompt_node.first = True
    
@subscribe(prompt_node, 'prompt')
def prompt(data):
    character = data[0]
    talk_manner = data[1]
    if prompt_node.first:
        prompt_node.first = False
        meaasge = f"接下来我和你对话， 请你的性格是：{character}，你和我的对话方式是：{talk_manner}"
    else:
        meaasge = f"请完全重置你自己的性格和说话方式，接下来我和你的对话, 请你的性格是：{character}，你和我的对话方式是：{talk_manner}"
    Bus.publish('LLM', (PROMPT, meaasge))


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
def handler(data):
    text_type, text = data[0], data[1]
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
    Bus.publish('ai_answer', (text_type, answer))



###################################################文字转语音节点########################################
import pyttsx3
from threading import Lock

TTS_node = Node('TTS')

@initialize(TTS_node)
def init():
    TTS_node.lock = Lock()
    
@subscribe(TTS_node, 'TTS_message')
def handler(answer):
    def say(msg):
        with TTS_node.lock:
            engine = pyttsx3.init()
            rate = engine.getProperty('rate') 
            engine.setProperty('rate', rate)
            engine.say(msg)
            engine.runAndWait()
        
    say(answer)
    Bus.publish("ai_answer", (VOICE_END, ""))

#################################################注册要运行的节点###########################################
APP_node.register()
display_node.register()
screen_node.register()
servo_node.register()
weather_node.register()
TTS_node.register()
LLM_node.register()
prompt_node.register()
STT_node.register()
record_node.register()


# 系统开始运行
miniROS.run()   
    
    

