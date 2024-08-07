from miniROS.Bus import *
from miniROS.Node import *

class miniROS:
    @classmethod
    def run(cls, main_loop=True):
        Node.run(main_loop=main_loop)
         
    @classmethod
    def stop(cls):
        Node.stop_all()
        