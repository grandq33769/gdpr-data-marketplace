from Crypto.Cipher import AES
from Crypto import Random
from data_marketplace.utils.thread import DMthread
from data_marketplace.utils.common import to_byte

def encrypt(key, msg):
   k = to_byte(key)
   m = to_byte(msg)
   iv = Random.new().read(AES.block_size)
   cipher = AES.new(k, AES.MODE_CFB, iv)
   encryted = iv + cipher.encrypt(m)
   return encryted

def decrypt(key, msg):
   k = to_byte(key)
   m = to_byte(msg)
   iv = m[:AES.block_size]
   cipher = AES.new(k, AES.MODE_CFB, iv)
   plain = cipher.decrypt(m[AES.block_size:])
   return plain


if __name__ == "__main__":
   key = b'12345678912345678912345678912345'
   msg = encrypt(key, 'HelloWorld')
   print('Encrypted', msg)
   plain = decrypt(key, msg)
   print('Decrypted', plain.decode('utf-8'))
   with open('./_file/client/raw/512.txt', 'rb') as f:
      content = f.read()
   
   dmthread = DMthread()
   encrypted = dmthread.run(encrypt, key, content)
   with open('encrypted.bin', 'wb') as f:
      f.write(encrypted)

   with open('encrypted.bin', 'rb') as f:
      content = f.read()
   plain = dmthread.run(decrypt, key, content)
   with open('plain.txt', 'wb') as f:
      f.write(plain)

   

