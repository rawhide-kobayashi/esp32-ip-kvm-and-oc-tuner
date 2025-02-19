from ipkvm import ui
from ipkvm import frame_buffer
from flask import Response
import time

def generate_frames():
    while True:
        frame_buffer.new_frame.wait()
        frame_buffer.new_frame.clear()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer.cur_frame + b'\r\n')

@ui.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@ui.route('/')
def index():
    return """
    <html>
        <head>
            <title>Webcam Stream</title>
        </head>
        <body>
            <h1>Webcam Stream</h1>
            <img src="/video_feed">
        </body>
    </html>
    """