def simple_generator():
    yield 1
    yield 2
    yield 3

# 创建生成器对象
gen = simple_generator()

# 使用 next() 函数获取值
print(next(gen))  # 输出 1
print(next(gen))  # 输出 2
print(next(gen))  # 输出 3

# 或者使用 for 循环遍历生成器
for value in simple_generator():
    print(value)