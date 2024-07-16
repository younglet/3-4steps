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
                    node.receive(message)
class Node:
    def __init__(self, name):
        self.name = name
    def receive(self, message):
        print(f'{self.name} received message on topic: {message}')

    def receive(self, message):
        print(f'{self.name} received message on topic: {message}')

if __name__ == "__main__":
    bus = Bus()
    
    node1 = Node('Node 1')
    node2 = Node('Node 2')
    node3 = Node('Node 3')

    bus.subscribe("news", node1)
    bus.subscribe("news", node2)
    bus.subscribe("sports", node1)
    bus.subscribe("sports", node3)

    # 通过节点实例间接发布消息到总线上
    bus.publish("news", "Latest technology update!", sender=node1)
    bus.publish("sports", "Basketball season starts!", sender=node1)