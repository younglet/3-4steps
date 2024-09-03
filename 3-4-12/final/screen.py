import ctypes
import subprocess
from screeninfo import get_monitors

                
# 屏幕旋转参数设定
NO_ROTATE = 0
ROTATE_90 = 1
ROTATE_180 = 2
ROTATE_270 = 3

class DEVMODE(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", ctypes.c_char * 32),
        ("dmSize", ctypes.c_ushort),
        ("dmFields", ctypes.c_ulong),
        ("dmPelsWidth", ctypes.c_ulong),
        ("dmPelsHeight", ctypes.c_ulong)
    ]

def set_screen_size(device, res_width=800, res_height=600):
    subprocess.run("DisplaySwitch.exe /extend")
    user32 = ctypes.windll.user32
    devmode = DEVMODE()
    devmode.dmSize = ctypes.sizeof(DEVMODE)
    devmode.dmPelsWidth = res_width
    devmode.dmPelsHeight = res_height
    devmode.dmFields = 0x00080000 | 0x00100000
    
    monitors = get_monitors()
    device_name = monitors[device].name
    
    if user32.ChangeDisplaySettingsExA(device_name.encode('utf-8'), ctypes.byref(devmode), None, 1, None) != 0:
        ValueError(f"无法设置显示{device}")
        
    return monitors[device]
        
