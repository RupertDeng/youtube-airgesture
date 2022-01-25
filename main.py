from camera_capture import CameraCapture
from gesture_control import GestureControl
from multiprocessing import Process, Pipe

def camera(conn):
  camera_instance = CameraCapture(0, 0.7, 0.1)
  camera_instance.streaming(conn)

def gesture(conn):
  gesture_instance = GestureControl(1000, 300)
  gesture_instance.commanding(conn)


if __name__ == '__main__':

  downstream_conn, upstream_conn = Pipe(False)
  camera_process = Process(target=camera, args=(upstream_conn,))
  gesture_process = Process(target=gesture, args=(downstream_conn,))

  camera_process.start()
  gesture_process.start()
  camera_process.join()
  gesture_process.join()
