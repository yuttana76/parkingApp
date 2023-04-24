import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509 import load_pem_x509_certificate

CERT_PATH = os.environ['KTB_CERT_PATH']

def encrypt(plainText):
    with open(CERT_PATH, 'rb') as f:
        cert_data = f.read()

    cert = load_pem_x509_certificate(cert_data)
    public_key = cert.public_key()

    ciphertext = public_key.encrypt(
        plainText.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=cert.signature_hash_algorithm),
            algorithm=cert.signature_hash_algorithm,
            label=None
        )
    )

    return ciphertext.hex()
