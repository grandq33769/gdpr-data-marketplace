from socketio import ClientNamespace
from data_marketplace.client import client
from data_marketplace.utils.log import logging

log = logging.getLogger('data_marketplace.client.api')

class Data_Resgistration(ClientNamespace):
   def __init__(self, namespace, response):
      ClientNamespace.__init__(self, namespace)
      self.classname = self.__class__.__name__
      self.response = response
      
   def on_connect(self):
      log.info('%s - Connected', self.classname)
      super().emit('upload', {'data':'Hello {}'.format(self.classname)})

   def on_disconnect(self):
      log.info('%s - Disconnected', self.classname)

   def on_response(self, msg):
      log.info('Recevied Response: %s', msg['data'])

   def on_tx_confirm_response(self, msg):
      self.response.add(msg['tx_hash'])

class Data_Purchase(ClientNamespace):
   def __init__(self, namespace, response):
      ClientNamespace.__init__(self, namespace)
      self.classname = self.__class__.__name__
      self.response = response
      
   def on_connect(self):
      log.info('%s - Connected', self.classname)
      super().emit('upload', {'data':'Hello {}'.format(self.classname)})

   def on_disconnect(self):
      log.info('%s - Disconnected', self.classname)

   def on_response(self, msg):
      log.info('Recevied Response: %s', msg['data'])

   def on_purchase_confirm_response(self, msg):
      self.response.add(msg['tx_hash'])

   def on_confirmed(self, msg):
      log.info('Tx Confirmed: %s', msg['tx_hash'])

client.sio.register_namespace(Data_Resgistration('/data-registration', client.dr_confirm))
client.sio.register_namespace(Data_Purchase('/data-purchase', client.dp_confirm))