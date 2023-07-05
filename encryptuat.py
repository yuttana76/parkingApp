import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from base64 import b64encode

CERT_PATH = os.environ.get('KTB_UAT_CERT_PATH','/home/ittipon/Downloads/UAT_CGPInApp_parking.mrta-99246/cgpinapp_99246_uat.cer')


def encryptuat(plainText):
    # Load the public key from file in PEM format
    with open(CERT_PATH, 'rb') as f:
        public_key = RSA.importKey(f.read())
    # Use PKCS1_v1_5 to perform RSA encryption with ECB and PKCS1 padding
    cipher = PKCS1_v1_5.new(public_key)
    cipher_text = cipher.encrypt(plainText.encode('utf-8'))
    # Base64 encode the cipher text and return it
    # return b64encode(cipher_text).decode('utf-8').replace('/','%2F').replace('+','%2B').replace('=','%3D')
    return b64encode(cipher_text).decode('utf-8')

if __name__ == '__main__':
    plaintext = '1231231'
    cipher = encryptuat(plaintext)
    cipher2 = encryptuat('1108030672354')
    print(cipher)
    url = f'https://cgp.uat.krungthai.com/P2PRegister/?tran_type=D&site_name=https://parking.mrta.co.th/uat/payment-methods/&term_id=99246&term_seq={cipher}&ref1={cipher2}&cid={cipher2}'
    print(url)