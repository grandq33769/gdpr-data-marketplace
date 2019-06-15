import os
from importlib import import_module as im
from data_marketplace.utils.log import logging
from data_marketplace.utils.threading import DMthread

log = logging.getLogger('data_marketplace.client.api')

class DataMarketplaceClient():

   def __init__(self, config, sio):
      self.cfg = config
      self.sio = sio
      self.send = dict()

   def run(self):
      self.sio.connect(self.cfg['Data_Marketplace']['host'])

   def registry(self, file):
      self.send = dict()
      if not self.validate(file):
         log.error('Validation failed in Data registration.')
         return
      namespace = self.sio.namespace_handlers['/data-registration']

      # Encryption of file
      try:
         encrypted = self.encrypt(file)
         log.info('Encrypted Data store in : %s', encrypted)
      except FileNotFoundError:
         log.error('Encryption Failure. File Not Found.', exc_info=True)
         return

      signature = self.sign(encrypted)
      tx_hash = self.sendTx(encrypted, signature)
      namespace.emit('tx_confirm', {'txhash': tx_hash, 'data': encrypted})

   def validate(self, file):
      return True

   def encrypt(self, file):
      log.info("Encryption of file.")
      key = self.cfg['Symmetric']['key']
      path = self.cfg['Data_Marketplace']['encrypt_path']
      encrypt_algo = self.cfg['Data_Marketplace']['symmetric']
      encrypt = im('data_marketplace.crypto.'+encrypt_algo).encrypt
      hash_algo = self.cfg['Data_Marketplace']['hash']
      hash_func = im('data_marketplace.crypto.'+hash_algo).hash_func
      dmt = DMthread()

      # Read File
      with open(file, 'rb') as f:
         contents = f.read()

      # Encryption
      encrypted = dmt.run(encrypt, key, contents)

      # Update Send Tx Data
      hexhash = hash_func(encrypted)
      self.send.update({'file_hash':hexhash})

      # Write File
      filename = hexhash + '.bin'
      path = os.path.join(path, filename)
      with open(path, 'wb') as f:
         f.write(encrypted)

      return path

   def sign(self, file):
      return 'aaa'

   def sendTx(self, encrypted, signature):
      return 'aaa'
