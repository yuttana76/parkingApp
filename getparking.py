from app import Parking_manage, Carpacity_manage, Parking_log, db, Parking_member
from flask_login import current_user
import datetime
from sqlalchemy import or_
from apiGetParkRT import find_availability

def get_parking_json():
    station = Parking_manage.query.filter_by(parking_status = 'active').all()
    stations = []
    limitdate = datetime.datetime.today() -  datetime.timedelta(7)
    card = Parking_member.query.filter_by(
        identity_card=current_user.identity_card).filter(or_(Parking_member.card_expire_date >= limitdate.strftime('%Y-%m-%d'),Parking_member.card_expire_date == None))\
            .filter(or_(Parking_member.card_status !='0',Parking_member.card_status == None)).all() #.filter(Parking_member.card_status ==1) เพิ่มตอนขึ้นระบบ
    print(len(card))
    if len(card) == 1:
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
            carpacity = Carpacity_manage.query.filter_by(
                parking_code=code.parking_code).first()
            station['allfreeparking'] = carpacity.member_limit
            station['nfreeparking'] = carpacity.member_remaining
            print(carpacity.member_remaining)
            print(type(carpacity.member_remaining))
            if code.parking_status == 'inactive' or (card[0].parking_code == code.parking_code) or (carpacity.member_remaining == 0): 
                station['button'] = 'button'
            else:
                station['button'] = 'submit'
            if code.parking_code == card[0].parking_code:
                station['alert'] = f"alert('ไม่สามารถเลือกสถานีที่มีบัตรอยู่แล้วได้')"
            else:
                station['alert'] = ''
            stations.append(station)
    elif len(card) == 2:
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
            carpacity = Carpacity_manage.query.filter_by(
                parking_code=code.parking_code).first()
            station['allfreeparking'] = carpacity.member_limit
            station['nfreeparking'] = carpacity.member_remaining
            station['button'] = 'button'
            station['alert'] = f"alert('ไม่สามารถเลือกใช้บัตรได้เกิน2ใบ')"
            # if code.parking_status =='inactive' or (card[0].parking_code == code.parking_code) or (card[1].parking_code == code.parking_code):
            #     station['button'] = 'button'
            # else:
            #     station['button'] = 'summit'
            # if (code.parking_code == card[0].parking_code) or (code.parking_code == card[1].parking_code):
            #     station['alert'] = f"alert('ไม่สามารถเลือกสถานีที่มีบัตรอยู่แล้วได้')"
            # else:
            #     station['alert'] = ''
            stations.append(station)
    else:
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
            carpacity = Carpacity_manage.query.filter_by(
                parking_code=code.parking_code).first()
            station['allfreeparking'] = carpacity.member_limit
            station['nfreeparking'] = carpacity.member_remaining
            if code.parking_status == 'inactive' or (carpacity.member_remaining == 0):
                station['button'] = 'button'
            else:
                station['button'] = 'submit'
            station['alert'] = ''
            stations.append(station)
    db.session.commit()
    return stations


def get_parking_json2():
    station = Parking_manage.query.all()
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
            station['card_hover_detail_color'] = 'blueline'
        elif code.line_name == 'สายสีม่วง':
            station['mrline'] = 'button-2'
            station['card_hover_detail_color'] = 'purpleline'
        elif code.line_name == 'สายสีเขียว':
            station['mrline'] = 'button-3'
            station['card_hover_detail_color'] = 'greenline'
        carpacity = Carpacity_manage.query.filter_by(
                parking_code=code.parking_code).first()
        station['allfreeparking'] = find_availability(code.parking_name)['ncarrem']
        station['nfreeparking'] = carpacity.member_remaining
        if code.parking_name in ['สถานีห้วยขวาง','สถานีศูนย์วัฒนธรรม (อาคารจอด)','สถานีเพชรบุรี','สถานีแยก คปอ.','สถานีคูคต']:
            station['button'] = 'submit'
            station['alert'] = 'console.log("")'
        elif code.parking_status == 'inactive' :
            station['button'] = 'button'
            station['alert'] = "alert('สถานีนี้ยังไม่เปิดให้บริการ')"
        else:
            station['button'] = 'submit'
            station['alert'] = 'console.log("")'
        stations.append(station)
    return stations

