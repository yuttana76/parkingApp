import sys
import  chilkat
from base64 import b64encode
cert = chilkat.CkCert()
rsa = chilkat.CkRsa()

success = cert.LoadFromFile("C:/D/certEncrypt/uat/parkandlive.mrta_98427.cer")
if (success == False):
    print(1,cert.lastErrorText())
    sys.exit()

pubKey = cert.ExportPublicKey()

if (cert.get_LastMethodSuccess() != True):
    print(2,cert.lastErrorText())
    sys.exit()

publicKey = pubKey.getXml()
print('pub',publicKey)
success = rsa.ImportPublicKey(publicKey)
usePrivateKey = False

def encryptuat(plainText):
    
    print(plainText,'plaintext')
    rsa.put_EncodingMode("base64")
    encrypted = rsa.encryptStringENC(plainText,usePrivateKey)
    print('encr',encrypted)
    return encrypted


