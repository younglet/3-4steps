from miniROS.Bus import *
from miniROS.Node import *

class miniROS:
     @classmethod
     def run(main_loop=True):
         Node.run(main_loop=main_loop)