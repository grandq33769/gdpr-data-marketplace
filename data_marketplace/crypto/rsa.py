import os
from Crypto.Cipher import PKCS1_v1_5 as Cipher
from Crypto.Signature import PKCS1_v1_5 as Signature
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto import Random
from data_marketplace.utils.common import to_byte
from data_marketplace.utils.log import logging

log = logging.getLogger('data_marketplace.crypto.rsa')

def encrypt(key_path, msg):
   m = to_byte(msg)
   with open(key_path) as f:
      contents = f.read()
   rsa_key = RSA.importKey(contents)
   cipher = Cipher.new(rsa_key)
   encrypted = cipher.encrypt(m)
   return encrypted

def decrypt(key_path, encrypted):
   e = to_byte(encrypted)
   # TODO: Consider how to create sentinel
   sentinel = Random.new().read(32)

   with open(key_path) as f:
      contents = f.read()
   rsa_key = RSA.importKey(contents)

   cipher = Cipher.new(rsa_key)
   plain = cipher.decrypt(e, sentinel)
   return plain

def sign(priv_key_path, digest_instance):
   key = _import_key(priv_key_path)
   signer = Signature.new(key)
   sig = signer.sign(digest_instance)
   return sig

def verify(pub_key_path, msg, sig):
   key = _import_key(pub_key_path)
   verifier = Signature.new(key)
   verified = verifier.verify(msg, sig)
   return verified

def _import_key(path):
   with open(path, 'r') as f:
      key = RSA.importKey(f.read())
   return key

def genearte_key_pair(length, path):
   from Crypto import Random
   random_generator = Random.new().read
   rsa = RSA.generate(length, random_generator)

   log.info('Generating private key. Key length: %d', length)
   private_pem = rsa.exportKey()
   name = 'private-{:d}.pem'.format(length)
   join_path = os.path.join(path, name)
   with open(join_path, 'w') as f:
      f.write(private_pem.decode('utf-8'))

   log.info('Generating private key. Key length: %d', length)
   public_pem = rsa.publickey().exportKey()
   name = 'public-{:d}.pem'.format(length)
   join_path = os.path.join(path, name)
   with open(join_path, 'w') as f:
      f.write(public_pem.decode('utf-8'))

if __name__ == "__main__":

   # Test signature verification
   ############################################################
   # pu_path = '../../instance/client/producer/public-4096.pem'
   # pr_path = '../../instance/client/producer/private-4096.pem'
   # msg = 'HelloWorld!'.encode('utf-8')
   # from Crypto.Hash import SHA256
   # digest = SHA256.new(msg)
   # print(digest)

   # sig = sign(pr_path, digest)
   # import base64
   # print(sig)
   # print(base64.b64encode(sig))
   # print(base64.b64decode(base64.b64encode(sig)))
   # verified = verify(pu_path, digest, sig)

   # print(verified)

   # Generate key pair
   ############################################################
   # path = './instance/client/consumer/'
   # genearte_key_pair(4096, path)
   ############################################################

   # Encrypt aes-key by rsa pub-key
   ############################################################
   aes = 'bl1tkcgf7mwfi178elkr2mjxhzhzrkru'
   pub_key_path = './instance/client/consumer/public-4096.pem'
   priv_key_path = './instance/client/consumer/private-4096.pem'

   encrypt_msg = encrypt(pub_key_path, aes)
   print(encrypt_msg)
   with open('./_file/server/key/test.bin', 'wb') as f:
      f.write(encrypt_msg)

   with open('./_file/server/key/test.bin', 'rb') as f:
      contents_byte = f.read()
   plain = decrypt(priv_key_path, contents_byte)