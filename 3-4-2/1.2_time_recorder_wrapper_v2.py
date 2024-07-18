import time


def run_with_time_recorder(func):
    start_time = time.time()
    func()
    end_time = time.time()
    print(f'函数{func.__name__}用时:{ end_time - start_time }S')

def print_10k_times():
    for i in range(10_000):
        print(i) 


def print_100k_times():
    for i in range(100_000):
        print(i) 


run_with_time_recorder(print_10k_times)
run_with_time_recorder(print_100k_times)
