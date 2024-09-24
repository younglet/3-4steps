import time


def run_with_time_recorder(func):
    def modified_func():
        start_time = time.time()
        result = func()  
        end_time = time.time()
        print(f'函数{func.__name__}用时:{ end_time - start_time }秒')
    return modified_func

@run_with_time_recorder
def print_10k_times():
    for i in range(10_000):  # 
        print(i)

print_10k_times()