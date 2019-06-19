from flask import Flask
from flask_socketio import SocketIO
from data_marketplace.utils.iota import connect_iota

app = Flask(__name__, \
            instance_relative_config=True)
app.config.from_object('config.default')
app.config.from_pyfile('config.py')
socketio = SocketIO(app)
app.iota = connect_iota(app.config['IOTA_NODE'],
                        app.config['IOTA_SEED'])
