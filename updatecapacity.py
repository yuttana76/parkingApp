import sqlalchemy
from app import Carpacity_manage,db,Parking_log,Parking_manage,Parking_member
from sqlalchemy import extract
import datetime

def capacity_count(parking_code,log_id):
    today = datetime.datetime.today()
    capacity = Carpacity_manage.query.filter_by(parking_code=parking_code).first()
    count_online = 0
    all_member1 = Parking_member.query.filter(Parking_member.card_expire_date > today).filter(Parking_member.parking_code==parking_code).all()
    for member in all_member1:
        check_log = Parking_log.query.filter_by(card_id=member.card_id).filter(Parking_log.parking_code == member.parking_code)\
            .filter(Parking_log.transaction_type != '3').filter(Parking_log.service_start_date < today).order_by(Parking_log.Id.desc()).first()
        if check_log:
            if check_log.input_type == '1':
                count_online +=1
    
    count_contect_site = 0
    all_member = Parking_member.query.filter(Parking_member.card_expire_date > today).filter(Parking_member.parking_code==parking_code).all()
    for member in all_member:
        check_log = Parking_log.query.filter_by(card_id=member.card_id).filter(Parking_log.parking_code == member.parking_code)\
            .filter(Parking_log.transaction_type != '3').filter(Parking_log.service_start_date < today).order_by(Parking_log.Id.desc()).first()
        if check_log:
            if check_log.input_type == '2':
                count_contect_site +=1
    member_remaining = capacity.member_limit - (count_online + count_contect_site) + capacity.adjust_member
    capacity.count_online = count_online
    capacity.count_contect_site = count_contect_site
    capacity.member_remaining = member_remaining if member_remaining >= 0 else 0

    #######################invoice no###############################
    if log_id:
        log_update = Parking_log.query.filter_by(Id=log_id).first()
        station = Parking_manage.query.filter_by(parking_code=parking_code).first()
        
        if log_update.transaction_type == '5':
            return 'success'

        if log_update.invoice_no:
            pass
        else:
            last_invoice = station.start_inv_no
            invoice = last_invoice.split('/')[0]+ '/' + station.parking_branch+'/' +str(int(last_invoice.split('/')[-1])+1).zfill(4)
            station.start_inv_no = invoice
            log_update.invoice_no = invoice
            same_branch = Parking_manage.query.filter_by(parking_branch = station.parking_branch).all()
            if same_branch != []:
                    for branchs in same_branch:
                        branchs.start_inv_no = invoice
        
        if log_update.deposit_amount == 0:
            db.session.commit()
            return 'Success'
        
        else:
            if log_update.invoice_deposit:
                pass
            else:
                invoice2 = invoice.split('/')[0]+ '/' + station.parking_branch+'/' +str(int(invoice.split('/')[-1])+1).zfill(4)
                station.start_inv_no = invoice2
                log_update.invoice_deposit = invoice2
                same_branch2 = Parking_manage.query.filter_by(parking_branch = station.parking_branch).all()
                if same_branch2 != []:
                    for branchs in same_branch2:
                        branchs.start_inv_no = invoice2
                db.session.commit()
                return 'Success'
    else:
        db.session.commit()
        return 'Success'

def month_to_day(y):
    if (y%400 == 0 ) or (y%4 == 0) and (y%100 != 0):
        return 28
    else :
        return 27

def genday(number_of_month,start_date):
    month_ = {
            '01':30,
            '02':28 if (int(start_date.split('-')[0])%400 == 0 ) or (int(start_date.split('-')[0])%4 == 0) and (int(start_date.split('-')[0])%100 != 0) else 27 ,
            '03':30,
            '04':29,'05':30,'06':29,
            '07':30,'08':30,'09':29,
            '10':30,'11':29,'12':30
        }
    day_plus = number_of_month -1
    if number_of_month ==1:
        return month_[start_date.split('-')[1]]
    else:
        day_count = 0
        for i in range(int(start_date.split('-')[1]),int(start_date.split('-')[1])+number_of_month):
            day_count += month_[str(i).zfill(2)]
            print(i,':',month_[str(i).zfill(2)])
            if i == 12:
                number_of_month = int(start_date.split('-')[1])+number_of_month -13
                y_m_d = start_date.split('-')
                start_date = f'{int(y_m_d[0])+1}-{1}-{y_m_d[2]}'
                month_['02'] = 28 if (int(start_date.split('-')[0])%400 == 0 ) or (int(start_date.split('-')[0])%4 == 0) and (int(start_date.split('-')[0])%100 != 0) else 27
                for i in range(int(start_date.split('-')[1]),int(start_date.split('-')[1])+number_of_month):
                    day_count += month_[str(i).zfill(2)]
                    print(i,':',month_[str(i).zfill(2)])
                break
        return day_count +day_plus