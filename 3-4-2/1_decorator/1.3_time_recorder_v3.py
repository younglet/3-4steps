import time


def run_with_time_recorder(func):
    def modified_func():
        start_time = time.time()
        func()
        end_time = time.time()
        print(f'{func.__name__}:{ end_time - start_time }S')
    return modified_func

def print_10k_times():
    for i in range(10_000):
        print(i) 

print_10k_times = run_with_time_recorder(print_10k_times)


print_10k_times()
