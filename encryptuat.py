import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from base64 import b64encode

CERT_PATH = os.environ.get('KTB_UAT_CERT_PATH','C:/D/certEncrypt/uat/cgpinapp_99246_uat.ce')


def encryptuat(plainText):
    # Load the public key from file in PEM format
    with open(CERT_PATH, 'rb') as f:
        public_key = RSA.importKey(f.read())
    # Use PKCS1_v1_5 to perform RSA encryption with ECB and PKCS1 padding
    cipher = PKCS1_v1_5.new(public_key)
    cipher_text = cipher.encrypt(plainText.encode('utf-8'))
    # Base64 encode the cipher text and return it
    return b64encode(cipher_text).decode('utf-8').replace('/','%2F').replace('+','%2B').replace('=','%3D')


if __name__ == '__main__':
    plaintext = '1231231'
    cipher = encryptuat(plaintext)
    cipher2 = encryptuat('1111111111111')
    print(cipher)
    url = f'https://cgp.uat.krungthai.com/P2PRegister/?tran_type=R&site_name=https://parking.mrta.co.th/uat/payment-methods/&term_id=99246&term_seq={cipher}&ref1={cipher2}&cid=bN8wUPNtBe4hJPAXJq5Vc3JxNLf%2BMgXAOASkYiRo8YWzT7eOGw7AAKgwPBX3MOy%2BWtbyh1O8cXF1%0D%0AoNBcI88swYVj%2BgK%2B%2BsygAdY%2F6qjr38J%2BKVhxmCThC3oqKhbFKqcV%2BdnZsuECIqmzaRRRbUiz5DVx%0D%0AraJN0wD%2FP0IPYaiG5U0Qec3gZwnmxTyxd4RSstVY4MocyzRf%2F7gZZFEdcWakIbad%2FgCc6T%2BIyhms%0D%0AvzhVhNLgpWTiN907CKD7BzGwhr8haz2qO%2Bn7lJfn3yya8Zi9bocYnpKceN6GSQdO7xjXpIr54E9b%0D%0AFmEdhFgradC547M7hGYM5OoSsQrtTm92WEAkUA%3D%3D'
    print(url)