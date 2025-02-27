from ipkvm import app, ui
from ipkvm import frame_buffer, esp32_serial
from flask import Response, render_template
from ipkvm.util.mkb import HIDKeyCode, HIDMouseScanCodes

def generate_frames():
    while True:
        frame_buffer.new_frame.wait()
        frame_buffer.new_frame.clear()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer.cur_frame + b'\r\n')
        
@ui.on('key_down')
def handle_keydown(data: str):
    msg = {
      "key_down": HIDKeyCode[data].value
    }

    esp32_serial.mkb_queue.put(msg)

@ui.on('key_up')
def handle_keyup(data: str):
    msg = {
      "key_up": HIDKeyCode[data].value
    }

    esp32_serial.mkb_queue.put(msg)

@ui.on("mouse_move")
def handle_mousemove(data: list[int]):
    msg = {
      "mouse_coord": {
          "x": data[0],
          "y": data[1]
      }
    }

    esp32_serial.mkb_queue.put(msg)

@ui.on('mouse_down')
def handle_mousedown(data: int):
    msg = {
      "mouse_down": HIDMouseScanCodes[data]
    }
    
    esp32_serial.mkb_queue.put(msg)

@ui.on('mouse_up')
def handle_mouseup(data: int):
    msg = {
      "mouse_up": HIDMouseScanCodes[data]
    }
    
    esp32_serial.mkb_queue.put(msg)

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
