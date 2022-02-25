# A simple windows app to control youtube in browser with hand gesture

## 1) Basic mechanism
- Two processes are running in parallel utilizing multi-core CPU to reduce latency.
- `Camera_capture` process will detect key hand landmark points using opencv and mediapipe libraries in real time, and send data over to gesture-control process via python multi-processing data pipe.
- `Gesture-control` process will listen to the data flow and determine which fingers are out-straight, and map the state based on gesture mapping (see below), and trigger key-pressing event on chrome browser via pyautogui package, in order to control youtube playback.

## 2) Finger class
- To streamline the calculation on finger state, a finger class is created, and instantiated for all 5 fingers at the beginning of gesture_control process.
- Every fingers has 4 key points (MCP, PIP, DIP, TIP) from root to tip (reference: [mediapipe](https://google.github.io/mediapipe/solutions/hands.html)), and including the palm-wrist point, the class will use all these points to determine finger state.
- First, `determine if finger is fully extended out from palm`, by the angle between the two section (wrist -> MCP) vs. (MCP -> PIP)
- Second, `determin if finger is straight` based on the angle between he two section (MCP -> PIP) vs. (DIP -> TIP).
- Each step has a threshhold value defined in the finger class, so it can also be individually tuned for each finger.
- It is not the most accurate method since the camerate image is on 2d plane and sometimes the key points from the same finger may even overlop when hand is rotating. But for the gestures I need, it is robust enough.

## 3) Gesture mapping
- all five fingers are straight out --> send key-press 'space' --> `pause or resume playback`
- thumb and index fingers are out --> send key-press 'f' --> `activate or deactivate fullscreen`
- index and middle fingers are out --> send key-press 'c' --> `activate or deactivate caption`
- only thumb finger is out, pointing left or right --> send key-press 'left-arrow/right-arrow' --> `seek backward/forward 5 seconds`
- index and litte fingers are out --> send key-press '>' --> `speed up playback rate by 1 level`
- thumb and little fingers are out --> send key-press '<' --> `slow down playback rate by 1 level`
- fist or un-recognized gesture -- > no action
- The gesture determination is executed every key_action_delay time which was set to default 1s for all except seek backward/forward. Seeking backward/forward delay is set to 0.3s to allow consecutive triggering.

## 4) Installation and testing
- Install the required packages after cloning the repository
- Start the app with `python main.py`, after the camera window shows up, mouse click on browser youtube page for standby.
- Play with the provided gesture mapping. Terminate the app by press 'q' on the camera window.
- You may need to adjust the finger gesture threshold for your hands.

_After thoughts: the mediapipe library is so much fun. Just with the hand detection capability, one can also make an useful app to capture guitar chord from youtube videos. Might need some other ML tools to detect the guitar fretboard layout, but it should be do-able. :-) _
