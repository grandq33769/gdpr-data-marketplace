import os
import json
import base64
from threading import Thread
from flask import render_template
from flask_socketio import Namespace, emit
from importlib import import_module as im
from data_marketplace.server import app, socketio
from data_marketplace.crypto.hash import _hash, _validate
from data_marketplace.utils.common import print_json, read_file_byte, write_file_byte, to_byte
from data_marketplace.utils.thread import DMthread
from data_marketplace.utils.dlt import get_tx_ctx, get_tx_ctx_by_bundle, wait_tx_confirmed
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
      tx_hash = data['tx_hash']
      log.info('Recevied Data Registration Confirm - Tx hash: %s', tx_hash)

      # Get Transaction Contents
      dmt = DMthread()
      msg, sig = dmt.run(get_tx_ctx, app.iota, tx_hash)
      log.info('Transaction Contents: %s\n'\
               'Signature: %s\n', print_json(msg), print_json(sig))

      # Write File
      write_path = os.path.join(app.base_path, app.config['STORAGE_PATH'])
      encrypted_path, key_path = dmt.run(_write_tx_confirm,
                                         write_path,
                                         data, msg)

      # Validation of contents hash
      result = _validate(str(msg['Contents']),
                         msg['Contents_Hash'],
                         app.config['HASH'])
      assert result
      log.info('Successful Validation of Contents Hash.')

      # Verify the signature
      asymmetric = app.config['ASYMMETRIC']
      digest = _hash(str(msg['Contents']), app.config['HASH'])
      sig_byte = base64.b64decode(to_byte(sig['Signature']))
      verify = im('data_marketplace.crypto.' + asymmetric).verify
      verified = verify(key_path, digest, sig_byte)
      assert verified
      log.info('Verification Result of Signature: %s', verified)

      # Validation of encrypted file
      encrypted = read_file_byte(encrypted_path)
      result = _validate(encrypted,
                         msg['Contents']['Encrypted_Hash'],
                         app.config['HASH'])
      assert result
      log.info('Successful Validation of Encrypted File.')

      self.emit('tx_confirm_response',
                {'message': 'Successful Confirmation',
                 'tx_hash': tx_hash})
      
# TODO: Should rename as `Data_Trading`
class Data_Purchase(Namespace):
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

   def on_purchase_confirm(self, data):
      tx_hash = data['tx_hash']
      log.info('Recevied Data Purchase Confirm - Tx hash: %s', tx_hash)

      # Get Transaction Contents
      dmt = DMthread()
      msg, sig = dmt.run(get_tx_ctx, app.iota, tx_hash)
      log.info('Transaction Contents: %s\n'\
               'Signature: %s\n', print_json(msg), print_json(sig))
      
      # Validation of contents hash
      result = _validate(str(msg['Contents']),
                         msg['Contents_Hash'],
                         app.config['HASH'])
      
      assert result
      log.info('Successful Validation of Contents Hash.')

      asymmetric = app.config['ASYMMETRIC']
      digest = _hash(str(msg['Contents']), app.config['HASH'])
      sig_byte = base64.b64decode(to_byte(sig['Signature']))
      verify = im('data_marketplace.crypto.' + asymmetric).verify
      #TODO: Assume public key alread existed from previous step
      key_name = msg['Contents']['Consumer_ID'] + '.pem'
      key_path = os.path.join(app.base_path, app.config['STORAGE_PATH'],
                              "pem", key_name)
      verified = verify(key_path, digest, sig_byte)
      assert verified
      log.info('Verification Result of Signature: %s', verified)

      self.emit('purchase_confirm_response',
                {'message': 'Successful Confirmation',
                 'tx_hash': tx_hash})
      notify = lambda: self._notify(tx_hash)
      t = Thread(target=wait_tx_confirmed,
                 args=(app.iota, tx_hash, app.config['CHECK_TIME'], notify))
      t.start()
   
   def on_download(self, data):
      # TODO: Validate Client Identity
      tx_hash = data['tx_hash']
      log.info('Recevied Data Download - Tx hash: %s', tx_hash)

      # Get Transaction Contents
      dmt = DMthread()
      log.info('Get Purchase Transaction ...')
      msg, sig = dmt.run(get_tx_ctx, app.iota, tx_hash)
      log.info('Transaction Contents: %s\n'\
               'Signature: %s\n', print_json(msg), print_json(sig))

      log.info('Get Target Contents from Target Bundle ...')
      bundle_hash = msg['Contents']['Target_Bundle']
      log.info('Target Hash: %s\n', bundle_hash)
      msg, sig = dmt.run(get_tx_ctx_by_bundle, app.iota, bundle_hash)
      log.info('Transaction Contents: %s\n'\
               'Signature: %s\n', print_json(msg), print_json(sig))

      storage_path = os.path.join(app.base_path, app.config['STORAGE_PATH'])
      key_name = msg['Contents']['Owner'] + '.bin'
      key_path = os.path.join(storage_path, 'key', key_name)
      with open(key_path, 'rb') as f:
         key = f.read()
         log.info('Encrypted AES key: %s', key)
      
      file_name = msg['Contents']['Encrypted_Hash'] + '.bin'
      file_path = os.path.join(storage_path, 'encrypted', file_name)
      with open(file_path, 'rb') as f:
         encrypted = f.read()
      
      self.emit('download_response', {'bundle_hash': bundle_hash,
                                      'file': encrypted,
                                      'key': key})

   def _notify(self, tx_hash):
      self.emit('confirmed', {'message': 'Confirmed Tx',
                              'tx_hash': tx_hash})

def _write_tx_confirm(base_path, response, msg):
   file_name = msg['Contents']['Encrypted_Hash'] + '.bin'
   key_name = msg['Contents']['Owner'] + '.pem'
   encrypted_path = os.path.join(base_path, 'encrypted', file_name)
   key_path = os.path.join(base_path, 'pem', key_name)

   log.info('Encrypted File Store Path: %s\n'\
            'Public Key Path: %s\n', encrypted_path, key_path)

   write_file_byte(encrypted_path, response['data'])
   write_file_byte(key_path, response['public_key'])
   return encrypted_path, key_path

socketio.on_namespace(Data_Registration('/data-registration'))
socketio.on_namespace(Data_Purchase('/data-purchase'))
