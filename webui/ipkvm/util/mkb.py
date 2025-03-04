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
        self.bios_timer = time.time()
        self.power_status = None

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
                            self.power_status = line["pwr"]

                        elif "post_code" in line:
                            # This code is what presents when you are in BIOS, but also... Other times.
                            # In another part of the script, we'll check to see if it's hung around for a few
                            # seconds. If so, we are in BIOS.
                            if POSTHex7Segment[line["post_code"]] != "Ab":
                                self.bios_timer = time.time()

                            ui.emit("update_seven_segment", POSTHex7Segment[line["post_code"]])

                    except json.JSONDecodeError:
                        continue

                    except UnicodeDecodeError:
                        continue
                    # self.post_code_queue.put(ser.read().hex())
                
                time.sleep(0.01)

    def get_device(self):
        if name == "posix":
            return serial.Serial(f"/dev/serial/by-id/{profile["esp32_serial"]}", 115200, bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
        
        else:
            raise RuntimeError("Your OS is unsupported!")
