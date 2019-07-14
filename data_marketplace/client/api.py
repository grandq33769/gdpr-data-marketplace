from os.path import join
from socketio import ClientNamespace
from importlib import import_module as im
from data_marketplace.client import client
from data_marketplace.crypto.hash import _validate
from data_marketplace.utils.log import logging
from data_marketplace.utils.common import print_json
from data_marketplace.utils.thread import DMthread
from data_marketplace.utils.dlt import get_tx_ctx_by_bundle

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

   def on_download_response(self, msg):
      storage_path = client.cfg['Data_Marketplace']['storage_path']
      log.info('Storage Path: %s', storage_path)

      dmt = DMthread()
      log.info('Get Target Contents from Target Bundle ...')
      bundle_hash = msg['bundle_hash']
      log.info('Target Hash: %s\n', bundle_hash)
      ctx, sig = dmt.run(get_tx_ctx_by_bundle, client.iota, bundle_hash)
      log.info('Transaction Contents: %s\n'\
               'Signature: %s\n', print_json(ctx), print_json(sig))

      # Validation of recevied file and hash
      result = _validate(msg['file'], ctx['Contents']['Encrypted_Hash'], client.hash_algo)
      assert result
      log.info('Validation Result of Recevied File Hash: %s', result)

      # Decrypt AES key
      decrypted_key = client.asy_decrypt(msg['key'])
      log.info('Decrypted key: %s', decrypted_key)

      # Decrypt the file
      plain = client.sym_decrypt(decrypted_key, msg['file'])
      # TODO: file format determination
      file_name = ctx['Contents']['Data_Hash'] + '.txt'
      file_path = join(storage_path, 'received', file_name)
      with open(file_path, 'wb') as f:
         f.write(plain)
      self.response.add(msg['tx_hash'])

client.sio.register_namespace(Data_Resgistration('/data-registration', client.dr_confirm))
client.sio.register_namespace(Data_Purchase('/data-purchase', client.dp_confirm))