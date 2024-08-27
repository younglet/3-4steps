import time 
import sys

# 比较推导式和生成器表达式的性能
start_time = time.time()
comprehension_nums = [_ for _ in range(1_000_000)]
print(f'列表推导式创建用时: {(time.time() - start_time):0.8f} s')
print(f'列表推导式占用内存: {sys.getsizeof(comprehension_nums)} bytes')

start_time = time.time()
generator_nums = (_ for _ in range(1_000_000))
print(f'生成器创建用时: {(time.time() - start_time):0.8f} s')
print(f'生成器占用内存: {sys.getsizeof(generator_nums)} bytes')