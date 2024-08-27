generator_nums = (_ for _ in range(10))

for _ in range(11):
    print(next(generator_nums))
