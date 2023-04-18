from datetime import datetime, date, timedelta
from flask import jsonify,  Response
import json
import requests
from app import  (
    Parking_member as p_mem,
    Parking_log as pl,
    db
)
from time import sleep

def request_to_api(url, data,headers=None):
    if headers:
        response =  requests.post(url=url, headers=headers, data=data)
    else:
        response =  requests.post(url=url, data=data)
    res = response.json()
    return res

class ApiMember:
    def __init__(self, data):
        self.availableApiMember = ['N1013', 'N1014']
        print(data)
        self.data = data
    
    def from_orm(self, transaction):
        print('transaction: ', transaction)
        self.transaction = transaction
        self.vcard_type = self.transaction.vcard_type
        self.parking_code = self.transaction.parking_code
    
    def prepare_data(self, methods):
        vcard_type = self.vcard_type
        data={}
        if vcard_type == 'CIT':
            license_plate2 = self.data.get('license_plate2') if self.data.get('license_plate2') else self.data.get('license_plate1')
            card_expire_date = self.data.get('card_expire_date')
            card_expire_date = datetime.strptime(card_expire_date, '%Y-%m-%d') if isinstance(card_expire_date, str) else card_expire_date
            f_card_expire_date = datetime(card_expire_date.year, card_expire_date.month, card_expire_date.day)\
                .strftime('%Y-%m-%d %H:%M:%S')
            service_start_date =  self.data.get('service_start_date')
            service_start_date = datetime.strptime(service_start_date, '%Y-%m-%d') if isinstance(service_start_date, str) else service_start_date
            f_service_start_date = datetime(service_start_date.year, service_start_date.month, service_start_date.day)\
                .strftime('%Y-%m-%d %H:%M:%S')
            if methods == 'insert':
                data['stationCode'] = self.data.get('parking_code')
                data['memberFirstName'] = self.data.get('first_name')
                data['memberLastName'] = self.data.get('last_name')
                data['memberCardName'] = self.data.get('card_id')
                data['memberLicensePlate1'] = self.data.get('license_plate1')
                data['memberLicensePlate2'] = license_plate2
                data['memberCardExpire'] = f_card_expire_date
                data['memberCardStart'] = f_service_start_date
            elif methods == 'update':
                data['stationCode'] = self.data.get('parking_code')
                data['token_id'] = self.transaction.token_id
                data['memberFirstName'] = self.data.get('first_name')
                data['memberLastName'] = self.data.get('last_name')
                data['memberCardName'] = self.data.get('card_id')
                data['memberLicensePlate1'] = self.data.get('license_plate1')
                data['memberLicensePlate2'] = license_plate2
                data['memberCardExpire'] = f_card_expire_date
                data['memberCardStart'] = f_service_start_date
            data['username'] = 'jpark'
            data['password'] = 'jPark54321'
            data['stationCode'] = 'GN23' if data['stationCode'] == 'N1013' else 'GN24'
            data['remark'] = ''
        return data

    def url_methods(self, methods):
        vcard_type = self.vcard_type
        if vcard_type == 'CIT':
            if methods == 'insert':
                url = 'https://uatparkandride.mrta.co.th/jpark/v1/member/insert'
            elif methods == 'update':
                url = 'https://uatparkandride.mrta.co.th/jpark/v1/member/update'
            elif methods == 'cardlost':
                url = 'https://uatparkandride.mrta.co.th/jpark/v1/member/cardlost'
            elif methods == 'cardreturn':
                url = 'https://uatparkandride.mrta.co.th/jpark/v1/member/cardreturn'
        return url
    
    def try_to_request(self, method, headers=None):
        url = self.url_methods(method)
        data = self.prepare_data
        if self.vcard_type == 'CIT':
            sleep(30)
            print('30 s.')
            try:
                res = request_to_api(url=url, data=data, headers=headers)
                if res.get('error') != True:
                    token_id = res['data']['token_id']
                    if method=='insert':
                        self.transaction.token_id = token_id
                    self.transaction.api_member_status = '1'
                    db.session.commit()
                    print('success')
            except requests.exceptions.RequestException as e:
                self.transaction.api_member_status = '0'
                db.session.commit()
                print('failed again...')

    def request_insert(self):
        vcard_type = self.vcard_type
        parking_code = self.parking_code
        method = 'insert'
        if parking_code in self.availableApiMember:
            try:
                url = self.url_methods(method)
                data = self.prepare_data(method)
                self.prepare_data = data
                res = request_to_api(url=url, data=data)
                print(res.get('message'))
                if vcard_type == 'CIT':
                    if res.get('error') != True:
                        token_id = res['data']['token_id']
                        self.transaction.token_id = token_id
                        self.transaction.api_member_status = '1'
                        db.session.commit()
                        return ({'status':True, 'message': res.get('message')}), 200
                    else:
                        return {'status':False, 'message': res.get('message')}, 201
            except requests.exceptions.RequestException as e:
                if vcard_type == 'CIT':
                    self.transaction.api_member_status = '0'
                    db.session.commit()
                return {'status':False, 'message': f'ไม่สามารถส่งข้อมูลไปยัน {vcard_type} ได้ โปรดลองใหม่อีกครั้ง'}, 404

        return {'status':True}, 200

    def request_update(self):
        vcard_type = self.vcard_type
        parking_code = self.parking_code
        method = 'update'
        if parking_code in self.availableApiMember:
            try:
                url = self.url_methods(method)
                data = self.prepare_data(method)
                print(data)
                self.prepare_data = data
                res = request_to_api(url=url, data=data)
                print(res.get('message'))
                if vcard_type == 'CIT':
                    if res.get('error') != True:
                        self.transaction.api_member_status = '1'
                        db.session.commit()
                        return ({'status':True, 'message': res.get('message')}), 200
                    else:
                        print('*****cant update****')
                        return {'status':False, 'message': res.get('message')}, 201
            except requests.exceptions.RequestException as e:
                if vcard_type == 'CIT':
                    self.transaction.api_member_status = '0'
                    db.session.commit()
                return {'status':False, 'message': f'ไม่สามารถส่งข้อมูลไปยัน {vcard_type} ได้ โปรดลองใหม่อีกครั้ง'}, 404

        return {'status':True}, 200


