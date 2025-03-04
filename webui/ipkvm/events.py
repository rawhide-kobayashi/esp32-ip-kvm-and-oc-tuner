from ipkvm import ui
from ipkvm import esp32_serial
from ipkvm.util.mkb import HIDKeyCode, HIDMouseScanCodes, GPIO
import time

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
    if esp32_serial.power_status == "off":
        power_switch(0.2)

@ui.on("soft_power_off")
def handle_soft_poweroff():
    if esp32_serial.power_status == "on":
        power_switch(0.2)

@ui.on("hard_power_off")
def handle_hard_poweroff():
    if esp32_serial.power_status == "on":
        power_switch(0.5)

@ui.on("reboot_into_bios")
def handle_reboot_bios():
    if esp32_serial.power_status == "on": # and OS state = offline
        power_switch(5)
        time.sleep(2)
        power_switch(0.2)
    
    else:
        power_switch(0.2)
    
    while time.time() - esp32_serial.bios_timer <= 5 or time.time() - esp32_serial.bios_timer >= 6:
        print(time.time() - esp32_serial.bios_timer)
        msg = {
            "key_down": HIDKeyCode.Delete.value
        }
        esp32_serial.mkb_queue.put(msg)
        time.sleep(0.1)
        msg = {
            "key_up": HIDKeyCode.Delete.value
        }
        esp32_serial.mkb_queue.put(msg)
        time.sleep(0.1)
        
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
