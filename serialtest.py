import serial
import sys
import datetime

def read_serial(port):
    try:
        # Open the serial port
        with serial.Serial(port, 115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE) as ser:
            print(f"Listening on {port} at 115200 baud...")
            while True:
                # Read a line from the serial port
                line = ser.read()   
                # Print the raw data
                print(f'{datetime.datetime.now()} {line}')
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
    read_serial("/dev/serial/by-id/usb-1a86_USB_Single_Serial_585D015807-if00")
