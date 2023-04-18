import datetime
from flask import request, Response
import json
from app import Parking_log, db
from getReserveParking import capacity_countout

def response_api(code, message_dict=False):
    message_dict_ = {
            '100':{'message':'success', 'description':'เข้าสำเร็จ', 'gate_status':'1', 'result_code':'success','opengatein_date':datetime.datetime.now()},
            '101':{'message':'success', 'description':'ออกสำเร็จ', 'gate_status':'1', 'result_code':'success','opengateout_date':datetime.datetime.now()},
            '102':{'message':'fail', 'description':'ออกไม่สำเร็จ', 'gate_status':'', 'result_code':'fail'},
            '103':{'message':'fail', 'description':'เข้าไม่สำเร็จ', 'gate_status':'', 'result_code':'fail'},
            '104':{'message':'fail', 'description':'ได้ทำการ Scan QRcode แล้ว', 'gate_status':'', 'result_code':'success'},
            '105':{'message':'fail', 'description':'QRcode หมดอายุ', 'gate_status':'', 'result_code':'fail'},
            '106':{'message':'fail', 'description':'ไม่ได้ทำรายการขาเข้า', 'gate_status':'', 'result_code':'fail'},
            '107':{'message':'fail', 'description':'qrcode ผิดพลาด หรือ ได้ทำรายการไปแล้ว', 'gate_status':'', 'result_code':'fail'},
            '109':{'message':'fail', 'description':'การทำรายการผิดพลาด error', 'gate_status':'', 'result_code':'fail'},
            '110':{'message':'fail', 'description':'qrcode ผิดพลาด เนื่องจาก scan ผิดอาคาร', 'gate_status':'', 'result_code':'fail'}
        }
    if message_dict == False:
        body = {
            'status':{
                'code':code,
                'message':message_dict_[code]['message'],
                'description':message_dict_[code]['description']
            }
        }
        headers = {
            'Content-Type': "application/json"
        }
        payload = json.dumps(body)
        res = Response(headers=headers,response=payload)
        return res
    else:
        return message_dict_


def api_bookin_log():
    
    username = request.get_json()['username']
    password = request.get_json()['password']
    qr_code_cit = request.get_json()['qrCode']
    parking_code_cit = request.get_json()['stationCode']
    kioskin_code = request.get_json()['kioskCode']
    floorin_code = request.get_json()['floorCode']
    kiosk_timestamp = datetime.datetime.strptime(request.get_json()['kioskSendTimestamp'], '%Y-%m-%d %H:%M:%S')
   
    if request.method == 'POST' and username == 'jparkapi' and password == '123456' :
        
        qrcode_row = Parking_log.query.filter(Parking_log.qr_code_reserve == qr_code_cit).order_by(
                Parking_log.qr_code_exprie.desc()).first()
        try:
            qr_code_reserve = qrcode_row.qr_code_reserve
        except:
            qr_code_reserve = None
        if qr_code_reserve:
            
            parking_code = qrcode_row.parking_code
            if parking_code_cit == parking_code:
                
                qr_code_gateout_status = qrcode_row.qr_code_gateout_status
                if qr_code_gateout_status != '1':
                    
                    qr_code_gatein_status = qrcode_row.qr_code_gatein_status
                    if qr_code_gatein_status != '1' :
                        
                        qr_code_exprie = qrcode_row.qr_code_exprie
                        if kiosk_timestamp <= qr_code_exprie:
                            code = '100'
                        else:
                            code = '105'
                    else:
                        code = '104'
                else:
                    code = '107'
            else:
                code = '110'
        else:
            code = '103'
    
    if code != '103':
        Id = qrcode_row.Id
        message_dict = response_api(code, message_dict=True)
        update_log = Parking_log.query.filter_by(Id=Id).first()
        update_log.kioskin_code = kioskin_code
        update_log.floorin_code = floorin_code
        update_log.resultin_code = code
        if code == '100':
            update_log.opengatein_date = message_dict[code]['opengatein_date']
            update_log.qr_code_gatein_status = message_dict[code]['gate_status']
        db.session.commit()
        return response_api(code)
    else:
        return response_api(code)

def api_bookout_log():
    
    username = request.get_json()['username']
    password = request.get_json()['password']
    qr_code_cit = request.get_json()['qrCode']
    parking_code_cit = request.get_json()['stationCode']
    kioskout_code = request.get_json()['kioskCode']
    floorout_code = request.get_json()['floorCode']     
    
    if request.method == 'POST' and username == 'jparkapi' and password == '123456' :
        
        qrcode_row = Parking_log.query.filter(Parking_log.qr_code_reserve == qr_code_cit).order_by(
                Parking_log.qr_code_exprie.desc()).first()
        try:
            qr_code_reserve = qrcode_row.qr_code_reserve
        except:
            qr_code_reserve = None
        if qr_code_reserve:

            parking_code = qrcode_row.parking_code
            if parking_code_cit == parking_code:
                
                qr_code_gateout_status = qrcode_row.qr_code_gateout_status
                if qr_code_gateout_status != '1':
                   
                    qr_code_gatein_status = qrcode_row.qr_code_gatein_status
                    if qr_code_gatein_status == '1' :
                        code = '101'
                    else:
                        code = '106'
                else:
                    code = '107'
            else:
                code = '110'
        else:
            code = '102'

    if code != '102':
        Id = Parking_log.query.filter(Parking_log.qr_code_reserve == qr_code_cit).order_by(
                Parking_log.qr_code_exprie.desc()).first().Id
        message_dict = response_api(code, message_dict=True)
        update_log = Parking_log.query.filter_by(Id=Id).first()
        update_log.kioskout_code = kioskout_code
        update_log.floorout_code = floorout_code
        update_log.resultout_code = code
        if code == '101':
            update_log.opengateout_date = message_dict[code]['opengateout_date']
            update_log.qr_code_gateout_status = message_dict[code]['gate_status']
            
            capacity_countout(parking_code, update_log.reserve_floor)
        db.session.commit()       
        return response_api(code) 
    else:
        return response_api(code) 

