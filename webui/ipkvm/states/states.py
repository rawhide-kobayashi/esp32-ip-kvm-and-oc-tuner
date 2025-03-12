from enum import Enum
import time
from transitions.experimental.utils import with_model_definitions, add_transitions, transition
from transitions.extensions import GraphMachine
from ipkvm.util import esp32_serial
from ipkvm.util.mkb import GPIO, HIDKeyCode
from ipkvm.app import logging, ui

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

    state: State = State.IdleWaitingForInput

    # TRANSITION DEFINITIONS
    @add_transitions(transition([State.PoweredOff, State.IdleWaitingForInput], State.POST, after="_power_on",
                                unless="client_powered"))
    def power_on(self): ...

    @add_transitions(transition(State.POST, State.WaitingForOS))
    def enter_os(self): ...
 
    @add_transitions(transition(State.WaitingForOS, State.WaitingForHWInfo))
    def os_booted(self): ...
 
    @add_transitions(transition(State.WaitingForHWInfo, State.OCTypeDecision))
    def hwinfo_available(self): ...
 
    @add_transitions(transition(State.POST, State.EnterBIOS, after="_enter_bios"))
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

    @add_transitions(transition([State.BIOSSetup, State.IdleWaitingForInput, State.BootLoop, State.POST,
                                 State.WaitingForOS, State.RoughMulticoreUndervolt,
                                 State.PreciseMulticoreUndervolt, State.SingleCoreTuning],
                                 State.PoweredOff, after="_hard_shutdown", conditions="client_powered"))
    def hard_shutdown(self): ...

    @add_transitions(transition(State.IdleWaitingForInput, State.PoweredOff,
                                after="_soft_shutdown", conditions="client_powered"))
    def soft_shutdown(self): ...

    @add_transitions(transition(State.OCTypeDecision, State.RoughMulticoreUndervolt))
    def rough_multicore_undervolt(self): ...

    @add_transitions(transition(State.OCTypeDecision, State.PreciseMulticoreUndervolt))
    def precise_multicore_undervolt(self): ...

    @add_transitions(transition(State.OCTypeDecision, State.SingleCoreTuning))
    def single_core_tuning(self): ...

    
    # PROPERTIES GO HERE
    @property
    def client_powered(self):
        return esp32_serial.power_status
    
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
    def _power_on(self):
        self._power_switch(0.2)

        # Unknown code definition, but this is the first consistent one indicating POST has started.
        while esp32_serial.last_post_code != "FC":
            pass

    def _hard_shutdown(self):
        self._power_switch(5)
        while self.client_powered:
            pass
        
    def _soft_shutdown(self):
        self._power_switch(0.2)
        while self.client_powered:
            pass

    def _enter_bios(self):
        # Wait until the POST has progressed far enough for USB devices to be loaded and options to be imminent
        esp32_serial.notify_code = "45"
        esp32_serial.active_notification_request.set()
        esp32_serial.post_code_notify.wait()
        esp32_serial.post_code_notify.clear()

        # Spam delete until the BIOS is loaded
        esp32_serial.notify_code = "Ab"
        esp32_serial.active_notification_request.set()
        while not esp32_serial.post_code_notify.is_set():
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

        esp32_serial.post_code_notify.clear()

        # Wait a few seconds for the BIOS to become responsive
        time.sleep(5)

    # OTHER FUNCTIONS GO HERE
    def reboot_into_bios(self):
        if self.client_powered:
            if self.state is State.IdleWaitingForInput:
                self.soft_shutdown()

            else:
                self.hard_shutdown()

        self.power_on()
        self.enter_bios()


@with_model_definitions
class MyMachine(GraphMachine):
    pass

model = Overclocking()
machine = MyMachine(model, states=State, initial=model.state)

machine.get_graph().draw('my_state_diagram.svg', prog='dot')
