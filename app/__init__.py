from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)
socketio = SocketIO(app, async_mode='threading')

from app import views
