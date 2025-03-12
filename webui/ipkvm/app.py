from flask import Flask
from flask_socketio import SocketIO
import logging

app = Flask(__name__)
ui = SocketIO(app)
logger = app.logger
logger.setLevel(logging.INFO)