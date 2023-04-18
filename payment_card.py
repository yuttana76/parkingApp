from app import Parking_manage,Parking_member,Parking_log
import datetime
from sqlalchemy import all_, or_

def check_status_card(exp):
    if exp != None:
        day_remaining = datetime.date.today() - exp
        if day_remaining.days < -7 :
            status = 'ยังไม่ถึงกำหนดการ'
        elif day_remaining.days >= -7 and day_remaining.days <= 0:
            status = 'ต่ออายุ'
        elif day_remaining.days > 7:
            status = 'หมดอายุ'
        else:
            status = 'พร้อมชำระ'      
    else:
        status = 'บัตรใหม่'
    return status

def pay_date(payment_date):
    today = datetime.datetime.today().date() 
    if payment_date:
        remaining = today - payment_date
        if remaining.days >= -7 and remaining.days <= 7:
            return 'ผ่าน'
        else :
            return 'ไม่ผ่าน'
    else :
        return 'ผ่าน'


def payment(identity_card):
    cards = []
    limitdate = datetime.datetime.today() -  datetime.timedelta(7)
    data = Parking_member.query.filter_by(
        identity_card = identity_card).filter(or_(
            Parking_member.card_expire_date >= limitdate.strftime('%Y-%m-%d'),
            Parking_member.card_expire_date == None
        )).filter(or_(Parking_member.card_status !='0',Parking_member.card_status == None)).all()
    for i in data:
        user_card =  Parking_manage.query.filter_by(parking_code=i.parking_code).first()
        card = {}
        # card['parking_name'] = user_card.parking_name
        card['card_id'] = i.card_id
        card['price'] = f'{user_card.parking_price:,}'.split('.')[0]
        
        card['type'] = i.vcard_type
        card['status'] = check_status_card(i.card_expire_date) #1=ต่ออายุ 0=บัตรใหม่  2=ยังไม่หมดอายุ
        card['color'] = user_card.line_name
        card['price2'] = int(user_card.parking_price)
        # card['exp'] = i.card_expire_date
        all_log = Parking_log.query.filter_by(card_id=i.card_id)\
            .filter(Parking_log.identity_card==i.identity_card).filter(Parking_log.parking_code==i.parking_code).order_by(Parking_log.Id.desc()).all()
        log = all_log[0]
    
        if user_card.parking_code == 'BL220' :
            print('no deposit')
            card['deposit'] = 0
        elif len(all_log) > 1 and all_log[1].transaction_type == '3' and i.return_card != '1':
            print('old member no deposit')
            card['deposit'] = 0
        else:
            print('have deposit')
            card['deposit'] = int(user_card.deposit_amount)
        if i.card_expire_date != None:
            exp2 = i.card_expire_date + datetime.timedelta(1)
            card['exp'] = exp2.strftime('%d/%m/%Y')
            card['exp2'] = exp2.strftime('%Y-%m-%d')
        else:
            card['exp'] = None
            card['exp2'] = None
        card['payment_status'] = log.payment_status
        card['parking_name'] = log.parking_name
        card['parking_name_eng'] = user_card.parking_name_eng
        card['payment_status'] = str(card['payment_status'])
        card['verify'] = log.verify_status
        card['q'] = log.q_no
        card['paydate'] = pay_date(i.card_expire_date)
        card['id'] = i.Id
        cancel_status = Parking_log.query.filter_by(identity_card=i.identity_card)\
            .filter(Parking_log.parking_code == i.parking_code)\
            .filter(Parking_log.input_type == '1').filter(Parking_log.transaction_type == '3').first()
        cancel_status2 = Parking_log.query.filter_by(identity_card=i.identity_card)\
            .filter(Parking_log.parking_code == i.parking_code)\
            .filter(Parking_log.transaction_type != '3').order_by(Parking_log.Id.desc()).first()
        if cancel_status:
            if cancel_status2.invoice_no:
                card['cancel_status'] = '1'
            else:
                card['cancel_status'] = '0'
        else :
            card['cancel_status'] = '0'
        if log.verify_status == '5':
            continue
        elif log.verify_status !='5':
            cards.append(card)
    return cards

def payment_exp(identity_card):
    cards = []
    limitdate = datetime.datetime.today() -  datetime.timedelta(7)
    data = Parking_member.query.filter_by(
        identity_card = identity_card).filter(or_(
            Parking_member.card_expire_date <= limitdate.strftime('%Y-%m-%d')
        )).filter(or_(Parking_member.card_status !='0',Parking_member.card_status == None)).all()
    for i in data:
        user_card =  Parking_manage.query.filter_by(parking_code=i.parking_code).first()
        card = {}
        card['parking_name'] = user_card.parking_name
        card['card_id'] = i.card_id
        card['price'] = f'{user_card.parking_price:,}'.split('.')[0]
        card['deposit'] = int(user_card.deposit_amount)
        card['type'] = i.vcard_type
        card['status'] = check_status_card(i.card_expire_date) #1=ต่ออายุ 0=บัตรใหม่  2=ยังไม่หมดอายุ
        card['color'] = user_card.line_name
        card['price2'] = int(user_card.parking_price)
        card['exp'] = i.card_expire_date
        if i.card_expire_date != None:
            card['exp'] = i.card_expire_date.strftime('%d/%m/%Y')
        cards.append(card)
    return cards

def neworold(identity_card):
    check_user =Parking_member.query.filter_by(identity_card = identity_card).first()
    if check_user:
        check_user = 1
    elif not check_user:
        check_user = 0
    return check_user