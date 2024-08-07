class Bus:
    """
    总线类，用于控制节点的注册和注销，以及针对某个主题的消息发布
    """
    topics = {}

    @staticmethod
    def register_node(node):
        """注册节点的所有订阅主题"""
        for topic in node.subscriptions.keys():
            Bus.register_topic(node, topic)

    @staticmethod
    def unregister_node(node):
        """注销节点并清理没有订阅者的主题"""
        for topic, nodes in list(Bus.topics.items()):
            if node in nodes:
                nodes.remove(node)
                if not nodes:  # 如果某主题下没有节点了，则删除该主题
                    del Bus.topics[topic]

    @staticmethod
    def register_topic(node, topic):
        """为节点注册主题"""
        if topic not in Bus.topics:
            Bus.topics[topic] = []
        if node not in Bus.topics[topic]:
            Bus.topics[topic].append(node)

    @staticmethod
    def publish(topic, message):
        """发布消息到某个主题"""
        if topic in Bus.topics:
            for node in Bus.topics[topic]:
                node.receive_message(topic, message)



