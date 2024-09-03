import serial
import serial.tools.list_ports
import struct

class ServoController:
    def __init__(self) -> None:
        # 控制舵机的一些协议的相关指令
        self.SERVO_MOVE_TIME_WRITE = 1
        self.SERVO_MOVE_TIME_WRITE_length = 7
        self.SERVO_POS_READ = 28
        self.SERVO_POS_READ_length = 3
        self.board_info = "1A86:7523"
        #打开串口
        self.ser = serial.Serial(self.find_board(), 115200, timeout=1)
        
    def set_angle_time(self, angle, time):
        """
        要在time时间内转到angle这个角度
        time的范围是0-30秒
        angle的范围是0-240度,需要映射到0-1000的整数
        """
        # if not 0 <= angle <= 240:
        #     raise ValueError("Input angle must be between 0 and 240.")
        # if not 0 <= time <= 30:
        #     raise ValueError("Input time must be between 0 and 30.")
        angle = max(min(angle, 240), 0)
        time = max(min(time, 30), 0)
        # 角度映射到0-1000，并确保结果为整数
        angle = int(round(1000 *angle / 240))
        time = int(time*1000) # 转换为毫秒
        data = [0x55, 0x55, 0x01, self.SERVO_MOVE_TIME_WRITE_length, self.SERVO_MOVE_TIME_WRITE,
                angle & 0xff, (angle >> 8) & 0xff, time & 0xff, (time >> 8) & 0xff]
        crc = self.calculate_crc(data[2:])
        data.append(crc)
        # 发送数据
        self.ser.write(bytearray(data))
        
    def read_angle(self):
        data = [0x55, 0x55, 0x01, self.SERVO_POS_READ_length, self.SERVO_POS_READ]
        crc = self.calculate_crc(data[2:])
        data.append(crc)
        # 发送读取命令
        self.ser.write(bytearray(data))
        # 读取命令
        # if self.ser.in_waiting >= 8:
        # 读取8个字节
        response = self.ser.read(8)
        if len(response) == 8 and response[0] == 0x55 and response[1] == 0x55:
            # 检查第三个字节是否为1
            if response[2] == 1:
                # 计算并检查CRC
                calculated_crc = self.calculate_crc(response[2:-1])
                if calculated_crc == response[-1]:
                    # 组合倒数第二和第三个字节为16位有符号整数
                    high_byte = response[-2]  # 高八位
                    low_byte = response[-3]   # 低八位
                    # 组合成16位无符号整数
                    combined_value = (high_byte << 8) | low_byte
                    # 使用struct转换无符号整数为有符号整数
                    signed_value = struct.unpack('h', struct.pack('H', combined_value))[0]
                    return signed_value*0.24
                else:
                    print("CRC check failed")
            else:
                print("Third byte check failed")
        else:
            print("Header bytes are incorrect or wrong response length")
        return None
        
    def find_board(self):

        # 列举系统中所有可用的串口
        ports = list(serial.tools.list_ports.comports())

        # 遍历所有串口，查找匹配的VID:PID
        for port in ports:
            if self.board_info in port.hwid:
                return port.device

        raise ValueError("board not found")
    
    @staticmethod
    def calculate_crc(data):
        return (~(sum(data))) & 0xff
    
    
# x=ServoController()
# for angle in range(21,100):
    
#     x.set_angle_time(angle, 0.1)
# print(x.read_angle())
    
    