class Bus:
    def __init__(self):
        self.topics = {}

    def subscribe(self, topic_name, node):
        if topic_name not in self.topics:
            self.topics[topic_name] = []
        if node not in self.topics[topic_name]:
            self.topics[topic_name].append(node)

    def unsubscribe(self, topic_name, node):
        if topic_name in self.topics and node in self.topics[topic_name]:
            self.topics[topic_name].remove(node)

    def publish(self, topic_name, message, sender):
        if topic_name in self.topics:
            for node in self.topics[topic_name]:
                if node != sender:
                    node.receive(topic_name,message)
class Node:
    def __init__(self, name):
        self.name = name

    def receive(self, topic, message):
        print(f'{self.name} 收到了主题为{topic}的消息，消息内容为： {message} ')

if __name__ == "__main__":
    bus = Bus()
    
    node1 = Node('节点1')
    node2 = Node('节点2')
    node3 = Node('节点3')

    bus.subscribe("新闻", node1)
    bus.subscribe("新闻", node2)
    bus.subscribe("体育", node1)
    bus.subscribe("体育", node3)

    # 通过节点实例间接发布消息到总线上
    bus.publish("新闻", "科技取得重大突破！", sender=node1)
    bus.publish("体育", "篮球新赛季开始！", sender=node1)