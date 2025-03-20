from enum import Enum
import time
from transitions.experimental.utils import with_model_definitions, add_transitions, transition
from transitions.extensions import GraphMachine
from ipkvm.util.mkb import esp32_serial
from ipkvm.util.mkb.mkb import GPIO
from ipkvm.util.mkb.scancodes import HIDKeyCode
from ipkvm.app import logging, ui

logging.basicConfig(level=logging.INFO)

class State(Enum):
    PoweredOff = "powered off"
    EnterBIOS = "enter bios"
    BIOSSetup = "bios setup"
    WaitingForOS = "waiting for os"
    OCTypeDecision = "next process decision"
    RoughMulticoreUndervolt = "rough multicore undervolting"
    PreciseMulticoreUndervolt = "precise multicore undervolting"
    POST = "power on self test"
    WaitingForHWInfo = "waiting for hwinfo"
    BootLoop = "boot loop"
    IdleWaitingForInput = "idle, waiting for input"
    SingleCoreTuning = "single core tuning"

class Overclocking:

    # wait for power status ig
    time.sleep(0.5)
    if esp32_serial.usb_status:
        state: State = State.IdleWaitingForInput
    else:
        state: State = State.PoweredOff

    _enter_bios_flag = False
    _running_automatic = False

    _current_BIOS_location = "EZ Mode"

    # TRANSITION DEFINITIONS
    @add_transitions(transition(State.PoweredOff, State.POST, unless="client_powered"))
    def power_on(self): ...

    @add_transitions(transition(State.POST, State.WaitingForOS))
    def wait_os(self): ...
 
    @add_transitions(transition(State.WaitingForOS, State.WaitingForHWInfo))
    def os_booted(self): ...
 
    @add_transitions(transition(State.WaitingForHWInfo, State.OCTypeDecision))
    def hwinfo_available(self): ...
 
    @add_transitions(transition(State.POST, State.EnterBIOS))
    def enter_bios(self): ...
 
    @add_transitions(transition(State.EnterBIOS, State.BIOSSetup))
    def start_bios_setup(self): ...
 
    @add_transitions(transition(State.BIOSSetup, State.POST))
    def finished_bios_setup(self): ...
 
    @add_transitions(transition(State.IdleWaitingForInput, State.WaitingForHWInfo))
    def begin_automation(self): ...
 
    @add_transitions(transition(State.POST, State.BootLoop))
    def unsuccessful_post(self): ...
 
    @add_transitions(transition(State.BootLoop, State.PoweredOff))
    def trigger_cmos_reset(self): ...
 
    @add_transitions(transition([State.IdleWaitingForInput, State.RoughMulticoreUndervolt,
                                 State.PreciseMulticoreUndervolt, State.SingleCoreTuning], State.POST))
    def reboot(self): ...

    @add_transitions(transition([State.BIOSSetup, State.IdleWaitingForInput, State.POST, State.WaitingForOS,
                                 State.RoughMulticoreUndervolt, State.PreciseMulticoreUndervolt, 
                                 State.SingleCoreTuning], State.PoweredOff, after="_hard_shutdown"))
    def hard_shutdown(self): ...

    @add_transitions(transition(State.IdleWaitingForInput, State.PoweredOff,
                                after="_soft_shutdown"))
    def soft_shutdown(self): ...

    @add_transitions(transition(State.OCTypeDecision, State.RoughMulticoreUndervolt))
    def rough_multicore_undervolt(self): ...

    @add_transitions(transition(State.OCTypeDecision, State.PreciseMulticoreUndervolt))
    def precise_multicore_undervolt(self): ...

    @add_transitions(transition(State.OCTypeDecision, State.SingleCoreTuning))
    def single_core_tuning(self): ...

    @add_transitions(transition([State.POST, State.EnterBIOS], State.IdleWaitingForInput))
    def go_idle(self): ...

    
    # PROPERTIES GO HERE
    @property
    def client_powered(self):
        return esp32_serial.usb_status
    
    @property
    def current_BIOS_location(self):
        return self._current_BIOS_location
    
    @current_BIOS_location.setter
    def current_BIOS_location(self, value: str):
        if type(value) == str:
            self._current_BIOS_location = value

        else:
            raise ValueError("Attempted to set the current BIOS location to a non-string value!")

    # STATE ENTRY FUNCTIONS
    def on_enter_POST(self):
        post_timer = time.time()

        # If five minutes passes with no USB availability, something has gone terribly wrong...
        while time.time() - post_timer <= 300 and not esp32_serial.usb_status:
            pass

        if not esp32_serial.usb_status:
            self.unsuccessful_post()

        else:
            if self._enter_bios_flag:
                self.enter_bios()

            elif self._running_automatic:
                self.wait_os()

            else:
                self.go_idle()

    def on_enter_EnterBIOS(self):
        # # Wait until the POST has progressed far enough for USB devices to be loaded and options to be imminent
        # esp32_serial.notify_code = "45"
        # esp32_serial.active_notification_request.set()
        # esp32_serial.post_code_notify.wait()
        # esp32_serial.post_code_notify.clear()
# 
        # # Spam delete until the BIOS is loaded
        # esp32_serial.notify_code = "Ab"
        # esp32_serial.active_notification_request.set()
        # while not esp32_serial.post_code_notify.is_set():
        
        spam_timer = time.time()

        # Crushed by my lack of consistent access to BIOS post codes, we simply take our time...
        while time.time() - spam_timer <= 10:
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

        # esp32_serial.post_code_notify.clear()

        # Wait a few seconds for the BIOS to become responsive
        time.sleep(5)

        self._enter_bios_flag = False

        if self._running_automatic:
            self.start_bios_setup()

        else:
            self.go_idle()

    # STATE EXIT FUNCTIONS
    def on_exit_PoweredOff(self):
        self._power_switch(0.2)        
    
    # UTILITY FUNCTIONS GO HERE
    def _power_switch(self, delay: float):
        msg = {
            "pwr": GPIO.HIGH.value
        }
        esp32_serial.mkb_queue.put(msg)
        time.sleep(delay)
        msg = {
                "pwr": GPIO.LOW.value
            }
        esp32_serial.mkb_queue.put(msg)

    # FUNCTIONS TRIGGERED BY STATE CHANGES
    def _hard_shutdown(self):
        self._power_switch(5)
        
    def _soft_shutdown(self):
        self._power_switch(0.2)
        while esp32_serial.usb_status:
            pass

        # Wait a few seconds to REALLY be sure we're powered off...
        time.sleep(10)

    # OTHER FUNCTIONS GO HERE
    def reboot_into_bios(self):
        if esp32_serial.usb_status:
            if self.state is State.IdleWaitingForInput:
                self.soft_shutdown()

            else:
                self.hard_shutdown()

        self._enter_bios_flag = True
        self.power_on()


@with_model_definitions
class MyMachine(GraphMachine):
    pass
