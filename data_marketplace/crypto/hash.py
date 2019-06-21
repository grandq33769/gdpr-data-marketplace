from importlib import import_module as im
from data_marketplace.utils.common import to_byte
from data_marketplace.utils.log import logging

log = logging.getLogger('data_marketplace.crypto.hash')

def _hash(contents, hash_algo):
   log.info(
       "Hashing the file.\n\
        Hash object: %s,\n\
        Hash function: %s", id(contents), hash_algo)

   return _get_digest(contents, hash_algo)

def _validate(origin, target, hash_algo):
   digest = _get_digest(origin, hash_algo)
   calculated = digest.hexdigest()
   log.info('Calculated Hash: %s\n'
            'Target Hash: %s', calculated, target)
   if calculated == target:
      return True
   else:
      return False

def _get_digest(contents, hash_algo):
   module_name = hash_algo.upper() 
   contents_byte = to_byte(contents)
   return im('Crypto.Hash.' + module_name).new(contents_byte)