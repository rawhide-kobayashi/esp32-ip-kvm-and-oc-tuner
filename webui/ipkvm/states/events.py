from ipkvm.app import ui

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

@ui.on("test_route")
def handle_test_route():
    graphs.test_route()