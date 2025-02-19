from os import name
import threading
import av, av.container
import cv2
from ipkvm import profile
from ipkvm.util import video
from ipkvm import logger
import time

class FrameBuffer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.buffer_lock = threading.Lock()
        self.cur_frame = None
        self.new_frame = threading.Event()
        self.start()
        
    def run(self):
        self.capture_feed()
            

    def capture_feed(self):
        device = self.acquire_device()
        print(device)
        time.sleep(5)
        while True:
            # try:
            #     for frame in device.decode(video=0):
            #         frame = frame.to_ndarray(format='rgb24')
            #         ret, self.cur_frame = cv2.imencode('.jpg', frame)
            #         print(ret)
            #         cv2.imwrite("test.jpg", frame)
            # except av.BlockingIOError:  
            #     pass

            success, frame = device.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                self.cur_frame = buffer.tobytes()
                self.new_frame.set()
                

    # def acquire_device(self):
    #     device_list = video.create_device_list()
    #     device_path = ""
    #     for device in device_list:
    #         if device.friendly_name == profile["video_device"]["friendly_name"]:
    #             device_path = device.path
# 
    #     if name == "posix":
    #         return av.open(device_path, format="video4linux2", container_options={
    #             "framerate": profile["video_device"]["fps"], 
    #             "video_size": profile["video_device"]["resolution"], 
    #             "input_format": profile["video_device"]["format"]
    #             })
# 
    #     else:
    #         raise RuntimeError("We're on something other than Linux, and that's not yet supported!")

    def acquire_device(self):
        device_list = video.create_device_list()
        device_path = ""
        for device in device_list:
            if device.friendly_name == profile["video_device"]["friendly_name"]:
                device_path = device.path

        if name == "posix":
            device = cv2.VideoCapture(device_path)  # Use default webcam (index 0)

        else:
            raise RuntimeError("We're on something other than Linux, and that's not yet supported!")

        device.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        device.set(cv2.CAP_PROP_FRAME_WIDTH, int(profile["video_device"]["resolution"].split('x')[0]))
        device.set(cv2.CAP_PROP_FRAME_HEIGHT, int(profile["video_device"]["resolution"].split('x')[1]))
        device.set(cv2.CAP_PROP_FPS, float(profile["video_device"]["fps"]))

        return device