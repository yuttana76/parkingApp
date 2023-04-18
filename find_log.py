import datetime
from app import Parking_log, Parking_manage,Parking_member
from sqlalchemy import or_

def find_last_log(identity_card):
    limitdate = datetime.datetime.today() -  datetime.timedelta(7)
    cards = Parking_member.query.filter_by(identity_card=identity_card).filter(or_(
        Parking_member.card_expire_date>= limitdate.strftime('%Y-%m-%d'),Parking_member.card_expire_date == None)).all()
    transaction = []
    for card in cards:
        log = Parking_log.query.filter_by(identity_card=card.identity_card).filter(
            Parking_log.payment_status =='0').filter(Parking_log.card_id==card.card_id).order_by(Parking_log.Id.desc()).first()
        if log != None:
            transaction.append(log)
    return transaction

def reserve(identity_card):
    limitdate = datetime.datetime.today() -  datetime.timedelta(7)
    cards = Parking_member.query.filter_by(identity_card=identity_card).filter(or_(
        Parking_member.card_expire_date>= limitdate.strftime('%Y-%m-%d'),Parking_member.card_expire_date == None)).all()
    transaction = []
    for card in cards:
        log = Parking_log.query.filter_by(identity_card=card.identity_card).filter(or_(
            Parking_log.verify_status =='3',Parking_log.verify_status =='4')).filter(Parking_log.card_id==card.card_id)\
                .filter(Parking_log.parking_code==card.parking_code).order_by(Parking_log.Id.desc()).first()
        if log != None:
            transaction.append(log)
    return transaction

def card_reserve(cards):
    cards_reserve = []
    for card in cards:
        dict_ = {}
        if card.verify_status == '3':
            queue = Parking_log.query.filter_by(parking_code=card.parking_code).filter(Parking_log.verify_status=='4').count()+1
            dict_['q'] = f'Q{queue:04}'
            dict_['station'] = card.parking_name
            dict_['status'] = 'รอจอง'
            dict_['count'] = queue -1
            dict_['reserve_button'] =f'<button class="btn btn-success" style="width: 150px;" onclick="reserve({card.Id},{queue})">จองคิว</button>'
            dict_['cancel'] = ''
        if card.verify_status == '4':
            que = int(card.q_up)
            dict_['q'] = f'Q{que:04}'
            dict_['station'] = card.parking_name
            dict_['status'] = 'จอง'
            dict_['count'] = que
            dict_['reserve_button'] = ''
            dict_['cancel'] = f'<button class="btn btn-danger" style="width: 150px;" onclick="cancelReserve({card.Id})">ยกเลิกคิว</button>'
        cards_reserve.append(dict_)
    return cards_reserve

def find_log_last_pay(identity_card,station):
    # limitdate = datetime.datetime.today() -  datetime.timedelta(7)
    cards = Parking_member.query.filter_by(identity_card=identity_card)\
            .filter(or_(Parking_member.card_status == '1',Parking_member.card_status == None)).filter(Parking_member.parking_code == station).all()#.filter(or_(Parking_member.card_expire_date>= limitdate.strftime('%Y-%m-%d'),Parking_member.card_expire_date == None))\
    transaction = []
    print(cards)
    for card in cards:
        log = Parking_log.query.filter_by(identity_card=card.identity_card).filter(
            Parking_log.payment_status =='1').filter(Parking_log.card_id==card.card_id).filter(Parking_log.parking_code==card.parking_code).order_by(Parking_log.Id.desc()).first()
        print(log)
        if log != None:
            transaction.append(log)
    return transaction 
