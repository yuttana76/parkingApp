from app import Parking_manage, Carpacity_manage,  Policy, Parking_log, db
import datetime
from flask_login import current_user
from ref2 import genRef2
from flask import request, Response
import json
from db_config import mysql
import hashlib
import time
import multiprocessing as mp


#ploy
def get_reserve_parking_json():
    try:
        Parking = Parking_log.query.filter(Parking_log.identity_card == current_user.identity_card).order_by(
            Parking_log.parking_reserve_date.desc()).first()
        if Parking.qr_code_reserve != None and Parking.qr_code_gateout_status == "1" :
            status_qr = 0
        elif datetime.datetime.now() > Parking.qr_code_exprie :
            status_qr = 0
        else:
            status_qr = 1
    except: #กรณีจองครั้งแรก
        status_qr = 0
    
    print(status_qr)
    station = Parking_manage.query.filter_by(reserve_status = "active").all()    
    stations = []
    for code in station:
        station = {}
        station['no'] = code.parking_code
        station['name'] = code.parking_name
        station['name_en'] = code.parking_name_eng
        if code.parking_image == '' or code.parking_image == None:
            station['image_source'] = "bangraknoithait.jpg"
        elif code.parking_image != '' and code.parking_image != None:
            station['image_source'] = code.parking_image
        if code.line_name == 'สายสีน้ำเงิน':
            station['mrline'] = 'button-1'
        elif code.line_name == 'สายสีม่วง':
            station['mrline'] = 'button-2'
        elif code.line_name == 'สายสีเขียว':
            station['mrline'] = 'button-3'
        
        capacity = Carpacity_manage.query.filter_by(
            parking_code=code.parking_code).first()
        station['emptyparkinglot'] = capacity.reserver_remaining

        station['reserve_floor'] = capacity.reserve_floor.split(",")
        station['reserve_floor_remain'] = capacity.reserve_floor_remain.split(",")

        if station['emptyparkinglot'] == 0:
            station['button'] = 'button'
        else:
            station['button'] = 'submit'
        
        station['status_qr']= status_qr
        stations.append(station)
    print(stations)   
    return stations


def policy_station(station):
    policy = Policy.query.filter_by(policy_name=station).first()
    policy = policy.policy_des.split('\n')
    return policy

def format_period(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60  
    return "%02d:%02d:%02d" % (hour, minutes, seconds)
    


def reserve_period_price(station):
    stations = {}
    columns = Parking_manage.query.filter_by(parking_name = station).first()
    stations['name'] = station
    stations['reserve_checkin_period'] = int(columns.reserve_checkin_period)
    stations['reserve_payment_period'] = int(columns.reserve_payment_period)
    stations['reserve_checkin_period_format'] = format_period(int(columns.reserve_checkin_period)*60)
    stations['reserve_payment_period_format'] = format_period(int(columns.reserve_payment_period)*60)
    stations['reserve_price'] = str(columns.reserve_price)
    stations['no'] = columns.parking_code

    return stations

# reserve_period_price('สถานีแยก คปอ.')

def capacity_countin(parking_code, floor):
    capacity = Carpacity_manage.query.filter_by(parking_code=parking_code).first()
    reserve_count = capacity.reserve_count + 1
    reserve_limit =  capacity.reserve_limit
    reserve_floor = capacity.reserve_floor.split(",")
    reserve_floor_remain = capacity.reserve_floor_remain.split(",")

    reserver_remaining = reserve_limit - reserve_count
    idx  = reserve_floor.index(floor)
    reserve_floor_remain[idx] = str(int(reserve_floor_remain[idx])-1)
    reserve_floor_remain = ','.join(map(str, reserve_floor_remain))

    capacity.reserve_count = reserve_count
    capacity.reserver_remaining = reserver_remaining
    capacity.reserve_floor_remain = reserve_floor_remain
    db.session.commit()

def capacity_countout(parking_code, floor):
    capacity = Carpacity_manage.query.filter_by(parking_code=parking_code).first()
    reserve_count = capacity.reserve_count - 1
    reserve_limit =  capacity.reserve_limit
    reserve_floor = capacity.reserve_floor.split(",")
    reserve_floor_remain = capacity.reserve_floor_remain.split(",")

    reserver_remaining = reserve_limit - reserve_count
    idx  = reserve_floor.index(floor)
    reserve_floor_remain[idx] = str(int(reserve_floor_remain[idx])+1)
    reserve_floor_remain = ','.join(map(str, reserve_floor_remain))
            
    capacity.reserve_count = reserve_count
    capacity.reserver_remaining = reserver_remaining
    capacity.reserve_floor_remain = reserve_floor_remain
    db.session.commit()

def cal_vat(total, percent_vat):
    vat = 1 + percent_vat/100
    amount = round(total/vat, 2)
    vat_in_bath = round(total-amount, 2)
    return amount, vat_in_bath

def insert_reserve_log(station, floor):
    reserve_log = {}
    
    columns = Parking_manage.query.filter_by(parking_name = station).first()
    reserve_log['no'] = columns.parking_code
    reserve_log['parking_type'] = columns.parking_type_name
    reserve_log['input_type'] = '1'
    reserve_log['transaction_type'] = '4'
    reserve_log['first_name'] = current_user.first_name
    reserve_log['last_name'] = current_user.last_name
    reserve_log['identity_card'] = current_user.identity_card
    reserve_log['phone'] = current_user.phone
    reserve_log['total'] = int(columns.reserve_price)
    reserve_log['parking_reserve_date'] = datetime.datetime.now()
    amount, vat_in_bath = cal_vat(int(columns.reserve_price), 7)
    reserve_log['amount'] = amount
    reserve_log['vat'] = vat_in_bath
    id_ = Parking_log.query.filter(Parking_log.Id >= 0).order_by(Parking_log.Id.desc()).first().Id +1
    orderNumber = genRef2(a=0, id_=id_,station=reserve_log['no'])
    reserve_log['orderNumber'] = orderNumber
    reserve_log['station'] = station
    reserve_log['reserve_floor'] = floor

    new_log = Parking_log(
        parking_code=reserve_log['no'],
        parking_name=reserve_log['station'],
        parking_type_name=reserve_log['parking_type'],
        input_type=reserve_log['input_type'],
        transaction_type=reserve_log['transaction_type'],
        first_name=reserve_log['first_name'],
        last_name=reserve_log['last_name'],
        identity_card=reserve_log['identity_card'],
        phone=reserve_log['phone'],
        total=reserve_log['total'],
        amount=amount,
        vat=vat_in_bath,
        parking_reserve_date=datetime.datetime.now(),
        orderNumber = reserve_log['orderNumber'],
        reserve_floor = reserve_log['reserve_floor'] 
    )
    db.session.add(new_log)
    db.session.commit()
    capacity_countin(reserve_log['no'], floor)
    return reserve_log

def gen_securityKey_pd(ref2,total):  # passachon
    cur = mysql.connection.cursor()
    cur.execute('select secure_hash_secret_pd from key_info')
    res = cur.fetchone()
    merchantId = '900000303'  
    orderRef = ref2
    currcode = '764'  
    amount = str(total)
    payType = 'N' 
    SecureHashKey = res[0] 
    print("*******",SecureHashKey)
    securityKey = merchantId+'|'+orderRef+'|' + \
        currcode+'|'+amount+'|'+payType+'|'+SecureHashKey
    securityKey = securityKey.encode('utf-8')
    h = hashlib.sha512(securityKey)
    return h.hexdigest()


def payment_timeout(orderNumber, sec_):
    sec = sec_/3
    time.sleep(sec)
    Parking = Parking_log.query.filter(Parking_log.orderNumber ==orderNumber).order_by(
        Parking_log.parking_reserve_date.desc()).first()
    print(Parking)
    time.sleep(sec)
    Parking = Parking_log.query.filter(Parking_log.orderNumber ==orderNumber).order_by(
        Parking_log.parking_reserve_date.desc()).first()
    print(Parking)
    time.sleep(sec)
    timeout = 1
    if timeout == 1 and Parking.payment_status != '1':
        capacity_countout(Parking.parking_code, Parking.reserve_floor)
        print('ตรงเงื่อนไข')
    else:
        print('ไม่ตรงเงื่อนไข')

def qr_opengate_timeout(orderNumber, sec):
    time.sleep(sec)
    Parking = Parking_log.query.filter(Parking_log.orderNumber ==orderNumber).order_by(
        Parking_log.parking_reserve_date.desc()).first()
    timeout = 1
    if timeout == 1 and Parking.payment_status != '1' :
        if Parking.qr_code_gatein_status != '1':
            capacity_countout(Parking.parking_code, Parking.reserve_floor)
            print('ตรงเงื่อนไข')
    else:
        print('ไม่ตรงเงื่อนไข')

def remaining_time(orderNumber, period):
    parking_reserve_date = Parking_log.query.filter(Parking_log.orderNumber ==orderNumber).order_by(
        Parking_log.parking_reserve_date.desc()).first().parking_reserve_date
    payment_exp_date = parking_reserve_date + datetime.timedelta(minutes=period)
    today = datetime.datetime.today()
    if parking_reserve_date:
        datecalculate = payment_exp_date - today
        remaining = datecalculate.total_seconds()

        if remaining > 0:
            payment_exp_date = payment_exp_date.strftime('%H:%M:%S')
            remaining = int(remaining)
            hour = remaining // 3600 
            remaining = remaining - (hour * 3600)
            minute = remaining // 60
            second = remaining - (minute * 60)
            countdowntimer = f'{str(hour).zfill(2)}:{str(minute).zfill(2)}:{str(second).zfill(2)}'
        else:
            payment_exp_date = '00:00:00'
            countdowntimer = '00:00:00'
    else:
        countdowntimer = '00:00:00'
    print(countdowntimer)
    return countdowntimer

def payment_exp_date(orderNumber, parking_name):
    parking_reserve_date = Parking_log.query.filter(Parking_log.orderNumber ==orderNumber).order_by(
        Parking_log.parking_reserve_date.desc()).first().parking_reserve_date
    reserve_payment_period = int(Parking_manage.query.filter_by(parking_name=parking_name).first().reserve_payment_period)
    payment_exp = parking_reserve_date + datetime.timedelta(minutes=reserve_payment_period)
    print(payment_exp)
    return payment_exp

def gen_qrcode_opengate(ref1,ref2,station,floor):
    ref1_ = ref1[-5:]
    my_qrcode_json = {"ref1":ref1_, "ref2":ref2, "station":station, "floor":floor}
    my_qrcode = str(my_qrcode_json)
    
    log = Parking_log.query.filter(Parking_log.orderNumber == ref2).order_by(
        Parking_log.parking_reserve_date.desc()).first()
    print(log)
    log.qr_code_reserve = my_qrcode
    db.session.commit()
    return my_qrcode

def response_api_qrlog(code, text_qr):
    message_dict = {
        '100':{'message':'success', 'description':'ระบบทำการบันทึก Qr code เรียบร้อย', 'qr_code':text_qr},
        '101':{'message':'fail', 'description':'รหัสลานจอดไม่ถูกต้อง', 'qr_code':text_qr},
        '102':{'message':'fail', 'description':'username หรือ password ไม่ถูกต้อง', 'qr_code':text_qr}
    }
    body = {
        'status':{
                'code':code,
                'message':message_dict[code]['message'],
                'description':message_dict[code]['description'],
                'qr_code':message_dict[code]['qr_code'],
                'timestamp':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    headers = {
        'Content-Type': "application/json"
    }
    payload = json.dumps(body)
    res = Response(headers=headers,response=payload)
    return res

def gen_qr_parking_log():
    username = request.get_json()['username']
    password = request.get_json()['password']
    parking_code_cit = request.get_json()['stationCode']
    # print(parking_code_cit)
    id_ = Parking_log.query.filter(Parking_log.Id >= 0).order_by(Parking_log.Id.desc()).first().Id+1
    ref1 = "3333333333333"
    ref2 = "CIT"+parking_code_cit+str(id_).zfill(10)
    # print(ref2)
    if request.method == 'POST' and username == 'jparkapi' and password == '123456' :
        
        if parking_code_cit in ['N1013','N1014']:
            code = '100' 
            parking_name='สถานีแยก คปอ.'if parking_code_cit == 'N1013' else 'สถานีคูคต'
            text_qr = {"ref1":ref1[-5:], "ref2":ref2, "station":parking_name, "floor":"1"}  
            log = Parking_log(
                parking_code=parking_code_cit,
                parking_name=parking_name,
                parking_type_name="CIT",
                input_type="1",
                transaction_type="4",
                first_name="test",
                last_name="test",
                identity_card=ref1,
                phone="0800000000",
                total=20,
                amount=18.69,
                vat=18.69,
                parking_reserve_date=datetime.datetime.now(),
                orderNumber= ref2,
                reserve_floor="1",
                payment_name = "3",
                payment_status = "1",
                payment_date = datetime.datetime.now(),
                qr_code_reserve = str(text_qr),
                qr_code_exprie = datetime.datetime.now() + datetime.timedelta(minutes=60),
                qr_show_exp = datetime.datetime.now() + datetime.timedelta(days=1)
            )
            db.session.add(log)
            db.session.commit()

            # capacity_countin(parking_code_cit, '1')
            return response_api_qrlog(code, str(text_qr))
        else:
            code = '101'
            return response_api_qrlog(code, None)
    else:
        code = '102'
        return response_api_qrlog(code, None)