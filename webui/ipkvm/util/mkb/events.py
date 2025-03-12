from ipkvm.app import ui
from . import esp32_serial
from .scancodes import HIDKeyCode, HIDMouseScanCodes

@ui.on("get_serial_devices")
def handle_get_serial_devices():
    return esp32_serial.get_device_list()

@ui.on('key_down')
def handle_keydown(data: str):
    msg = {
      "key_down": HIDKeyCode[data].value
    }

    esp32_serial.mkb_queue.put(msg)

@ui.on('key_up')
def handle_keyup(data: str):
    msg = {
      "key_up": HIDKeyCode[data].value
    }

    esp32_serial.mkb_queue.put(msg)

@ui.on("mouse_move")
def handle_mousemove(data: list[int]):
    msg = {
      "mouse_coord": {
          "x": data[0],
          "y": data[1]
      }
    }

    esp32_serial.mkb_queue.put(msg)

@ui.on('mouse_down')
def handle_mousedown(data: int):
    msg = {
      "mouse_down": HIDMouseScanCodes[data]
    }
    
    esp32_serial.mkb_queue.put(msg)

@ui.on('mouse_up')
def handle_mouseup(data: int):
    msg = {
      "mouse_up": HIDMouseScanCodes[data]
    }
    
    esp32_serial.mkb_queue.put(msg)