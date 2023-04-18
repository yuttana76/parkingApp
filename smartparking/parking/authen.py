import functools
import hashlib
from app import app
from flask import jsonify, request 

def authenApikey(func):
    @functools.wraps(func)
    def authenticated(*args,**kwargs):
        if request.json:
            api_key = request.headers.get('APIKEY')
        else:
            return jsonify({'message':'Please provide your api key.'}),400
        
        if request.method == 'POST' and api_key == app.secret_key:
            return func(*args,**kwargs)
        else:
            return jsonify({'message':'Invalid api key.'}),400
        
    return authenticated

def authenticateSV(func):
    @functools.wraps(func)
    def verifyheaders(*args,**kwargs):
        if request.json:
            sender_key = request.headers.get('APIKEY')
            sender_token = request.headers.get('VERIFY-TOKEN')
            if apikey_and_token_is_correct(senderkey = sender_key,sendertoken=sender_token,body=request.get_json()):
                return func(*args,**kwargs)
            return jsonify({'message':'Invalid api headers.'}),400  
        else:
            return jsonify({'message':'Please provide your api key.'}),400
    return verifyheaders
        
def ciphertext(body,apikey):
    SALT = '9FVxAyOuCrw'
    body = str(body)
    plaintext = apikey + body + SALT
    hash_obj = hashlib.sha256(bytes(plaintext))
    ciphertext = hash_obj.hexdigest()
    return ciphertext

def apikey_and_token_is_correct(senderkey,sendertoken,body):
    APIKEY = 'hIplFxuEU6ENXKN7DUnNKTHtxHovP2F7CVyKrAh_0Xm6pSFPNn0S3EKn1AFoh-66xuo'
    if senderkey == APIKEY and sendertoken == ciphertext(body=body,apikey=APIKEY):
        return True 
    return False
    