import easygui

# 消息框
easygui.msgbox('你好，欢迎来到斯坦星球！')

# 输入框
name = easygui.enterbox('请问你叫什么名字?')
easygui.msgbox('你好呀, ' + name + '!')

# 是否框
result = easygui.ynbox('你喜欢编程吗？')
if result:
  easygui.msgbox('太棒了！我们一起学习编程吧！')
else:
  easygui.msgbox('没关系，我会让你体验到编程的乐趣的！')

# 选择框
choices = ['机器人', '编程', '网络']
selected_choice = easygui.choicebox('从中选择出你最喜欢的主题', choices = choices)
easygui.msgbox('你最喜欢的主题：' + selected_choice + '！')

# 运行 easygui.egdemo()
easygui.egdemo()