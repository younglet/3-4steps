import time


def print_10k_times():
    for i in range(10_000):
        print(i)    

start_time = time.time()
print_10k_times()
end_time = time.time()

print(f'用时:{ end_time - start_time }S')
