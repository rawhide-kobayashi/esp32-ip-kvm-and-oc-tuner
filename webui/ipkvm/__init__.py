from os import name, listdir
from flask import Flask
from flask_socketio import SocketIO
import json
import logging

app = Flask(__name__)
ui = SocketIO(app)
logger = app.logger
logger.setLevel(logging.INFO)

def new_profile():
    device_list = video.create_device_list()
    print(f"Detected {len(device_list)} video devices on your system.")
    print("Please enter the number of your preferred video device.")
    for i, device in enumerate(device_list):
        print(f"{i + 1}. {device.friendly_name}")

    device = int(input("> ")) - 1

    if len(device_list[device].video_formats) > 1:
        print("Please enter your preferred video input format: ")
        for i, format in enumerate(device_list[device].video_formats):
            print(f"{i + 1}. {format}")

        format = list(device_list[device].video_formats.keys())[int(input("> ")) - 1]

    else:
        format = next(iter(device_list[device].video_formats))
        print(f"Video input format auto-detected as {format}!")

    print("Please enter the number of your preferred video resolution.")

    for i, resolution in enumerate(device_list[device].video_formats[format]):
        print(f"{i + 1}. {resolution}")

    resolution = list(device_list[device].video_formats[format].keys())[int(input("> ")) - 1]

    print("Please enter the number of your preferred video refresh rate.")

    for i, fps in enumerate(device_list[device].video_formats[format][resolution]):
        print(f"{i + 1}. {fps}")

    fps = str(device_list[device].video_formats[format][resolution][int(input("> ")) - 1])

    if name == "posix":
        serial_devices = listdir("/dev/serial/by-id/")

    else:
        serial_devices = []

    if len(serial_devices) > 1:
        print("Please enter the number of your preferred ESP32 serial device.")
        for i, serial_device in enumerate(serial_devices):
            print(f"{i + 1}. {serial_device}")

        serial_device = serial_devices[int(input("> ")) - 1]

    elif len(serial_devices) == 1:
        print(f"ESP32 auto-detected as {serial_devices[0]}!")
        serial_device = serial_devices[0]

    else:
        raise RuntimeError("No valid ESP32 devices connected!")

    print("Please enter your new profile name.")
    profile_name = input("> ")

    profile: dict[str, str | dict[str, str]] = {
        "video_device": {
            "friendly_name": device_list[device].friendly_name,
            "format": format,
            "resolution": resolution,
            "fps": fps
        },

        "esp32_serial": serial_device
    }
    
    with open(f"profiles/{profile_name}.json", 'w') as file:
        json.dump(profile, file)

    return profile

if len(listdir("profiles")) == 0:
        print("No profiles found, entering runtime profile configuration...")
        profile = new_profile()

elif len(listdir("profiles")) == 1:
    print(f"Only one profile found, autoloading {listdir("profiles")[0]}...")
    with open(f"profiles/{listdir("profiles")[0]}", 'r') as file:
        profile = json.load(file)
        print(profile)

from ipkvm.util import video
from ipkvm import feed

frame_buffer = feed.FrameBuffer()

from ipkvm import routes
