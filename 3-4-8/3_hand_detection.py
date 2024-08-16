import cv2
import mediapipe as mp

# 初始化MediaPipe Hands
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=2,
    min_detection_confidence=0.5)


# 加载一张图像
image_path = 'path/to/your/image.jpg'
image = cv2.imread(image_path)

# 转换BGR图像为RGB
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# 处理图像
results = hands.process(image_rgb)

# 绘制关键点
image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
if results.multi_hand_landmarks:
    for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            image, hand_landmarks, mp_hands.HAND_CONNECTIONS)


# 显示结果图像
cv2.imshow('手势检测', image)
cv2.waitKey(0)
cv2.destroyAllWindows()