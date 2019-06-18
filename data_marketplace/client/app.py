import os
import sys
import base64
import json
from importlib import import_module as im
from iota import Iota, TryteString, Address, Tag, ProposedTransaction
from data_marketplace.utils.common import import_template, print_json
from data_marketplace.utils.log import logging
from data_marketplace.utils.thread import DMthread

log = logging.getLogger('data_marketplace.client.api')

class DataMarketplaceClient():

   def __init__(self, config, sio):
      self.cfg = config
      self.sio = sio
      self.send = dict()

   def run(self):
      try:
         self.iota = self.connect_iota()
      except ConnectionError:
         log.error('No Available IOTA node.'\
                   'Please check the configuration again.'\
                   'Terminate Process.')
         self.shutdown()
      try:
         self.sio.connect(self.cfg['Data_Marketplace']['host'])
         log.info("Success to connect Data Marketplace Server at %s", 
                  self.cfg['Data_Marketplace']['host'])
      except:
         log.error('Failed to connect Data Marketplace Server'\
                   'Please check the configuration again.'\
                   'Terminate Process.', exc_info=True)
         self.shutdown()

   def registry(self, data_path, response_json, price, expired_date):
      # Update variable
      self.send = dict()
      self.send.update({'Owner':self._hash(self.cfg['Data_Marketplace']['client_id']).hexdigest(),
                        'Price':price,
                        'Expired_Date':expired_date})

      self.import_contents('s2_schema_response', response_json)
      # TODO: Validation
      if not self.validate(data_path, None):
         log.error('Validation failed in Data registration.')
         return
      namespace = self.sio.namespace_handlers['/data-registration']

      # Encryption of file
      try:
         encrypted, encrypted_path, data_hash = self.encrypt(data_path)
         log.info('Encrypted Data store in : %s', encrypted_path)
         self.send.update({'Data_Hash':data_hash.hexdigest()})
      except FileNotFoundError:
         log.error('Encryption Failure.' \
                   'File Not Found.' \
                   'Data Registration Terminated.', exc_info=True)
         return
  
      # Calculate the contents hash
      try:
         contents_hash = self._hash(str(self.get_contents('s3_certificate')))
         self.send.update({'Contents_Hash':contents_hash.hexdigest()})
      except KeyError:
         log.error('Missing Data in Contents.' \
                   'Please confirm the completness of Contents.' \
                   'Data Registration Terminated.', exc_info=True)
         return

      # Calculate the Signature of Hash
      try:
         signature = self.sign(contents_hash)
         sign_str = base64.b64encode(signature).decode('utf-8')
         self.send.update({'Signature': sign_str})
      except:
         log.error('Signing Error.', exc_info=True)
         return

      # Send Transaction to IOTA network
      try:
         tx_hash = self.send_tx('s3_certificate', self.send['Send_Address'])
      except:
         log.error('Send Transaction Error.', exc_info=True)
         return

      namespace.emit('tx_confirm', {'txhash': tx_hash, 'data': encrypted})

   def validate(self, file_path, schema_json):
      return True

   def encrypt(self, file_path):
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
      # Encryption
      encrypted = dmt.run(encrypt_func, key, contents)
      digest = dmt.run(self._hash, contents)
      encrypted_path = self._write_encrypted(encrypted, digest)
      return encrypted, encrypted_path, digest

   def _hash(self, file):
      hash_algo = self.cfg['Data_Marketplace']['hash']
      get_digest = im('data_marketplace.crypto.'+hash_algo).get_digest
      log.info("Hashing the file.\n\
                File object: %s,\n\
                Hash function: %s"
               , id(file), hash_algo)

      digest = get_digest(file)
      return digest

   def _write_encrypted(self, encrypted, digest):
      path = self.cfg['Data_Marketplace']['encrypt_path']
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

   def connect_iota(self):
      nodes = eval(self.cfg['IOTA']['node'])
      seed = self.cfg['IOTA']['seed']
      log.info('Connecting IOTA network. IOTA full node list: %s', nodes)
      connected = False
      times = 1
      node = nodes.pop()
      while not connected:
         try:
            log.info('Trying to connecting IOTA node. Node address: "%s" Times: %d',
                     node, times)
            iota = Iota(node, seed)
            info = iota.get_node_info()
            connected = True
            log.info('Success Connected to IOTA node. Node address: "%s"\n'\
                     'Node Information:\n %s', node, print_json(info))
         except:
            if times < 3:
               times += 1
            else:
               try:
                  node = nodes.pop()
               except IndexError:
                  raise ConnectionError
            log.error('IOTA Connection Error. Retry Again.', exc_info=True)
      return iota

   def send_tx(self, template_name, address):
      log.info('Start sending transaction to IOTA networtk.')

      self.send.update({'Contents': self.get_contents(template_name)})
      addr = Address(address)
      tag = Tag(self.cfg['Data_Marketplace']['tag'])

      # Convert Contents to Trytes
      msg = self.get_contents(template_name, contents_only=False)
      msg = TryteString.from_unicode(json.dumps(msg))

      # Convert Signature to Trytes
      sig = self.get_contents('Signature', contents_only=False)
      sig = TryteString.from_unicode(json.dumps(sig))

      # Transaction Formation
      tx = ProposedTransaction(address=addr, message=msg, tag=tag, value=0)
      tx_sig = ProposedTransaction(address=addr, message=sig, tag=tag, value=0)
      log.info('Address: %s\nTag: %s\nTransaction Message: %s',
               addr, tag, msg)

      # Send Transfer
      dmt = DMthread()
      result = dmt.run(self.iota.send_transfer, [tx, tx_sig])
      return str(result['bundle'].hash)

   def shutdown(self):
      self.sio.disconnect()
      sys.exit()
