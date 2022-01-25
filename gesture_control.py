import time
import pyautogui
from finger import Finger

class GestureControl:

  def __init__(self, key_action_delay, playback_skip_delay):
    """
    Initialize 5 fingers and wrist point with empty coordinates. Finger's threshold values can be set individually.
    One attribute to keep track of the timestamp when a gesture is identified.
    Two timing attributes (in milli-second) are for the delay time to trigger key-press action, and trigger playback skip.
    """
    self.thumb = Finger('thumb', 45, 30)
    self.index = Finger('index', 20, 45)
    self.middle = Finger('middle', 20, 45)
    self.ring = Finger('ring', 20, 45)
    self.pinky = Finger('pinky', 20, 45)
    self.wrist = []
    self.last_timestamp = 0
    self.key_action_delay = key_action_delay
    self.playback_skip_delay = playback_skip_delay


  def update_hand(self, points):
    """
    update coordinates to all finger objects when the key points are received
    """
    self.wrist = points[0]
    self.thumb.update(*points[1:5])
    self.index.update(*points[5:9])
    self.middle.update(*points[9:13])
    self.ring.update(*points[13:17])
    self.pinky.update(*points[17:21])


  def get_gesture(self):
    """
    Determine the hand gesture. 6 specific gestures are selected to achieve the gesture control goal.
    Other kinds of gestures are simply set to 0 as un-recognizable, including fist.
    One can choose his/her own gesture set for different purposes, but a fine tuning of the finger threshold values might be needed if the gestures are similar with each other.
    Sometimes it is just not reliable enough with the simple approach used here on complex gesture.
    """

    # use bitmask to combine all fingers' state
    state = 0
    if self.thumb.is_straight(self.wrist): state |= 1 << 4
    if self.index.is_straight(self.wrist): state |= 1 << 3
    if self.middle.is_straight(self.wrist): state |= 1 << 2
    if self.ring.is_straight(self.wrist): state |= 1 << 1
    if self.pinky.is_straight(self.wrist): state |= 1

    if state == int('11111', 2):
      return 1        # all five fingers are straight out --> pause or resume playback
    elif state == int('11000', 2):
      return 2        # thumb and index are out --> activate or deactivate fullscreen
    elif state == int('01100', 2):
      return 3        # index and middle are out --> activate or deactivate caption
    elif state == int('10000', 2):
      return 4        # only thumb finger is out --> seek backward/forward 5 seconds
    elif state == int('01001', 2):
      return 5        # index and pinky are out --> speed up playback rate by 1 level
    elif state == int('10001', 2):
      return 6        # thumb and pinky are out --> slow down playback rate by 1 level
    else:
      return 0       # fist or un-recognized gesture -- > no command
    

  def get_thumb_direction(self):
    """
    Determine the thumb direction specifically for gesture 4, by comparing the thumb tip point along x-axis with the min/max of all palm points (wrist and MCPs).
    """
    palm_left = min(self.thumb.MCP[0], self.index.MCP[0], self.index.MCP[0], self.ring.MCP[0], self.pinky.MCP[0])
    palm_right = max(self.thumb.MCP[0], self.index.MCP[0], self.index.MCP[0], self.ring.MCP[0], self.pinky.MCP[0])
    if self.thumb.TIP[0] < palm_left:
      return 'L'
    elif self.thumb.TIP[0] > palm_right:
      return 'R'
    else:
      return 'M'

  
  def commanding(self, data_pipe):
    """
    Data pipe keeps sending over the key point coordinates. -1 to end the process.
    The coordinates will be updated to all fingers, and a gesture is identified to trigger key-press action via pyautogui in chrome browser.
    Based on experience, very often, a gesture might become un-recognizable intermittently.
    Therefore, rather than comparing current gesture with last gesture, it is easier to just set a delay time to trigger action
    1) if gestures if 4 (for skip 5s playback forward/backward), only trigger action after playback_skip_delay
    2) otherwise, only trigger key-press action after key_action_delay
    """

    while True:
      points = data_pipe.recv()  # the recv function will keep waiting until data is sent over from data pip upstream
      if points == -1: break
      self.update_hand(points)

      timestamp = int(time.time()) * 1000

      if timestamp - self.last_timestamp <= self.playback_skip_delay:
        continue

      gesture = self.get_gesture()

      if gesture == 4:
        direction = self.get_thumb_direction()
        if direction == 'M': continue
        elif direction == 'L': pyautogui.press('left')
        else: pyautogui.press('right')
        self.last_timestamp = timestamp
        continue

      if timestamp - self.last_timestamp <= self.key_action_delay:
        continue
      
      if gesture == 1:
        pyautogui.press('space')
      elif gesture == 2:
        pyautogui.press('f')
      elif gesture == 3:
        pyautogui.press('c')
      elif gesture == 4:
        direction = self.get_thumb_direction()
        if direction == 'M': continue
        elif direction == 'L': pyautogui.press('left')
        else: pyautogui.press('right')
      elif gesture == 5:
        pyautogui.press('>')
      elif gesture == 6:
        pyautogui.press('<')

      self.last_timestamp = timestamp

      


      
