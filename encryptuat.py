import os
# cert = chilkat.CkCert()
# rsa = chilkat.CkRsa()

# success = cert.LoadFromFile("C:/D/certEncrypt/uat/parkandlive.mrta_98427.cer")
# if (success == False):
#     print(1,cert.lastErrorText())
#     sys.exit()

# pubKey = cert.ExportPublicKey()

# if (cert.get_LastMethodSuccess() != True):
#     print(2,cert.lastErrorText())
#     sys.exit()

# publicKey = pubKey.getXml()
# print('pub',publicKey)
# success = rsa.ImportPublicKey(publicKey)
# usePrivateKey = False
CERT_PATH = os.environ['KTB_UAT_CERT_PATH']
def encryptuat(plainText):
    import  chilkat
    cert = chilkat.CkCert()
    rsa = chilkat.CkRsa()
    success = cert.LoadFromFile("C:/D/certEncrypt/uat/parkandlive.mrta_98427.cer")
    pubKey = cert.ExportPublicKey()
    publicKey = pubKey.getXml()
    success = rsa.ImportPublicKey(publicKey)
    usePrivateKey = False
    rsa.put_EncodingMode("base64")
    encrypted = rsa.encryptStringENC(plainText,usePrivateKey)
    return encrypted


