import requests as req
import json
def void_fastpay(payRef):
    data = {'merchantId': '900000303',
            'loginId':'ktbapi',
            'password':'test1234',
            'actionType':'Void',
            'payRef':payRef}

    resp = req.post("https://ktbfastpay.ktb.co.th/KTB/eng/merchant/api/orderApi.jsp", data)
    a = ((resp.text).replace('=', ':')).split('&')
    str =json.dumps(a)
    loaded_data = json.loads(str)
    code = 0
    for key in loaded_data:
        key = key.split(':')
        parameter = key[0]
        value = key[1]
        if parameter == 'resultCode':
            if value == '0': #success
                code = 1
            else:
                return {'status':'fail'}
        elif parameter == 'ref' and code == 1:
            orderNumber = value
        elif parameter == 'amt' and code == 1:
            total = value
            return {'status':'success','ref2':orderNumber,'amount':total}