from Crypto.Hash import SHA256
from data_marketplace.utils.common import to_byte

def get_digest(data):
   d = to_byte(data)
   digest = SHA256.new(d)
   return digest
