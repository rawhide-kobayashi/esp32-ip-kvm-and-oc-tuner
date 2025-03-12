from os import listdir, name as os_name
import dataclasses
import re
import subprocess
import threading
import av
import av.container
import cv2
from ipkvm.app import logger, ui
from ipkvm.util.profiles import profile_manager
import time
from PIL import Image
import io

FourCCtoFFMPEG = {
    "yuyv422": "YUYV",
    "mjpeg": "MJPG"
}

class FrameBuffer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.buffer_lock = threading.Lock()
        img = Image.open("webui/ipkvm/static/Bsodwindows10.png")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        jpeg_bytes = buffer.getvalue()  # This contains the JPEG image as bytes
        self.cur_frame = jpeg_bytes
        self.new_frame = threading.Event()
        self.new_frame.set()
        self.start()
        
    def run(self):
        while not profile_manager.restart_video.is_set():
            img = Image.open("webui/ipkvm/static/Bsodwindows10.png")
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG")
            jpeg_bytes = buffer.getvalue()  # This contains the JPEG image as bytes
            self.cur_frame = jpeg_bytes
            self.new_frame.set()
            time.sleep(1)

        while True:
            profile_manager.restart_video.clear()
            self.capture_feed()
            

    def capture_feed(self):
        device = self.acquire_device()
        while not profile_manager.restart_video.is_set():
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
                # ret, buffer = cv2.imencode('.jpg', frame)
                # self.cur_frame = buffer.tobytes()
                # Convert BGR (OpenCV) to RGB (PIL)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert to PIL Image
                img = Image.fromarray(frame_rgb)

                # Save to a bytes buffer (for in-memory use)
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG")
                jpeg_bytes = buffer.getvalue()  # This contains the JPEG image as bytes
                self.cur_frame = jpeg_bytes

                self.new_frame.set()

        device.release()
                

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
        device_list = create_device_list()
        device_path = ""
        for device_name in device_list:
            if device_name == profile_manager.profile["server"]["video_device"]["friendly_name"]:
                device_path = device_list[device_name]["path"]
                break

        video_device = cv2.VideoCapture(device_path)  # Use default webcam (index 0)

        video_device.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*FourCCtoFFMPEG[device_list[device_name]["codec"]]))
        video_device.set(cv2.CAP_PROP_FRAME_WIDTH, int(profile_manager.profile["server"]["video_device"]["resolution"].split('x')[0]))
        video_device.set(cv2.CAP_PROP_FRAME_HEIGHT, int(profile_manager.profile["server"]["video_device"]["resolution"].split('x')[1]))
        video_device.set(cv2.CAP_PROP_FPS, float(profile_manager.profile["server"]["video_device"]["fps"]))

        return video_device

@dataclasses.dataclass
class VideoDevice:
    """
    Container for video input device data.
    """
    friendly_name: str
    path: str
    video_formats: dict[str, dict[str, list[float]]]

def check_valid_device_linux(devices: list[str], valid_cameras: dict[str, str]):
    """
    Uses v4l2-ctl to determine whether a video device actually provides video.
    Takes list of /dev/videoX strings.
    Returns a dictionary of /dev/videoX strings as keys and friendly device names as values.
    """
    for device in devices:
        cmd = ["v4l2-ctl", "-d", device, "--all"]
        lines = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               check=True).stdout.decode().strip().splitlines()

        if v4l2_check_capability(lines):
            for line in lines:
                if "Model" in line:
                    model_name = line.split(':')[1].strip()
                    valid_cameras.update({model_name: device})

    return valid_cameras

def v4l2_check_capability(lines: list[str]):
    """
    Checks if the provided stdout from v4l2-ctl identifies a device as a video capture device.
    """
    for i, line in enumerate(lines):
        if "Device Caps" in line:
            x = i
            while "Media Driver Info" not in lines[x]:
                x += 1
                if "Video Capture" in lines[x]:
                    return True

    return False

def scan_devices():
    """
    Creates a list of valid video devices and returns a dictionary of friendly names and device paths.
    """
    valid_devices: dict[str, str] = {}

    if os_name == "posix":
        devices: list[str] = [f"/dev/{x}" for x in listdir("/dev/") if "video" in x]
        valid_devices = check_valid_device_linux(devices, valid_devices)

    elif os_name == "nt":
        # implement camera acqisition for windows
        pass

    return valid_devices

def get_video_formats(device: str):
    """
    Use v4l2-ctl (Linux) or FFplay (Windows) to get camera operating modes and sort by quality.
    """
    video_formats: dict[str, dict[str, list[str]]] = {}

    # Translates fourcc codec labels to the type that FFmpeg uses
    fourcc_format_translation: dict[str, str | None] = {
        "YUYV": "yuyv422",
        "MJPG": "mjpeg"
    }

    ranked_formats = {
        "yuyv422": 1,
        "mjpeg": 2
    }

    if os_name == "posix":
        cmd = ["v4l2-ctl", "-d", device, "--list-formats-ext"]
        output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout.decode().strip()
        matches = re.finditer(r"(?P<format>'\S*')|(?P<resolution>\d*x\d*)|(?P<fps>\d*.\d* fps)", output)

        if matches:
            video_format = None
            resolution = None
            fps = None

            for match in matches:
                if re.match(r"'\S*'", match[0]):
                    video_format = fourcc_format_translation[match[0].strip('\'')]
                    resolution = None
                    fps = None
                elif re.match(r"\d*x\d*", match[0]):
                    resolution = match[0]
                    fps = None
                elif re.match(r"\d*.\d* fps", match[0]):
                    fps = match[0].rstrip(" fps")

                if video_format and resolution and fps:
                    if video_format not in video_formats:
                        video_formats.update({
                            video_format: {
                                resolution: [fps]
                            }
                        })
                    elif resolution not in video_formats[video_format]:
                        video_formats[video_format].update({
                            resolution: [fps]
                        })
                    else:
                        video_formats[video_format][resolution].append(fps)

        for ranked_format in ranked_formats:
            if ranked_format in video_formats:
                #video_formats = {key: video_formats[key] for key in video_formats if key == ranked_format}
                video_formats = {
                    "codec": ranked_format,
                    "formats": video_formats[ranked_format]
                }

    return video_formats

def create_device_list():
    """
    Create a complete device list including name, device ID, and available video formats.
    """
    device_names = scan_devices()
    device_list: list[VideoDevice] = []
    devices = {}

    for device_name in device_names:
        # device_list.append(VideoDevice(device_name, device_names[device_name], get_video_formats(device_names[device_name])))
        devices[device_name] = {
            "path": device_names[device_name]
        }
        devices[device_name].update(get_video_formats(device_names[device_name]))
        #if len(device_list[-1].video_formats) == 0:
        #    device_list.pop()

    if len(devices) > 0:
        # logger.info(f"Found {len(device_list)} video devices.")
        return devices

    else:
        raise RuntimeError("No video devices found on this system!")
    
@ui.on("get_video_devices")
def handle_get_video_devices():
    return create_device_list()
