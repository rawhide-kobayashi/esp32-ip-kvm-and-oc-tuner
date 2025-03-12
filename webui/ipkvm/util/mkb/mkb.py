from enum import IntEnum
from os import name, listdir
import serial
from ipkvm.app import logger, ui
from ipkvm.util.profiles import profile_manager
import threading
from queue import Queue
import json
import time
from collections.abc import Mapping
from .post_codes import POSTTextDef, POSTHex7Segment
from .scancodes import HIDKeyCode

class GPIO(IntEnum):
    LOW = 0
    HIGH = 1

class Esp32Serial(threading.Thread):
    def __init__(self):
        super().__init__()
        self.post_code_queue: Queue[str] = Queue()
        self.mkb_queue: Queue[Mapping[str, int | str | Mapping[str, int]]] = Queue()
        self._power_status = False
        self._last_post_code = "00"
        self.notify_code: str
        self.active_notification_request = threading.Event()
        self.post_code_notify = threading.Event()

        self.start()

    def run(self):
        profile_manager.restart_serial.wait()
        
        while True:
            profile_manager.restart_serial.clear()
            self.do_work()
        

    def do_work(self):
        device = self.get_device()
        with device as ser:
            while not profile_manager.restart_serial.is_set():
                while not self.mkb_queue.empty():
                    msg = self.mkb_queue.get()
                    ser.write(json.dumps(msg).encode())

                while ser.in_waiting > 0:
                    try:
                        line = json.loads(ser.readline().decode().strip())

                        if "pwr" in line:
                            self._power_status = line["pwr"]

                        elif "post_code" in line:
                            self._last_post_code = POSTHex7Segment[line["post_code"]]

                            ui.emit("update_seven_segment", POSTHex7Segment[line["post_code"]])
                            ui.emit("update_post_log", f"{POSTTextDef[line["post_code"]]}: {POSTHex7Segment[line["post_code"]]}")

                            if self.active_notification_request.is_set():
                                if self._last_post_code == self.notify_code:
                                    self.post_code_notify.set()
                                    self.active_notification_request.clear()

                    except json.JSONDecodeError:
                        continue

                    except UnicodeDecodeError:
                        continue
                
                time.sleep(0.01)

    def get_device(self):
        if name == "posix":
            assert isinstance(profile_manager.profile["server"], dict)
            return serial.Serial(f"/dev/serial/by-id/{profile_manager.profile["server"]["esp32_serial"]}", 115200,
                                 bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
        
        else:
            raise RuntimeError("Your OS is unsupported!")
        
    def ez_press_key(self, key: str):
        msg = msg = {
            "key_down": HIDKeyCode[key].value
        }

        self.mkb_queue.put(msg)

        msg = msg = {
            "key_up": HIDKeyCode[key].value
        }

        self.mkb_queue.put(msg)

    def get_device_list(self):
        if name == "posix":
            serial_devices = listdir("/dev/serial/by-id/")
 
        else:
            serial_devices = []
 
        return serial_devices

    @property
    def power_status(self):
        return self._power_status
    
    @property
    def last_post_code(self):
        return self._last_post_code
