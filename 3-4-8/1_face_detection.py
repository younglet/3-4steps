import cv2
import mediapipe as mp

# 初始化 MediaPipe 的人脸检测模块
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# 加载一张图像
image_path = 'path/to/your/image.jpg'
image = cv2.imread(image_path)

# 将图像转换为 RGB 格式
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# 进行人脸检测
result = face_detection.process(image_rgb)

# 检查是否有任何检测结果
if result.detections:
    # 遍历所有的检测结果
    for detection in result.detections:
        # 获取边界框的位置
        bboxC = detection.location_data.relative_bounding_box1
        x_min = int(bboxC.xmin * image.shape[1])
        y_min = int(bboxC.ymin * image.shape[0])
        box_width = int(bboxC.width * image.shape[1])
        box_height = int(bboxC.height * image.shape[0])
        cv2.rectangle(image, (x_min, y_min), (x_min + box_width, y_min + box_height), (0, 255, 0), 2)


        # 打印检测信息
        print("检测置信度:", detection.score)
        print("边界框坐标 (x_min, y_min, 宽度, 高度):", (x_min, y_min, bboxC.width, bboxC.height))
else:
    print("未找到检测结果。")

# 显示结果图像
cv2.imshow('人脸检测', image)
cv2.waitKey(0)
cv2.destroyAllWindows()