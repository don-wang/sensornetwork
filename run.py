#!flask/bin/python
from app import app, socketio
# from app import socketio
# from flask_socketio import SocketIO

# socketio = SocketIO(app)

app.debug=True
app.threaded=True
app.config['SECRET_KEY'] = 'secret!'

socketio.run(app, host='0.0.0.0')
