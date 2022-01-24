import cv2
import mediapipe as mp
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while True:
  success, frame = cap.read()
  frame = cv2.flip(frame, 1)

  rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
  result = hands.process(rgb_frame)

  if result.multi_hand_landmarks:
    for lms in result.multi_hand_landmarks:
      print(lms.landmark[0])
      mp_draw.draw_landmarks(frame, lms, mp_hands.HAND_CONNECTIONS)

  cv2.imshow('Hand', frame)
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break
  # time.sleep(0.2)

cap.release()
cv2.destroyAllWindows()