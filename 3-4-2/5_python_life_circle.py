import time
from random import randint

class Person:
    def __init__(self):
        self.age = 1
        print('我出生了! 现在1岁')
        time.sleep(0.1)
        self.grow()
    
    def grow(self):
        for i in range(randint(30, 100)):
            self.age += 1 
            print(f'我长大了一岁! 现在{self.age}岁')
            time.sleep(0.1)
        del(self)
    
    def __del__(self):
        print(f'我死了，享年{self.age}岁')

person = Person()