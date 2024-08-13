import cv2
import numpy as np


img = cv2.imread('test.jpg') # 读取图像，test.jpg文件请自行准备或替换

cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # 转换为灰度图
cv2.resize(img, (640, 480)) # 缩放图像
cv2.flip(img, 1) # 翻转图像, 0竖直, 1水平, -1水平+竖直
kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]) # 创建核
cv2.filter2D(img, -1, kernel) # 滤波