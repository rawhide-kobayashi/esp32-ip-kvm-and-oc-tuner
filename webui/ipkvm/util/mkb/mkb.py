from enum import IntEnum
from os import name, listdir
import serial
from ipkvm.app import logger
from ipkvm.util.profiles import profile_manager
import threading
from queue import Queue
import json
import networkx as nx
import time
from collections.abc import Mapping
# from .post_codes import POSTTextDef, POSTHex7Segment
from .scancodes import ASCII2JS, HIDKeyCode
from ipkvm.util.types import MultiDiGraph, OverclockingDict

class GPIO(IntEnum):
    LOW = 0
    HIGH = 1

class Esp32Serial(threading.Thread):
    def __init__(self):
        super().__init__()
        # self.post_code_queue: Queue[str] = Queue()
        self.mkb_queue: Queue[Mapping[str, int | str | Mapping[str, int]]] = Queue()
        # self._power_status = False
        self._usb_status = False
        self._last_usb_status = False
        # self._last_post_code = "00"
        # self.notify_code: str
        # self.active_notification_request = threading.Event()
        # self.post_code_notify = threading.Event()

        self._key_delay = 0.2

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

                        # self._power_status = line["pwr"]
                        self._usb_status = line["usb"]

                        if self._usb_status != self._last_usb_status:
                            if self._usb_status:
                                logger.info("Client machine cleared POST.")
                            else:
                                logger.info("Client machine powered off.")

                            self._last_usb_status = self._usb_status

                        # elif "post_code" in line:
                        #     self._last_post_code = POSTHex7Segment[line["post_code"]]
# 
                        #     ui.emit("update_seven_segment", POSTHex7Segment[line["post_code"]])
                        #     ui.emit("update_post_log", f"{POSTTextDef[line["post_code"]]}: {POSTHex7Segment[line["post_code"]]}")
# 
                        #     if self.active_notification_request.is_set():
                        #         if self._last_post_code == self.notify_code:
                        #             self.post_code_notify.set()
                        #             self.active_notification_request.clear()
# 
                        #     print(f"{POSTTextDef[line["post_code"]]}: {POSTHex7Segment[line["post_code"]]}")

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
            raise RuntimeError("Your OS is unsupported at this time!")
        
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
    
    def _traverse_path(self, graph: MultiDiGraph, node_a: str, node_b: str):
        path = nx.shortest_path(graph, node_a, node_b)
        path_edges = list(zip(path[:-1], path[1:]))
        edge_path= [(u, v, graph[u][v]) for u, v in path_edges]

        for step in edge_path:
            if "initial_keypath" in step[2][0] and step[2][0]["visited"] == "false":
                keys = step[2][0]["initial_keypath"].split(',')
                # Type checker is simply wrong! This is the correct usage!
                graph.edges[step[0], step[1], 0]["visited"] = "true" # type: ignore

            else:
                keys = step[2][0]["keypath"].split(',')

            for key in keys:
                time.sleep(self._key_delay)
                self.ez_press_key(key)

    def _apply_setting(self, graph: MultiDiGraph, setting_node: str, new_value: str):
        if graph.nodes[setting_node]["option_type"] == "list":
            possible_values = graph.nodes[setting_node]["options"].split(',')
            key = graph.nodes[setting_node]["traversal_key"]

            time.sleep(self._key_delay)
            self.ez_press_key("Enter")

            for value in possible_values:
                time.sleep(self._key_delay)
                if value == new_value:
                    self.ez_press_key("Enter")
                    break

                else:
                    self.ez_press_key(key)

        elif graph.nodes[setting_node]["option_type"] == "field":
            for key in new_value:
                time.sleep(self._key_delay)
                self.ez_press_key(ASCII2JS[key])
            time.sleep(self._key_delay)
            self.ez_press_key("Enter")

        logger.info(f"Changed {setting_node} from {graph.nodes[setting_node]["value"]} to {new_value}!")
        graph.nodes[setting_node]["value"] = new_value



    def apply_all_settings(self, settings: OverclockingDict, graph: MultiDiGraph, current_node: str):
        for category in settings:
            for setting_node in settings[category]:
                if graph.nodes[setting_node]["value"] != settings[category][setting_node]:
                    self._traverse_path(graph, current_node, setting_node)
                    current_node = setting_node
                    self._apply_setting(graph, setting_node, settings[category][setting_node])

        return current_node

    # @property
    # def power_status(self):
    #     return self._power_status
    
    @property
    def usb_status(self):
        return self._usb_status
    
    # @property
    # def last_post_code(self):
    #     return self._last_post_code
