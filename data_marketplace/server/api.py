import os
import json
import base64
from flask import render_template
from flask_socketio import Namespace, emit
from importlib import import_module as im
from data_marketplace.server import app, socketio
from data_marketplace.crypto.hash import _hash, _validate
from data_marketplace.utils.common import print_json, read_file_byte, write_file_byte, to_byte
from data_marketplace.utils.thread import DMthread
from data_marketplace.utils.iota import get_tx_ctx
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
      print(write_path)
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
