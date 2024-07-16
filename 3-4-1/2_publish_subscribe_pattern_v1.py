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
        print(f'{self.name} received message: {message}')


if __name__ == "__main__":
    pub = Publisher()

    # 创建订阅者
    sub1 = Subscriber('Subscriber 1')
    sub2 = Subscriber('Subscriber 2')

    # 注册订阅者
    pub.register(sub1)
    pub.register(sub2)

    # 发布消息
    pub.publish("Hello, this is a new message!")

    # 注销订阅者
    pub.unregister(sub1)

    # 再次发布消息，此时只有sub2会收到消息
    pub.publish("Another message!")