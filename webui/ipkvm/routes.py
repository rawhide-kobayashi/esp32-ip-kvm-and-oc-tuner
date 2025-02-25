from ipkvm import app, ui
from ipkvm import frame_buffer
from flask import Response, render_template
import time
from ipkvm.util.mkb import HIDKeyCode
import serial
import json

def generate_frames():
    while True:
        frame_buffer.new_frame.wait()
        frame_buffer.new_frame.clear()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer.cur_frame + b'\r\n')
        
@ui.on('key_down')
def handle_keydown(data):
    test_json_a = {
      "mouseX": 99999,
      "mouseY": 99999,
      "mouse_down": ["rbutton", "lbutton"],
      "mouse_up": ["otherbutton"],
      "key_up": [],
      "key_down": [HIDKeyCode[data]]
    }

    print(HIDKeyCode[data])
    with serial.Serial('/dev/serial/by-id/usb-1a86_USB_Single_Serial_585D015807-if00', 115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE) as ser:
        ser.write(json.dumps(test_json_a).encode())

@ui.on('key_up')
def handle_keyup(data):
    test_json_a = {
      "mouseX": 99999,
      "mouseY": 99999,
      "mouse_down": ["rbutton", "lbutton"],
      "mouse_up": ["otherbutton"],
      "key_up": [HIDKeyCode[data]],
      "key_down": []
    }

    print(HIDKeyCode[data])
    with serial.Serial('/dev/serial/by-id/usb-1a86_USB_Single_Serial_585D015807-if00', 115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE) as ser:
        ser.write(json.dumps(test_json_a).encode())

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

"""@socketio.on("connect")
def kvm_client():
    ui.start_background_task(mkb_handler)"""
