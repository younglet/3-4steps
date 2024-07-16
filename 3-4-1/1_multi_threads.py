import threading
import time

def print_numbers():
    for i in range(5):
        print(i)
        time.sleep(1)

def print_letters():
    for letter in 'abcde':
        print(letter)
        time.sleep(1)

# 创建线程
t1 = threading.Thread(target=print_numbers)
t2 = threading.Thread(target=print_letters)

# 启动线程
t1.start()
t2.start()

# 等待线程结束（可选）
t1.join()
t2.join()

print("所有线程执行完毕。")