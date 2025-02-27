import serial
import sys
import datetime
import json
import time

test_json_a = {
  "mouseX": 99999,
  "mouseY": 99999,
  "mouse_down": ["rbutton", "lbutton"],
  "mouse_up": ["otherbutton"],
  "key_up": [],
  "key_down": [11, 12]
}

test_json_b = {
  "mouseX": 99999,
  "mouseY": 99999,
  "mouse_down": ["rbutton", "lbutton"],
  "mouse_up": ["otherbutton"],
  "key_up": [11, 12],
  "key_down": []
}

test_json_c = {
    "mouse_coord": {
        "x": 100,
        "y": 100,
    }
}

test_json_d = {
    "mouse_coord": {
        "x": 32000,
        "y": 32000,
    }
}

def read_serial(port):
    try:
        # Open the serial port
        with serial.Serial(port, 115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE) as ser:
            print(f"Listening on {port} at 115200 baud...")
            while True:
                # Read a line from the serial port
                while ser.in_waiting > 0:
                    line = str(ser.read().hex())
                    print(f'{datetime.datetime.now()} {line}')
                # Print the raw data
                ser.write(json.dumps(test_json_c).encode())
                time.sleep(1)
                ser.write(json.dumps(test_json_d).encode())
                time.sleep(1)
    except serial.SerialException as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit()

if __name__ == "__main__":
    #if len(sys.argv) != 2:
    #    print("Usage: python read_serial.py <port>")
    #    print("Example: python read_serial.py COM3 (Windows) or /dev/ttyUSB0 (Linux)")
    #    sys.exit(1)

    #port_name = sys.argv[1]
    read_serial('/dev/serial/by-id/usb-1a86_USB_Single_Serial_585D015807-if00')
