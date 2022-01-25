from math import acos, pi, sqrt
class Finger:

  def __init__(self, name, straight_thresh, extend_thresh):
    """
    The MCP, PIP, DIP and TIP points are using the same names from mediapipe for finger joint points.
    Each of them is 2-element (x, y) screen pixel array.
    staight_thresh: threshhold to determine when finger is not straight any more.
    extend_thresh: threshold to determine when finger is not fully extended from palm any more.
    """
    self.name = name
    self.MCP = []
    self.PIP = []
    self.DIP = []
    self.TIP = []
    self.straight_thresh = straight_thresh
    self.extend_thresh = extend_thresh

  def update(self, MCP, PIP, DIP, TIP):
    self.MCP = MCP
    self.PIP = PIP
    self.DIP = DIP
    self.TIP = TIP

  def get_angle(self, v1, v2):
    """
    utility function to calculte the angle between two vector v1, v2
    """
    x1, y1 = v1
    x2, y2 = v2
    l1, l2 = x1*x1 + y1*y1, x2*x2 + y2*y2
    if l1 <= 1 or l2 <= 1: return 180
    product = x1 * x2 + y1 * y2
    sign = 1 if product >= 0 else -1
    return acos(sign *sqrt(product ** 2 / (l1 * l2))) / pi * 180

  def is_straight(self, wrist_point):
    """
    The way to determine if finger is fully straight out includes 2 parts:
    1) determine if finger is fully extended from palm based on the angle between the two section (wrist -> MCP) vs. (MCP -> PIP)
    2) determine if finger is straight based on the angle between he two section (MCP -> PIP) vs. (DIP -> TIP)
    
    For the 2nd check, one can also use the angle between (MCP -> PIP) vs. (PIP -> DIP) if the top part of the finger is natually bending out. 
    """
    vector1 = [self.MCP[0] - wrist_point[0], self.MCP[1] - wrist_point[1]]
    vector2 = [self.PIP[0] - self.MCP[0], self.PIP[1] - self.MCP[1]]
    vector3 = [self.TIP[0] - self.DIP[0], self.TIP[1] - self.DIP[1]]
    return self.get_angle(vector1, vector2) <= self.extend_thresh and self.get_angle(vector2, vector3) <= self.straight_thresh

