import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from base64 import b64encode

CERT_PATH = os.environ.get('KTB_UAT_CERT_PATH','C:/D/certEncrypt/uat/parkandlive.mrta_98427.cer')


def encryptuat(plainText):
    # Load the public key from file in PEM format
    with open(CERT_PATH, 'rb') as f:
        public_key = RSA.importKey(f.read())
    # Use PKCS1_v1_5 to perform RSA encryption with ECB and PKCS1 padding
    cipher = PKCS1_v1_5.new(public_key)
    cipher_text = cipher.encrypt(plainText.encode('utf-8'))
    # Base64 encode the cipher text and return it
    return b64encode(cipher_text).decode('utf-8')


