from socketio import ClientNamespace
from data_marketplace.client import client
from data_marketplace.utils.log import logging

log = logging.getLogger('data_marketplace.client.api')

class Data_Resgistration(ClientNamespace):
   def __init__(self, namespace):
      ClientNamespace.__init__(self, namespace)
      self.classname = self.__class__.__name__
      
   def on_connect(self):
      log.info('%s - Connected', self.classname)
      super().emit('upload', {'data':'HelloWorld'})

   def on_disconnect(self):
      log.info('%s - Disconnected', self.classname)

   def on_response(self, message):
      log.info('Recevied Response: %s', message['data'])

client.sio.register_namespace(Data_Resgistration('/data-registration'))
