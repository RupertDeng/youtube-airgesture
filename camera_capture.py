import cv2
import mediapipe as mp
import time

class CameraCapture:

  def __init__(self, cam_ind, detection_confidence, cap_delay):

    # define camera capture attributes
    self.capture = cv2.VideoCapture(cam_ind)
    self.cap_width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    self.cap_height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    self.cap_delay = cap_delay

    # define mediapipe detector and drawer
    mp_hands = mp.solutions.hands
    self.detector = mp_hands.Hands(max_num_hands=1, static_image_mode=False, min_detection_confidence=detection_confidence, min_tracking_confidence=detection_confidence)
    self.drawer = mp.solutions.drawing_utils.draw_landmarks
    self.draw_connections = mp_hands.HAND_CONNECTIONS

  def destruct(self):
    """
    clean up steps when needed
    """
    self.capture.release()
    cv2.destroyAllWindows()

  def get_key_points(self, landmarks):
    """
    Mediapipe landmark coordinates are normalized to 0 ~ 1.
    Here convert them back to screen pixels and pass the array of points to gesture control process.
    """
    points = []
    for landmark in landmarks:
      points.append((int(landmark.x * self.cap_width), int(landmark.y * self.cap_height)))
    return points

  def streaming(self, data_pipe):
    while True:
      success, frame = self.capture.read()
      if not success:
        self.destruct()
        data_pipe.send(-1)
        raise Exception('Camera capturing failed!')
      
      frame = cv2.flip(frame, 1)
      rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
      hands = self.detector.process(rgb_frame).multi_hand_landmarks

      # if hand is detected, send key points via data pipe. Otherwise, don't send anything over.
      if hands:
        landmarks = hands[0]
        key_points = self.get_key_points(landmarks.landmark)
        data_pipe.send(key_points)
        self.drawer(frame, landmarks, self.draw_connections)

      cv2.imshow('Hand', frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):   # if 'q' is pressed on the window, send signal -1 via data pipe to end both processes.
        self.destruct()
        data_pipe.send(-1)
        break

      # capture delay time between frames. sometimes it can be useful if camera keeps detecting un-desired gesture during gesture transition.
      if self.cap_delay > 0: time.sleep(self.cap_delay)  