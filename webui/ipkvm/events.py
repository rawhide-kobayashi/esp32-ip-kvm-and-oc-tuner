from ipkvm import ui
from ipkvm import esp32_serial
from ipkvm.util.mkb import HIDKeyCode, HIDMouseScanCodes, GPIO
import time
from ipkvm.util import graphs
from ipkvm import states
from ipkvm import profile
import tomlkit

def power_switch(delay: float):
    msg = {
            "pwr": GPIO.HIGH.value
        }
    esp32_serial.mkb_queue.put(msg)
    time.sleep(delay)
    msg = {
            "pwr": GPIO.LOW.value
        }
    esp32_serial.mkb_queue.put(msg)

@ui.on("power_on")
def handle_poweron():
    states.model.power_on()

@ui.on("soft_power_off")
def handle_soft_poweroff():
    states.model.soft_shutdown()

@ui.on("hard_power_off")
def handle_hard_poweroff():
    states.model.hard_shutdown()

@ui.on("reboot_into_bios")
def handle_reboot_bios():
    states.model.reboot_into_bios()

@ui.on("clear_cmos")
def handle_clear_cmos():
    msg = {
            "cmos": GPIO.HIGH.value
        }
    esp32_serial.mkb_queue.put(msg)
    time.sleep(0.2)
    msg = {
            "cmos": GPIO.LOW.value
        }
    esp32_serial.mkb_queue.put(msg)

    time.sleep(1)

    power_switch(0.2)
    spam_delete_until_bios()
        
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

@ui.on("test_route")
def handle_test_route():
    graphs.test_route()

@ui.on("get_current_profile")
def handle_current_profile():
    return tomlkit.dumps(profile)