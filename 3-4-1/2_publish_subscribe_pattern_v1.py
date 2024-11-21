class Publisher:
    def __init__(self):
        self.subscribers = []

    def register(self, who):
        if who not in self.subscribers:
            self.subscribers.append(who)

    def unregister(self, who):
        if who in self.subscribers:
            self.subscribers.remove(who)

    def publish(self, message):
        for subscriber in self.subscribers:
            subscriber.receive(message)


class Subscriber:
    def __init__(self, name):
        self.name = name

    def receive(self, message):
        print(f'{self.name} 收到了一条信息: {message}')


if __name__ == "__main__":
    pub = Publisher()

    # 创建订阅者
    sub1 = Subscriber('订阅者1')
    sub2 = Subscriber('订阅者2')

    # 注册订阅者
    pub.register(sub1)
    pub.register(sub2)

    # 发布消息
    pub.publish("你好，这是一条消息！")

    # 注销订阅者
    pub.unregister(sub1)

    # 再次发布消息，此时只有sub2会收到消息
    pub.publish("这是另一条消息！")