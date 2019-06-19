from importlib import import_module as im
from data_marketplace.utils.log import logging

log = logging.getLogger('data_marketplace.crypto.hash')

def _hash(contents, hash_algo):
   get_digest = _choose(hash_algo)
   log.info(
       "Hashing the file.\n\
        Hash object: %s,\n\
        Hash function: %s", id(contents), hash_algo)

   digest = get_digest(contents)
   return digest

def _validate(origin, target, hash_algo):
   get_digest = _choose(hash_algo)
   calculated = get_digest(origin).hexdigest()
   log.info('Calculated Hash: %s\n'
            'Target Hash: %s', calculated, target)
   if calculated == target:
      return True
   else:
      return False

def _choose(hash_algo):
   return im('data_marketplace.crypto.' + hash_algo).get_digest