from ipkvm import ui
from flask import Response

import cv2

camera = cv2.VideoCapture(0)  # Use default webcam (index 0)

# Get some basic properties
width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = camera.get(cv2.CAP_PROP_FPS)
format = camera.get(cv2.CAP_PROP_FORMAT)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
camera.set(cv2.CAP_PROP_FPS, 60)

print(f"Current resolution: {width}x{height}")
print(f"Current FPS: {fps}")
print(f"Current format: {format}")

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


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