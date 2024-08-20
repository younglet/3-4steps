import threading
import queue
import time
from miniROS import Bus

class JumpOutException(Exception):
    """自定义异常，用于模拟break在on_process无限循环中"""
    pass

class ContinueException(Exception):
    """自定义异常，用于模拟 continue 在循环中的行为"""
    pass

class Node:
    """
    节点类，包含节点的启动、停止和消息处理逻辑
    """
    all_nodes = []

    def __init__(self, name, **kwargs):
        self.name = name
        self.subscriptions = {}
        self.message_queue = queue.Queue()
        self.node_thread = None
        self.on_process_thread = None  
        self.running = False
        self.initialize = None
        self.on_process = None
        self.on_stop = None
        self.should_stop = threading.Event()
        self.main = False  # 默认不是主线程
        self.loop = False  # 默认不是无限循环
        self.start_index = None  # 默认不关心启动顺序

        # 将kwargs中的参数转化为节点的属性
        for key, value in kwargs.items():
            if hasattr(self, key):
                raise ValueError(f"Attribute '{key}' conflicts with an existing attribute of Node.")
            setattr(self, key, value)
        
    def register(self):
        Node.all_nodes.append(self)
    
    def start(self):
        """启动节点，包括注册、启动任务线程和消息处理线程"""
        if not self.running:
            self.running = True
            self.should_stop.clear()
            if self.initialize:
                self.initialize()
            self.node_thread = threading.Thread(target=self._process_messages)
            self.node_thread.daemon = True
            self.node_thread.start()
            if self.on_process:
                if self.main:
                    self.on_process()  # 在主线程中运行
                else:
                    self.on_process_thread = threading.Thread(target=self.on_process)
                    self.on_process_thread.daemon = True
                    self.on_process_thread.start()
                    
    
    
    def node_break(self):
        """给出跳出异常，直接从调用的地方产生异常"""
        # if self.loop:
        raise JumpOutException()
    
    def node_continue(self):
        """给出跳出异常，直接从调用的地方产生异常"""
        # if self.loop:
        raise ContinueException()
    
    def stop(self):
        """停止节点，确保所有线程结束并注销节点"""
        if self.running:
            self.should_stop.set()
            if self.on_stop:
                self.on_stop()
            self.running = False
            Bus.unregister_node(self)
            Node.all_nodes.remove(self)

    def _process_messages(self):
        """消息处理线程，处理节点订阅的消息"""
        while self.running:
            try:
                topic, message = self.message_queue.get(timeout=0.001)
                if topic in self.subscriptions:
                    handlers = self.subscriptions[topic]
                    for handler in handlers:
                        threading.Thread(target=handler, args=(message,)).start()
            except queue.Empty:
                continue

    def receive_message(self, topic, message):
        """接收消息并放入队列"""
        self.message_queue.put((topic, message))
    
    @classmethod
    def run(cls, *, main_loop=True):
        """按照顺序启动所有节点"""
        n = len(cls.all_nodes)

        # 处理负索引和索引范围验证
        for node in cls.all_nodes:
            if node.start_index is not None:
                if node.start_index < 0:
                    node.start_index += n
                if not (0 <= node.start_index < n):
                    raise ValueError(f"Index out of range for node {node.name}")

        # 检查是否有重复的 start_index
        indices = [node.start_index for node in cls.all_nodes if node.start_index is not None]
        if len(indices) != len(set(indices)):
            raise ValueError("Duplicate start_index found")
        
        # 初始化执行列表
        execution_list = [None] * n

        # 填充已指定 start_index 的节点
        for node in cls.all_nodes:
            if node.start_index is not None:
                execution_list[node.start_index] = node

        # 分类未指定 start_index 的节点
        unspecified_nodes = [node for node in cls.all_nodes if node.start_index is None]
        main_false_nodes = [node for node in unspecified_nodes if not node.main]
        main_true_loop_false_nodes = [node for node in unspecified_nodes if node.main and not node.loop]
        main_true_loop_true_nodes = [node for node in unspecified_nodes if node.main and node.loop]

        # 按优先级填充空白位置
        index = 0
        for node_list in [main_false_nodes, main_true_loop_false_nodes, main_true_loop_true_nodes]:
            for node in node_list:
                while index < n and execution_list[index] is not None:
                    index += 1
                if index < n:
                    execution_list[index] = node
                    index += 1

        # 检查最终列表并发出警告
        last_main_false_index = max((i for i, node in enumerate(execution_list) if not node.main), default=-1)
        for i, node in enumerate(execution_list):
            if node.main and node.loop and i < n - 1:  # main 和 loop 都是 True 的节点不在末尾
                print(f"Warning: Node {node.name} with 'main' and 'loop' both True is not at the end, which may cause blocking.")
            if node.main and not node.loop and i < last_main_false_index:  # main 是 True 但 loop 是 False 的节点在 main 是 False 的节点之前
                print(f"Warning: Node {node.name} with 'main' True and 'loop' False is before a 'main' False node, which may cause unexpected behavior.")

        # 启动所有节点
        for node in execution_list:
            node.start()

        # 如果没有在主线程运行且为无限循环的节点，若 main_loop 为 True，保持主程序运行
        while main_loop:
            time.sleep(0.001)
            if len(Node.all_nodes) == 0:
                break
            
    @classmethod
    def stop_all(cls):
        """停止所有节点，确保所有线程结束"""
        for node in list(cls.all_nodes):  # 使用list来避免修改迭代中的列表
            node.stop()
   

def initialize(node):
    """
    装饰器：注册节点进行的一些初始化
    """
    def decorator(func):
        node.initialize = func
        return func
    return decorator

def set_task(node, *, loop=False, main=False, index=None):
    """
    装饰器：注册节点启动时的任务
    loop参数代表是否这个on_process需要无限循环来进行处理
    main参数代表是否这个on_process需要在主线程中运行
    """
    def decorator(func):
        def wrapper():
            if loop:
                while not node.should_stop.is_set():
                    try:
                        func()
                    except ContinueException:
                        continue  # 捕获 ContinueException 并继续循环
                    except JumpOutException:
                        break  # 捕获 JumpOutException 并跳出循环
            else:
                try:
                    func()
                except JumpOutException:
                    pass
                except ContinueException:
                    pass  # 在非循环任务中，ContinueException 无操作
        node.on_process = wrapper
        node.main = main  # 设置是否在主线程中运行
        node.loop = loop  # 设置是否为无限循环
        node.start_index = index  # 设置启动顺序
        return func
    return decorator

def on_stop(node):
    """
    装饰器：注册节点停止时的任务
    """
    def decorator(func):
        node.on_stop = func
        return func
    return decorator

def subscribe(node, topic):
    """
    装饰器：注册节点的消息处理函数
    """
    def decorator(func):
        def wrapper(message):
            try:
                func(message)
            except JumpOutException:
                pass
        if topic not in node.subscriptions:
            node.subscriptions[topic] = []
        node.subscriptions[topic].append(lambda msg: wrapper(msg))
        Bus.register_topic(node, topic)
        return func
    return decorator


def add_method(node):
    """
    装饰器：为节点添加新的方法，并防止名字重复
    """
    def decorator(func):
        if hasattr(node, func.__name__):
            raise ValueError(f"Method name '{func.__name__}' already exists in node '{node.name}'")
        setattr(node, func.__name__, func)
        return func
    return decorator