import os
import argparse
from data_marketplace.server.api import app, socketio
# app.config.from_object('config.dev')

app.base_path = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
   socketio.run(app, host=app.config['HOST'], port=app.config['PORT'])
