from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA

if __name__ == "__main__":
    from Crypto import Random
    random_generator = Random.new().read
    rsa = RSA.generate(8192, random_generator)

    private_pem = rsa.exportKey()
    with open('private-8192.pem', 'w') as f:
        f.write(private_pem.decode('utf-8'))

    public_pem = rsa.publickey().exportKey()
    with open('public-8192.pem', 'w') as f:
        f.write(public_pem.decode('utf-8'))