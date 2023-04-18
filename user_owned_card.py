import datetime
from app import Parking_member,Parking_log,db
from sqlalchemy import or_
import random

def owned_card(identity_card):
    limitdate = datetime.datetime.today() -  datetime.timedelta(7) 
    data = Parking_member.query.filter_by(
        identity_card = identity_card).filter(or_(Parking_member.card_status =='1',Parking_member.card_status == None)).all()

    for card in data:
        print( card.card_id ,'card id')
        log = Parking_log.query.filter_by(card_id=card.card_id).filter(Parking_log.parking_code==card.parking_code).order_by(Parking_log.Id.desc()).first()
        if card.card_expire_date:
            if (datetime.date.today() - card.card_expire_date).days > 7  :
                print('1')
                card.card_status = '0'
                cancel_log = Parking_log(
                    card_id=card.card_id,
                    input_type = 1,
                    transaction_type = 3,
                    identity_card = card.identity_card,
                    last_name = card.last_name_th,
                    first_name = card.first_name_th,
                    phone = card.phone,
                    parking_code = log.parking_code,
                    parking_name = log.parking_name,
                    parking_type_name = log.parking_type_name,
                    verify_status = log.verify_status,
                    )
                db.session.add(cancel_log)
                db.session.commit()
                data.remove(card)
        else:
            if datetime.date.today() > log.lastdate_pay:
                print('2')
                card.card_status = '0'
                cancel_log = Parking_log(
                    card_id=card.card_id,
                    input_type = 1,
                    transaction_type = 3,
                    identity_card = card.identity_card,
                    last_name = card.last_name_th,
                    first_name = card.first_name_th,
                    phone = card.phone,
                    parking_code = log.parking_code,
                    parking_name = log.parking_name,
                    parking_type_name = log.parking_type_name,
                    verify_status = log.verify_status,
                    )
                db.session.add(cancel_log)
                db.session.commit()
                data.remove(card)
    return data

def create_home_address(cards):
    if cards.address_no != None:
        address_no = str(cards.address_no) + ' '
    else:
        address_no = ''
    if cards.village != None:
        village = 'หมู่.' + str(cards.village)+' '
    else:
        village = ''
    if cards.district != None:
        district = 'เขต '+ str(cards.district) +' '
    else:
        district = ''
    if cards.sub_district != None:
        sub_district = 'แขวง ' + str(cards.sub_district) +' '
    else:
        sub_district =''
    if cards.province != None:
        province = str(cards.province) + '.'
    else :
        province = ''
    if cards.postal_code !=None:
        postal = str(cards.postal_code)
    else:
        postal = ''
    home_address = address_no + village + district + sub_district + province + postal
    if home_address == '':
        home_address = '-'
    return home_address

def create_company_address(cards):
    if cards.company_no != None:
        address_no = str(cards.company_no) + ' '
    else:
        address_no = ''
    if cards.company_village != None:
        village = 'หมู่.' + str(cards.company_village)+' '
    else:
        village = ''
    if cards.company_district != None:
        district = 'เขต '+ str(cards.company_district) +' '
    else:
        district = ''
    if cards.company_sub_district != None:
        sub_district = 'แขวง ' + str(cards.company_sub_district) + ' '
    else:
        sub_district = ''
    if cards.company_province != None:
        province = str(cards.company_province) + '.'
    else :
        province = ''
    if cards.company_postal_code !=None:
        postal = str(cards.company_postal_code)
    else:
        postal = ''
    company_address = address_no + village + district + sub_district + province + postal
    if company_address == '':
        company_address = '-'
    return company_address
  

def randomAlpha_cid(length):  
    alphabet = 'qwertyuiopasdfghjklzxcvbnm'
    result = ''.join((random.choice(alphabet)) for x in range(length))  
    return result

def checkCardNotRandom(card):
  alphabet = 'qwertyuiopasdfghjklzxcvbnm'
  for i in card:
    if i not in list(alphabet):
      return True
  return False

def checkCardNotReMem(transaction):
    identity_card = transaction.identity_card
    card_id = transaction.card_id
    all_log = Parking_log.query.filter_by(identity_card=identity_card)\
        .filter(Parking_log.card_id == card_id)\
        .filter(Parking_log.parking_code == transaction.parking_code).order_by(Parking_log.Id.desc()).all()
    if len(all_log)>1:
        transaction_type_of_log2 = all_log[1].transaction_type
        print('*****transaction_type_of_log2*******: ', transaction_type_of_log2)
        if transaction_type_of_log2 == '3':
            return False
        else:
            return True
    else:
        return True