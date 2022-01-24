import cv2
import mediapipe as mp
import time

class CameraCapture:

  def __init__(self, cam_ind, detection_confidence, cap_delay):
    self.capture = cv2.VideoCapture(cam_ind, cv2.CAP_DSHOW)
    mp_hands = mp.solutions.hands
    self.detector = mp_hands.Hands(max_num_hands=1, static_image_mode=False, min_detection_confidence=detection_confidence, min_tracking_confidence=detection_confidence)
    self.drawer = mp.solutions.drawing_utils
    self.draw_connections = mp_hands.HAND_CONNECTIONS
    self.cap_delay = cap_delay

  def destruct(self):
    self.capture.release()
    cv2.destroyAllWindows()

  def get_key_points(self, landmarks):
    points = []
    for landmark in landmarks:
      points.append((landmark.x, landmark.y))
    return points

  def streaming(self, data_pipe):
    while True:
      success, frame = self.capture.read()
      if not success:
        self.destruct()
        data_pipe.send([])
        raise Exception('Camera capturing failed!')
      
      frame = cv2.flip(frame, 1)
      rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

      hands = self.detector.process(rgb_frame).multi_hand_landmarks
      if not hands: continue
      landmarks = hands.pop()
      key_points = self.get_key_points(landmarks.landmark)
      data_pipe.send(key_points)
      self.drawer(frame, landmarks, self.draw_connections)

      cv2.imshow('Hand', frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
        self.destruct()
        data_pipe.send([])
        break

      if self.cap_delay > 0: time.sleep(self.cap_delay)