import sys
import os
import base64
import json
import time
from importlib import import_module as im
from iota import TryteString, Address, Tag, ProposedTransaction
from data_marketplace.crypto.hash import _hash
from data_marketplace.utils.common import import_template, read_file_byte
from data_marketplace.utils.log import logging
from data_marketplace.utils.dlt import connect_iota
from data_marketplace.utils.thread import DMthread

log = logging.getLogger('data_marketplace.client.api')

class DataMarketplaceClient():

   def __init__(self, config, sio):
      self.cfg = config
      self.sio = sio
      self.send = dict()
      self.dr_confirm = set()
      self.dp_confirm = set()

   def run(self):
      self.hash_algo = self.cfg['Data_Marketplace']['hash']
      self.pub_key = read_file_byte(self.cfg['Asymmetric']['public_key'])
      try:
         self.iota = connect_iota(eval(self.cfg['IOTA']['node']),
                                  self.cfg['IOTA']['seed'])
      except ConnectionError:
         log.error('No Available IOTA node.'\
                   'Please check the configuration again.'\
                   'Terminate Process.')
         self.shutdown()
      try:
         self.sio.connect(self.cfg['Data_Marketplace']['host'])
         log.info("Success to connect Data Marketplace Server at %s.", 
                  self.cfg['Data_Marketplace']['host'])
      except:
         log.error('Failed to connect Data Marketplace Server. '\
                   'Please check the configuration again.'\
                   'Terminate Process.', exc_info=True)
         self.shutdown()

   def registry(self, data_path, response_json, price, expired_date):
      # Update variable
      self.send = dict()
      self.send.update({'Owner':_hash(self.cfg['Data_Marketplace']['client_id'],\
                                      self.hash_algo).hexdigest(),
                        'Price':price,
                        'Expired_Date':expired_date})

      self.import_contents('s2_schema_response', response_json)
      # TODO: Validation
      if not self.validate(data_path, None):
         log.error('Validation failed in Data registration.')
         return False
      namespace = self.sio.namespace_handlers['/data-registration']

      # Encryption of file
      try:
         encrypted, encrypted_hash, encrypted_path, data_hash = \
                                                  self.sym_encrypt(data_path)
         log.info('Encrypted Data store in : %s', encrypted_path)
         self.send.update({'Data_Hash':data_hash.hexdigest()})
         self.send.update({'Encrypted_Hash':encrypted_hash.hexdigest()})
      except FileNotFoundError:
         log.error('Encryption Failure.' \
                   'File Not Found.' \
                   'Data Registration Terminated.', exc_info=True)
         return False
  
      # Calculate the contents hash
      try:
         contents_hash = _hash(str(self.get_contents('s3_certificate')), self.hash_algo)
         self.send.update({'Contents_Hash':contents_hash.hexdigest()})
      except KeyError:
         log.error('Missing Data in Contents.' \
                   'Please confirm the completness of Contents.' \
                   'Data Registration Terminated.', exc_info=True)
         return False

      # Calculate the Signature of Hash
      try:
         signature = self.sign(contents_hash)
         sign_str = base64.b64encode(signature).decode('utf-8')
         self.send.update({'Signature': sign_str})
      except:
         log.error('Signing Error.', exc_info=True)
         return False

      # Send Transaction to IOTA network
      try:
         tx_hash = self.send_tx('s3_certificate', self.send['Send_Address'])
      except:
         log.error('Send Transaction Error.', exc_info=True)
         return False

      # Send Confirmation Request to Server
      dmt = DMthread()
      self.send.update({'tx_hash': tx_hash, 'public_key': self.pub_key, 'data': encrypted})
      send_dict = self.get_contents('s4_tx_confirm', contents_only=False)
      self.dr_confirm.clear() 
      dmt.run(namespace.emit, 'tx_confirm', send_dict)

      result = dmt.run(self.wait_tx_confirm, tx_hash, self.dr_confirm)

      return result

   def purchase(self, address, bundle, value):
      # Update variable
      self.send = dict()
      self.send.update({'Consumer_ID':_hash(self.cfg['Data_Marketplace']['client_id'],\
                                      self.hash_algo).hexdigest(),
                        'Target_Bundle': bundle,
                        'Value': value})
      namespace = self.sio.namespace_handlers['/data-purchase']
      
      # Calculate the contents hash
      try:
         contents_hash = _hash(str(self.get_contents('b1_send_fund')), self.hash_algo)
         self.send.update({'Contents_Hash':contents_hash.hexdigest()})
      except KeyError:
         log.error('Missing Data in Contents.' \
                   'Please confirm the completness of Contents.' \
                   'Data Purchase Terminated.', exc_info=True)
         return False

      # Calculate the Signature of Hash
      try:
         signature = self.sign(contents_hash)
         sign_str = base64.b64encode(signature).decode('utf-8')
         self.send.update({'Signature': sign_str})
      except:
         log.error('Signing Error.', exc_info=True)
         return False

      # Send Fund to Address
      try:
         tx_hash = self.send_tx('b1_send_fund', address)
      except:
         log.error('Send Transaction Error.', exc_info=True)
         return False

      # Send Confirmation Request to Server
      dmt = DMthread()
      self.send.update({'tx_hash': tx_hash, 'public_key': self.pub_key})
      send_dict = self.get_contents('b2_purchase_confirm', contents_only=False)
      dmt.run(namespace.emit, 'purchase_confirm', send_dict)

      self.dp_confirm.clear()
      result = dmt.run(self.wait_tx_confirm, tx_hash, self.dp_confirm)

      return result

   def download(self, tx_hash):
      # TODO: Validate client to download the file
      namespace = self.sio.namespace_handlers['/data-purchase']

      dmt = DMthread()
      self.send.update({'tx_hash': tx_hash, 'public_key': self.pub_key})
      send_dict = self.get_contents('b3_download', contents_only=False)
      dmt.run(namespace.emit, 'download', send_dict)

      return False

   def validate(self, file_path, schema_json):
      return True

   def sym_encrypt(self, file_path):
      key = self.cfg['Symmetric']['key']
      encrypt_algo = self.cfg['Data_Marketplace']['symmetric']
      encrypt_func = im('data_marketplace.crypto.'+encrypt_algo).encrypt
      log.info("Encryption of file.\n\
                Input file path: %s,\n\
                Encrypted algorithm: %s,\n\
                Key length: %d"
               , file_path, encrypt_algo, len(key))

      dmt = DMthread()
      # Read File
      with open(file_path, 'rb') as f:
         contents = f.read()
      digest = dmt.run(_hash, contents, self.hash_algo)

      # Encryption
      encrypted = dmt.run(encrypt_func, key, contents)
      encrypted_hash = dmt.run(_hash, encrypted, self.hash_algo)
      encrypted_path = self._write_encrypted(encrypted, encrypted_hash)
      return encrypted, encrypted_hash, encrypted_path, digest

   def sym_decrypt(self, key, contents):
      dmt = DMthread()
      decrypt_algo = self.cfg['Data_Marketplace']['symmetric']
      decrypt_func = im('data_marketplace.crypto.'+decrypt_algo).decrypt
      log.info("Decryption of file.\n\
                Decrypt file size: %d,\n\
                Decrypt algorithm: %s,\n\
                Key length: %d"
               , len(contents), decrypt_algo, len(key))

      plain = dmt.run(decrypt_func, key, contents)
      return plain

   def asy_decrypt(self, encrypted):
      dmt = DMthread()
      priv_key_path = self.cfg['Asymmetric']['private_key']
      decrypt_algo = self.cfg['Data_Marketplace']['asymmetric']
      decrypt_func = im('data_marketplace.crypto.'+decrypt_algo).decrypt
      log.info("Decryption of file.\n\
                Decrypt file size: %d,\n\
                Decrypted algorithm: %s,\n\
                Private key path: %s"
               , len(encrypted), decrypt_algo, priv_key_path)

      decrypted = dmt.run(decrypt_func, priv_key_path, encrypted)
      return decrypted

   def _write_encrypted(self, encrypted, digest):
      path = os.path.join(self.cfg['Data_Marketplace']['storage_path'], 'encrypted')
      hexdigest = digest.hexdigest()
      log.info("Writing the encrypted object.\n\
                Encrypted object: %s,\n\
                Writing path: %s\n\
                Hash digest: %s"
               , id(encrypted), path, hexdigest)

      # Write File
      filename = hexdigest + '.bin'
      path = os.path.join(path, filename)
      with open(path, 'wb') as f:
         f.write(encrypted)
  
      return path

   def get_contents(self, name, contents_only=True):
      template_path = self.cfg['Data_Marketplace']['template_path']
      contents_dict = import_template(template_path, name, contents_only)

      for k in contents_dict.keys():
         if k in self.send:
            contents_dict[k] = self.send[k]

      return contents_dict

   def import_contents(self, name, jfile):
      template_path = self.cfg['Data_Marketplace']['template_path']
      contents_dict = import_template(template_path, name, contents=True)

      for k in contents_dict.keys():
         self.send.update({k: jfile['Contents'][k]})

   def form_trans_msg(self, name):
      template_path = self.cfg['Data_Marketplace']['template_path'] 
      trans_dict = import_template(template_path, name, contents=False)

      self.send.update({'Contents':self.get_contents(name)})
      for k in trans_dict.keys():
         trans_dict[k] = self.send[k]
      
      return trans_dict

   def sign(self, digest):
      priv_key_path = self.cfg['Asymmetric']['private_key']
      sign_algo = self.cfg['Data_Marketplace']['asymmetric']
      sign_func = im('data_marketplace.crypto.'+sign_algo).sign
      log.info("Signing the hash digest.\n\
                Digest object: %s,\n\
                Signing algorithm: %s\n\
                Hash digest: %s"
               , id(digest), sign_algo, digest.hexdigest())

      # Signing
      signature = sign_func(priv_key_path, digest)
      return signature

   def send_tx(self, template_name, address):
      log.info('Start sending transaction to IOTA networtk.')

      self.send.update({'Contents': self.get_contents(template_name)})
      addr = Address(address)
      tag = Tag(self.cfg['Data_Marketplace']['tag'])

      # Convert Contents to Trytes
      msg = self.get_contents(template_name, contents_only=False)
      msg = TryteString.from_unicode(json.dumps(msg))

      # Convert Signature to Trytes
      sig = self.get_contents('signature', contents_only=False)
      sig = TryteString.from_unicode(json.dumps(sig))

      # Transaction Formation
      tx = ProposedTransaction(address=addr, message=msg, tag=tag, value=0)
      tx_sig = ProposedTransaction(address=addr, message=sig, tag=tag, value=0)
      log.info('Address: %s\nTag: %s\nTransaction Message: %s',
               addr, tag, msg)

      # Send Transfer
      dmt = DMthread()
      result = dmt.run(self.iota.send_transfer, [tx, tx_sig])
      return str(result['bundle'].transactions[0].hash)
   
   def wait_tx_confirm(self, tx_hash, result):
      timeout = self.cfg['Data_Marketplace'].getint('wait_timeout')
      now = 0
      step = 0.1
      while tx_hash not in result and now < timeout:
         time.sleep(step)
         now += step

      if now > timeout:
         return False
      else:
         return True

   def read_config(self, cfg_path):
      self.cfg.read(cfg_path)

   def shutdown(self):
      self.sio.disconnect()
