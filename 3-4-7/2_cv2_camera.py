import cv2


cap = cv2.VideoCapture(0) # 创建一个VideoCapture对象，参数0表示默认摄像头

if not cap.isOpened(): # 检查是否成功打开了摄像头
    print("无法打开摄像头")
    exit()

while True:
    ret, frame = cap.read() # 从摄像头捕获一帧
    if not ret: # 如果正确捕获到一帧，则ret为True
        print("无法获取帧")
        break
    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) == ord('q'): # 按'q'键退出循环
        break

# 当一切都完成后释放摄像头
cap.release()
cv2.destroyAllWindows()