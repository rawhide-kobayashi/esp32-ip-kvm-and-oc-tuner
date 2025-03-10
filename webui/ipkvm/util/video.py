"""os.name provides the type of the operating system!"""
from os import name, listdir
import dataclasses
import re
import subprocess
import threading
import av
import av.container
import cv2
from ipkvm import logger

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

    if name == "posix":
        devices: list[str] = [f"/dev/{x}" for x in listdir("/dev/") if "video" in x]
        valid_devices = check_valid_device_linux(devices, valid_devices)

    elif name == "nt":
        # implement camera acqisition for windows
        pass

    return valid_devices

def get_video_formats(device: str):
    """
    Use v4l2-ctl (Linux) or FFplay (Windows) to get camera operating modes and sort by quality.
    """
    video_formats: dict[str, dict[str, list[str]]] = {}
    # Translates fourcc codec labels to the type that FFmpeg uses, and blacklists bad codecs.
    fourcc_format_translation: dict[str, str | None] = {
        "YUYV": None,
        "MJPG": "mjpeg"
    }

    if name == "posix":
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

    return video_formats

def create_device_list():
    """
    Create a complete device list including name, device ID, and available video formats.
    """
    device_names = scan_devices()
    device_list: list[VideoDevice] = []

    for device_name in device_names:
        device_list.append(VideoDevice(device_name, device_names[device_name], get_video_formats(device_names[device_name])))
        if len(device_list[-1].video_formats) == 0:
            device_list.pop()

    if len(device_list) > 0:
        logger.info(f"Found {len(device_list)} video devices.")
        return device_list

    else:
        raise RuntimeError("No video devices found on this system!")

# EZ DEBUGGING
if __name__ == '__main__':
    print(create_device_list())
