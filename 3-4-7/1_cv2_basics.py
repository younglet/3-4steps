import cv2

img = cv2.imread('test.jpg') # 读取图像，test.jpg文件请自行准备或替换
cv.imshow('test', img) # 显示图像，窗口名为test
cv2.waitKey(0) # 等待按键按下
cv2.imwrite('new.jpg', img) # 将图像保存为new.jpg
cv2.destroyAllWindows() # 关闭所有窗口