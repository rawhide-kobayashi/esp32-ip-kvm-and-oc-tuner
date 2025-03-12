from ipkvm.app import app
from ipkvm.util.video import frame_buffer
from flask import Response, render_template


def generate_frames():
    while True:
        frame_buffer.new_frame.wait()
        frame_buffer.new_frame.clear()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer.cur_frame + b'\r\n')

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
