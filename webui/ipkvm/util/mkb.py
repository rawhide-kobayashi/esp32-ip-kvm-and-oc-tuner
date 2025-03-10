from enum import IntEnum
from os import name
import serial
from ipkvm import profile
import threading
from queue import Queue
import json
import time
from ipkvm import ui
from collections.abc import Mapping

# python can't use NUMBERS as enum keys?!

PoweredUpCodeDef = {
    1: "System is entering S1 sleep state",
    2: "System is entering S2 sleep state",
    3: "System is entering S3 sleep state",
    4: "System is entering S4 sleep state",
    5: "System is entering S5 sleep state",
    16: "System is waking up from the S1 sleep state",
    32: "System is waking up from the S2 sleep state",
    48: "System is waking up from the S3 sleep state",
    64: "System is waking up from the S4 sleep state",
    170: "System has transitioned into ACPI mode. Interrupt controller is in APIC mode",
    172: "System has transitioned into ACPI mode. Interrupt controller is in APIC mode",
    255: "Indicates a failure has occurred"
}

POSTTextDef = {
    0: "Not used",
    1: "Power on. Reset type detection (soft/hard)",
    2: "AP initialization before microcode loading",
    3: "System Agent initialization before microcode loading",
    4: "PCH initialization before microcode loading",
    5: "OEM initialization before microcode loading",
    6: "Microcode loading",
    7: "AP initialization after microcode loading",
    8: "System Agent initialization after microcode loading",
    9: "PCH initialization after microcode loading",
    10: "OEM initialization after microcode loading",
    11: "Cache initialization",
    12: "Reserved for future AMI SEC error codes",
    13: "Reserved for future AMI SEC error codes",
    14: "Microcode not found",
    15: "Microcode not loaded",
    16: "PEI Core is started",
    17: "Pre-memory CPU initialization is started",
    18: "Pre-memory CPU initialization (CPU module specific)",
    19: "Pre-memory CPU initialization (CPU module specific)",
    20: "Pre-memory CPU initialization (CPU module specific)",
    21: "Pre-memory System Agent initialization is started",
    22: "Pre-Memory System Agent initialization (System Agent module specific)",
    23: "Pre-Memory System Agent initialization (System Agent module specific)",
    24: "Pre-Memory System Agent initialization (System Agent module specific)",
    25: "Pre-memory PCH initialization is started",
    26: "Pre-memory PCH initialization (PCH module specific)",
    27: "Pre-memory PCH initialization (PCH module specific)",
    28: "Pre-memory PCH initialization (PCH module specific)",
    29: "OEM pre-memory initialization codes",
    30: "OEM pre-memory initialization codes",
    31: "OEM pre-memory initialization codes",
    32: "OEM pre-memory initialization codes",
    33: "OEM pre-memory initialization codes",
    34: "OEM pre-memory initialization codes",
    35: "OEM pre-memory initialization codes",
    36: "OEM pre-memory initialization codes",
    37: "OEM pre-memory initialization codes",
    38: "OEM pre-memory initialization codes",
    39: "OEM pre-memory initialization codes",
    40: "OEM pre-memory initialization codes",
    41: "OEM pre-memory initialization codes",
    42: "OEM pre-memory initialization codes",
    43: "Memory initialization. Serial Presence Detect (SPD) data reading",
    44: "Memory initialization. Memory presence detection",
    45: "Memory initialization. Programming memory timing information",
    46: "Memory initialization. Confi guring memory",
    47: "Memory initialization (other)",
    48: "Reserved for ASL",
    49: "Memory Installed",
    50: "CPU post-memory initialization is started",
    51: "CPU post-memory initialization. Cache initialization",
    52: "CPU post-memory initialization. Application Processor(s) (AP) initialization",
    53: "CPU post-memory initialization. Boot Strap Processor (BSP) selection",
    54: "CPU post-memory initialization. System Management Mode (SMM) initialization",
    55: "Post-Memory System Agent initialization is started",
    56: "Post-Memory System Agent initialization (System Agent module specific)",
    57: "Post-Memory System Agent initialization (System Agent module specific)",
    58: "Post-Memory System Agent initialization (System Agent module specific)",
    59: "Post-Memory PCH initialization is started",
    60: "Post-Memory PCH initialization (PCH module specific)",
    61: "Post-Memory PCH initialization (PCH module specific)",
    62: "Post-Memory PCH initialization (PCH module specific)",
    63: "OEM post memory initialization codes",
    64: "OEM post memory initialization codes",
    65: "OEM post memory initialization codes",
    66: "OEM post memory initialization codes",
    67: "OEM post memory initialization codes",
    68: "OEM post memory initialization codes",
    69: "OEM post memory initialization codes",
    70: "OEM post memory initialization codes",
    71: "OEM post memory initialization codes",
    72: "OEM post memory initialization codes",
    73: "OEM post memory initialization codes",
    74: "OEM post memory initialization codes",
    75: "OEM post memory initialization codes",
    76: "OEM post memory initialization codes",
    77: "OEM post memory initialization codes",
    78: "OEM post memory initialization codes",
    79: "DXE IPL is started",
    80: "Memory initialization error. Invalid memory type or incompatible memory speed",
    81: "Memory initialization error. SPD reading has failed",
    82: "Memory initialization error. Invalid memory size or memory modules do not match",
    83: "Memory initialization error. No usable memory detected",
    84: "Unspecified memory initialization error",
    85: "Memory not installed",
    86: "Invalid CPU type or Speed",
    87: "CPU mismatch",
    88: "CPU self test failed or possible CPU cache error",
    89: "CPU micro-code is not found or micro-code update is failed",
    90: "Internal CPU error",
    91: "reset PPI is not available",
    92: "Reserved for future AMI error codes",
    93: "Reserved for future AMI error codes",
    94: "Reserved for future AMI error codes",
    95: "Reserved for future AMI error codes",
    96: "DXE Core is started",
    97: "NVRAM initialization",
    98: "Installation of the PCH Runtime Services",
    99: "CPU DXE initialization is started",
    100: "CPU DXE initialization (CPU module specific)",
    101: "CPU DXE initialization (CPU module specific)",
    102: "CPU DXE initialization (CPU module specific)",
    103: "CPU DXE initialization (CPU module specific)",
    104: "PCI host bridge initialization",
    105: "System Agent DXE initialization is started",
    106: "System Agent DXE SMM initialization is started",
    107: "System Agent DXE initialization (System Agent module specific)",
    108: "System Agent DXE initialization (System Agent module specific)",
    109: "System Agent DXE initialization (System Agent module specific)",
    110: "System Agent DXE initialization (System Agent module specific)",
    111: "System Agent DXE initialization (System Agent module specific)",
    112: "PCH DXE initialization is started",
    113: "PCH DXE SMM initialization is started",
    114: "PCH devices initialization",
    115: "PCH DXE Initialization (PCH module specific)",
    116: "PCH DXE Initialization (PCH module specific)",
    117: "PCH DXE Initialization (PCH module specific)",
    118: "PCH DXE Initialization (PCH module specific)",
    119: "PCH DXE Initialization (PCH module specific)",
    120: "ACPI module initialization",
    121: "CSM initialization",
    122: "Reserved for future AMI DXE codes",
    123: "Reserved for future AMI DXE codes",
    124: "Reserved for future AMI DXE codes",
    125: "Reserved for future AMI DXE codes",
    126: "Reserved for future AMI DXE codes",
    127: "Reserved for future AMI DXE codes",
    128: "OEM DXE initialization codes",
    129: "OEM DXE initialization codes",
    130: "OEM DXE initialization codes",
    131: "OEM DXE initialization codes",
    132: "OEM DXE initialization codes",
    133: "OEM DXE initialization codes",
    134: "OEM DXE initialization codes",
    135: "OEM DXE initialization codes",
    136: "OEM DXE initialization codes",
    137: "OEM DXE initialization codes",
    138: "OEM DXE initialization codes",
    139: "OEM DXE initialization codes",
    140: "OEM DXE initialization codes",
    141: "OEM DXE initialization codes",
    142: "OEM DXE initialization codes",
    143: "OEM DXE initialization codes",
    144: "Boot Device Selection (BDS) phase is started",
    145: "Driver connecting is started",
    146: "PCI Bus initialization is started",
    147: "PCI Bus Hot Plug Controller Initialization",
    148: "PCI Bus Enumeration 32",
    149: "PCI Bus Request Resources",
    150: "PCI Bus Assign Resources",
    151: "Console Output devices connect",
    152: "Console input devices connect",
    153: "Super IO Initialization",
    154: "USB initialization is started",
    155: "USB Reset",
    156: "USB Detect",
    157: "USB Enable",
    158: "Reserved for future AMI codes",
    159: "Reserved for future AMI codes",
    160: "IDE initialization is started",
    161: "IDE Reset",
    162: "IDE Detect",
    163: "IDE Enable",
    164: "SCSI initialization is started",
    165: "SCSI Reset",
    166: "SCSI Detect",
    167: "SCSI Enable",
    168: "Setup Verifying Password",
    169: "Start of Setup",
    170: "Reserved for ASL",
    171: "Setup Input Wait",
    172: "Reserved for ASL",
    173: "Ready To Boot event",
    174: "Legacy Boot event",
    175: "Exit Boot Services event",
    176: "Runtime Set Virtual Address MAP Begin",
    177: "Runtime Set Virtual Address MAP End",
    178: "Legacy Option ROM Initialization",
    179: "System Reset",
    180: "USB hot plug",
    181: "PCI bus hot plug",
    182: "Clean-up of NVRAM",
    183: "Confi guration Reset (reset of NVRAM settings)",
    184: "Reserved for future AMI codes",
    185: "Reserved for future AMI codes",
    186: "Reserved for future AMI codes",
    187: "Reserved for future AMI codes",
    188: "Reserved for future AMI codes",
    189: "Reserved for future AMI codes",
    190: "Reserved for future AMI codes",
    191: "Reserved for future AMI codes",
    192: "OEM BDS initialization codes",
    193: "OEM BDS initialization codes",
    194: "OEM BDS initialization codes",
    195: "OEM BDS initialization codes",
    196: "OEM BDS initialization codes",
    197: "OEM BDS initialization codes",
    198: "OEM BDS initialization codes",
    199: "OEM BDS initialization codes",
    200: "OEM BDS initialization codes",
    201: "OEM BDS initialization codes",
    202: "OEM BDS initialization codes",
    203: "OEM BDS initialization codes",
    204: "OEM BDS initialization codes",
    205: "OEM BDS initialization codes",
    206: "OEM BDS initialization codes",
    207: "OEM BDS initialization codes",
    208: "CPU initialization error",
    209: "System Agent initialization error",
    210: "PCH initialization error",
    211: "Some of the Architectural Protocols are not available",
    212: "PCI resource allocation error. Out of Resources",
    213: "No Space for Legacy Option ROM",
    214: "No Console Output Devices are found",
    215: "No Console Input Devices are found",
    216: "Invalid password",
    217: "Error loading Boot Option (LoadImage returned error)",
    218: "Boot Option is failed (StartImage returned error)",
    219: "Flash update is failed",
    220: "Reset protocol is not available",
    221: "Reserved for future AMI progress codes",
    222: "Reserved for future AMI progress codes",
    223: "Reserved for future AMI progress codes",
    224: "S3 Resume is stared (S3 Resume PPI is called by the DXE IPL)",
    225: "S3 Boot Script execution",
    226: "Video repost",
    227: "OS S3 wake vector call",
    228: "Reserved for future AMI progress codes",
    229: "Reserved for future AMI progress codes",
    230: "Reserved for future AMI progress codes",
    231: "Reserved for future AMI progress codes",
    232: "S3 Resume Failed",
    233: "S3 Resume PPI not Found",
    234: "S3 Resume Boot Script Error",
    235: "S3 OS Wake Error",
    236: "Reserved for future AMI error codes 31",
    237: "Reserved for future AMI error codes 31",
    238: "Reserved for future AMI error codes 31",
    239: "Reserved for future AMI error codes 31",
    240: "Recovery condition triggered by firmware (Auto recovery)",
    241: "Recovery condition triggered by user (Forced recovery)",
    242: "Recovery process started",
    243: "Recovery firmware image is found",
    244: "Recovery firmware image is loaded",
    245: "Reserved for future AMI progress codes",
    246: "Reserved for future AMI progress codes",
    247: "Reserved for future AMI progress codes",
    248: "Recovery PPI is not available",
    249: "Recovery capsule is not found",
    250: "Invalid recovery capsule",
    251: "Reserved for future AMI error codes",
    252: "Reserved for future AMI error codes",
    253: "Reserved for future AMI error codes",
    254: "Reserved for future AMI error codes",
    255: "Indicates a failure has occurred"
}

POSTHex7Segment = {
    0: "00",
    1: "01",
    2: "02",
    3: "03",
    4: "04",
    5: "05",
    6: "06",
    7: "07",
    8: "08",
    9: "09",
    10: "0A",
    11: "0b",
    12: "0C",
    13: "0d",
    14: "0E",
    15: "0F",
    16: "10",
    17: "11",
    18: "12",
    19: "13",
    20: "14",
    21: "15",
    22: "16",
    23: "17",
    24: "18",
    25: "19",
    26: "1A",
    27: "1b",
    28: "1C",
    29: "1d",
    30: "1E",
    31: "1F",
    32: "20",
    33: "21",
    34: "22",
    35: "23",
    36: "24",
    37: "25",
    38: "26",
    39: "27",
    40: "28",
    41: "29",
    42: "2A",
    43: "2b",
    44: "2C",
    45: "2d",
    46: "2E",
    47: "2F",
    48: "30",
    49: "31",
    50: "32",
    51: "33",
    52: "34",
    53: "35",
    54: "36",
    55: "37",
    56: "38",
    57: "39",
    58: "3A",
    59: "3b",
    60: "3C",
    61: "3d",
    62: "3E",
    63: "3F",
    64: "40",
    65: "41",
    66: "42",
    67: "43",
    68: "44",
    69: "45",
    70: "46",
    71: "47",
    72: "48",
    73: "49",
    74: "4A",
    75: "4b",
    76: "4C",
    77: "4d",
    78: "4E",
    79: "4F",
    80: "50",
    81: "51",
    82: "52",
    83: "53",
    84: "54",
    85: "55",
    86: "56",
    87: "57",
    88: "58",
    89: "59",
    90: "5A",
    91: "5b",
    92: "5C",
    93: "5d",
    94: "5E",
    95: "5F",
    96: "60",
    97: "61",
    98: "62",
    99: "63",
    100: "64",
    101: "65",
    102: "66",
    103: "67",
    104: "68",
    105: "69",
    106: "6A",
    107: "6b",
    108: "6C",
    109: "6d",
    110: "6E",
    111: "6F",
    112: "70",
    113: "71",
    114: "72",
    115: "73",
    116: "74",
    117: "75",
    118: "76",
    119: "77",
    120: "78",
    121: "79",
    122: "7A",
    123: "7b",
    124: "7C",
    125: "7d",
    126: "7E",
    127: "7F",
    128: "80",
    129: "81",
    130: "82",
    131: "83",
    132: "84",
    133: "85",
    134: "86",
    135: "87",
    136: "88",
    137: "89",
    138: "8A",
    139: "8b",
    140: "8C",
    141: "8d",
    142: "8E",
    143: "8F",
    144: "90",
    145: "91",
    146: "92",
    147: "93",
    148: "94",
    149: "95",
    150: "96",
    151: "97",
    152: "98",
    153: "99",
    154: "9A",
    155: "9b",
    156: "9C",
    157: "9d",
    158: "9E",
    159: "9F",
    160: "A0",
    161: "A1",
    162: "A2",
    163: "A3",
    164: "A4",
    165: "A5",
    166: "A6",
    167: "A7",
    168: "A8",
    169: "A9",
    170: "AA",
    171: "Ab",
    172: "AC",
    173: "Ad",
    174: "AE",
    175: "AF",
    176: "b0",
    177: "b1",
    178: "b2",
    179: "b3",
    180: "b4",
    181: "b5",
    182: "b6",
    183: "b7",
    184: "b8",
    185: "b9",
    186: "bA",
    187: "bb",
    188: "bC",
    189: "bd",
    190: "bE",
    191: "bF",
    192: "C0",
    193: "C1",
    194: "C2",
    195: "C3",
    196: "C4",
    197: "C5",
    198: "C6",
    199: "C7",
    200: "C8",
    201: "C9",
    202: "CA",
    203: "Cb",
    204: "CC",
    205: "Cd",
    206: "CE",
    207: "CF",
    208: "d0",
    209: "d1",
    210: "d2",
    211: "d3",
    212: "d4",
    213: "d5",
    214: "d6",
    215: "d7",
    216: "d8",
    217: "d9",
    218: "dA",
    219: "db",
    220: "dC",
    221: "dd",
    222: "dE",
    223: "dF",
    224: "E0",
    225: "E1",
    226: "E2",
    227: "E3",
    228: "E4",
    229: "E5",
    230: "E6",
    231: "E7",
    232: "E8",
    233: "E9",
    234: "EA",
    235: "Eb",
    236: "EC",
    237: "Ed",
    238: "EE",
    239: "EF",
    240: "F0",
    241: "F1",
    242: "F2",
    243: "F3",
    244: "F4",
    245: "F5",
    246: "F6",
    247: "F7",
    248: "F8",
    249: "F9",
    250: "FA",
    251: "Fb",
    252: "FC",
    253: "Fd",
    254: "FE",
    255: "FF"
}

HIDMouseScanCodes = {
    0: 1,
    2: 2,
    1: 4,
    3: 8,
    4: 16
}

ASCII2JS= {
    "1": "Digit1",
    "2": "Digit2",
    "3": "Digit3",
    "4": "Digit4",
    "5": "Digit5",
    "6": "Digit6",
    "7": "Digit7",
    "8": "Digit8",
    "9": "Digit9",
    "0": "Digit0",

    ".": "Period"
}

class GPIO(IntEnum):
    LOW = 0
    HIGH = 1

# God Bless CHADGPT
class HIDKeyCode(IntEnum):
    """
    Enum that translates modern JS key.code andvalues to HID scancodes.
    """
    # Letter keys (A-Z)
    KeyA = 4
    KeyB = 5
    KeyC = 6
    KeyD = 7
    KeyE = 8
    KeyF = 9
    KeyG = 10
    KeyH = 11
    KeyI = 12
    KeyJ = 13
    KeyK = 14
    KeyL = 15
    KeyM = 16
    KeyN = 17
    KeyO = 18
    KeyP = 19
    KeyQ = 20
    KeyR = 21
    KeyS = 22
    KeyT = 23
    KeyU = 24
    KeyV = 25
    KeyW = 26
    KeyX = 27
    KeyY = 28
    KeyZ = 29

    # Number keys (top row)
    Digit1 = 30
    Digit2 = 31
    Digit3 = 32
    Digit4 = 33
    Digit5 = 34
    Digit6 = 35
    Digit7 = 36
    Digit8 = 37
    Digit9 = 38
    Digit0 = 39

    # Control keys
    Enter = 40
    Escape = 41
    Backspace = 42
    Tab = 43
    Space = 44

    Minus = 45
    Equal = 46
    BracketLeft = 47
    BracketRight = 48
    Backslash = 49

    # Punctuation keys
    Semicolon = 51
    Quote = 52
    Backquote = 53
    Comma = 54
    Period = 55
    Slash = 56

    CapsLock = 57

    # Function keys (F1-F12)
    F1 = 58
    F2 = 59
    F3 = 60
    F4 = 61
    F5 = 62
    F6 = 63
    F7 = 64
    F8 = 65
    F9 = 66
    F10 = 67
    F11 = 68
    F12 = 69

    PrintScreen = 70
    ScrollLock = 71
    Pause = 72

    Insert = 73
    Home = 74
    PageUp = 75

    Delete = 76
    End = 77
    PageDown = 78

    ArrowRight = 79
    ArrowLeft = 80
    ArrowDown = 81
    ArrowUp = 82

    # Numpad keys
    NumLock = 83
    NumpadDivide = 84
    NumpadMultiply = 85
    NumpadSubtract = 86
    NumpadAdd = 87
    NumpadEnter = 88
    Numpad1 = 89
    Numpad2 = 90
    Numpad3 = 91
    Numpad4 = 92
    Numpad5 = 93
    Numpad6 = 94
    Numpad7 = 95
    Numpad8 = 96
    Numpad9 = 97
    Numpad0 = 98
    NumpadDecimal = 99

    # Additional keys
    IntlBackslash = 100
    ContextMenu = 101
    Power = 102

    # Modifier keys
    ControlLeft = 224
    ShiftLeft = 225
    AltLeft = 226
    MetaLeft = 227  # Windows / Command key (left)
    ControlRight = 228
    ShiftRight = 229
    AltRight = 230
    MetaRight = 231  # Windows / Command key (right)

class Esp32Serial(threading.Thread):
    def __init__(self):
        super().__init__()
        self.post_code_queue: Queue[str] = Queue()
        self.mkb_queue: Queue[Mapping[str, int | str | Mapping[str, int]]] = Queue()
        self.change_serial_device = threading.Event()
        self.device = self.get_device()
        self._power_status = False
        self._last_post_code = "00"
        self.notify_code: str
        self.active_notification_request = threading.Event()
        self.post_code_notify = threading.Event()

        self.start()

    def run(self):
        with self.device as ser:
            while True:
            # if self.change_serial_device.is_set():
            #    self.change_serial_device.clear()
            #    self.device = self.get_device()
            
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
                    # self.post_code_queue.put(ser.read().hex())
                
                time.sleep(0.01)

    def get_device(self):
        if name == "posix":
            return serial.Serial(f"/dev/serial/by-id/{profile["server"]["esp32_serial"]}", 115200, bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
        
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

    @property
    def power_status(self):
        return self._power_status
    
    @property
    def last_post_code(self):
        return self._last_post_code
