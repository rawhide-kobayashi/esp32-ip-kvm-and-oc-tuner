import subprocess
from flask import Flask, Response

app = Flask(__name__)

def generate():
    # FFmpeg command to capture the MJPEG stream without re-encoding.
    command = [
        'ffmpeg',
        '-f', 'v4l2',
        '-input_format', 'mjpeg', '-video_size', '1920x1080', '-framerate', '60.00',
        '-i', '/dev/video0',
        '-c', 'copy',
        '-f', 'mjpeg',
        'pipe:1'
    ]
    # Start the FFmpeg subprocess.
    process = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)
    data = b""
    while True:
        # Read raw bytes from FFmpeg's stdout.
        chunk = process.stdout.read(1024)
        if not chunk:
            break
        data += chunk

        # Look for complete JPEG frames by finding start and end markers.
        while True:
            start = data.find(b'\xff\xd8')  # JPEG start
            end = data.find(b'\xff\xd9')    # JPEG end
            if start != -1 and end != -1 and end > start:
                # Extract the JPEG frame.
                jpg = data[start:end+2]
                data = data[end+2:]
                # Yield the frame with the required multipart MJPEG boundaries.
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n')
            else:
                break

@app.route('/video_feed')
def video_feed():
    # Set the MIME type to multipart so browsers render it as an MJPEG stream.
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

