def fibonacci(n):
    a, b = 0, 1
    while n > 0:
        yield a
        a, b = b, a + b
        n -= 1

# 创建斐波那契数列生成器
fib_gen = fibonacci(10)

# 打印斐波那契数列
for num in fib_gen:
    print(num)