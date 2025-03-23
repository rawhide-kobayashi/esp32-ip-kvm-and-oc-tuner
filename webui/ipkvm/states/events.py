from ipkvm.app import ui
from . import model

from ipkvm.util.mkb import esp32_serial
from ipkvm.util.mkb.mkb import GPIO
import time

@ui.on("power_on")
def handle_poweron():
    model.power_on()

@ui.on("soft_power_off")
def handle_soft_poweroff():
    model.soft_shutdown()

@ui.on("hard_power_off")
def handle_hard_poweroff():
    model.hard_shutdown()

@ui.on("reboot_into_bios")
def handle_reboot_bios():
    model.reboot_into_bios()

@ui.on("clear_cmos")
def handle_clear_cmos():
    print("clear cmos and restart")
    msg = {
            "cmos": GPIO.HIGH.value
        }
    esp32_serial.mkb_queue.put(msg)
    time.sleep(0.2)
    msg = {
            "cmos": GPIO.LOW.value
        }
    esp32_serial.mkb_queue.put(msg)

    time.sleep(5)

    msg = {
            "pwr": GPIO.HIGH.value
        }
    esp32_serial.mkb_queue.put(msg)
    time.sleep(0.2)
    msg = {
            "pwr": GPIO.LOW.value
        }
    esp32_serial.mkb_queue.put(msg)

@ui.on("begin_automation")
def handle_begin_automation():
    model.begin_automation()
