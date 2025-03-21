from enum import IntEnum

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
