from Crypto.Hash import SHA256

def hash_func(data):
   digest = SHA256.new()
   digest.update(data)
   return digest.hexdigest()
