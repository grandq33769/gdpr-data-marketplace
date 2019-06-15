from flask import render_template
from flask_socketio import Namespace, emit
from data_marketplace.server import app, socketio
from data_marketplace.utils.log import logging

log = logging.getLogger('data_marketplace.server.api')

@app.route('/')
def index():
   return render_template('index.html')

class Data_Registration(Namespace):
   def __init__(self, namespace):
      Namespace.__init__(self, namespace)
      self.classname = self.__class__.__name__

   def on_connect(self):
      log.info('%s - Connected', self.classname)

   def on_disconnect(self):
      log.info('%s - Disconnected', self.classname)

   def on_upload(self, data):
      log.info('Raw Data: %s', data)
      self.emit('response', data)
   
   def on_tx_confirm(self, data):
      log.info('Recevied Data Registration Confirm - Tx hash: %s', data['txhash'])
      self.emit('response', data)

socketio.on_namespace(Data_Registration('/data-registration'))