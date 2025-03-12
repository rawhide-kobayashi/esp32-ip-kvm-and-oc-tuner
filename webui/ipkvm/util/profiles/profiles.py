from os import listdir
import threading
import tomlkit
from ipkvm.app import logger, ui
from typing import TypedDict

class VideoDict(TypedDict):
    friendly_name: str
    resolution: str
    fps: str

class ServerDict(TypedDict):
    esp32_serial: str
    video_device: VideoDict

class ClientDict(TypedDict):
    hostname: str
    hwinfo_port: str
    overclocking: dict[str, dict[str, str]]

class ProfileDict(TypedDict):
    server: ServerDict
    client: ClientDict

class ProfileManager():
    def __init__(self):
        self.restart_serial = threading.Event()
        self.restart_video = threading.Event()
        self.restart_hwinfo = threading.Event()
        self._cur_profile_name: str = ""
        self._profiles = listdir("profiles")

        if len(self._profiles) == 0:
            logger.info("No profiles found, loading default profile.")
            # For all intents and purposes, in this code, the profiles are treated like dictionaries...
            # But idk how to make pylance happy in all cases here.
            self._profile: ProfileDict = self.load_default_profile() # type: ignore

        elif len(self._profiles) >= 1:
            logger.info(f"Autoloading a profile: {self._profiles[0]}...")
            
            self.load_profile(self._profiles[0]) # type: ignore
            
    def load_default_profile(self):
        with open("webui/ipkvm/templates/default.toml", 'r') as file:
            self._cur_profile_name = "default.toml"
            return tomlkit.parse(file.read())
    
    def load_profile(self, name: str):
        with open(f"profiles/{name}", 'r') as file:
            self._cur_profile_name = name
            self._profile = tomlkit.parse(file.read()) # type: ignore
            self.notify_all()
        
    def save_profile(self, new_profile: ProfileDict, name: str = ""):
        if name == "":
            name = self._cur_profile_name

        else:
            if not name.endswith(".toml"):
                name += ".toml"
            
        with open(f"profiles/{name}", 'w') as file:
            # In case you do a save-as and change the name!
            self._cur_profile_name = name
            tomlkit.dump(new_profile, file)
            self._profiles = listdir("profiles")

        if new_profile["server"]["esp32_serial"] != self._profile["server"]["esp32_serial"]:
            self.restart_serial.set()

        if new_profile["server"]["video_device"] != self._profile["server"]["video_device"]:
            self.restart_video.set()

        if (new_profile["client"]["hostname"] != self._profile["client"]["hostname"] or 
            new_profile["client"]["hwinfo_port"] != self._profile["client"]["hwinfo_port"]):
            self.restart_video.set()

        self._profile = new_profile

    def notify_all(self):
        self.restart_serial.set()
        self.restart_video.set()
        self.restart_hwinfo.set()

    @property
    def cur_profile_name(self):
        return self._cur_profile_name
    
    @property
    def profile_list(self):
        return self._profiles
    
    @property
    def profile(self):
        return self._profile
