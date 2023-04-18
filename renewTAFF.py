from datetime import timedelta
import datetime
import calendar
from updatecapacity import genday 
from app import Parking_member,db
from find_log import find_log_last_pay

def renew_card_TAFF_orAll(cid,count_month,page,identity_card,parking_code):
    ref1 = identity_card
    find = find_log_last_pay(ref1,parking_code)
    print('******find******: ', find)
    if len(find) > 0 :
        print(find[0])
        service = find[0].service_start_date
        result = Parking_member.query.filter_by(card_id=cid).filter(Parking_member.parking_code==parking_code)\
            .filter(Parking_member.identity_card == ref1).first()
        result.card_expire_date = service + datetime.timedelta(genday(int(find[0].month),service.strftime('%Y-%m-%d')))
        db.session.commit()
        return 'success'
    return 'success'
    



def update_renewCard(cid,parking_code,sum, date, today):
    new_expi = date+timedelta(days=sum)
    update_member = Parking_member.query.filter_by(card_id=cid,parking_code=parking_code).first()
    update_member.card_last_read_date = today
    update_member.card_expire_date = new_expi
    db.session.commit()
    return new_expi

def update_renewCard_dashboard(cid,parking_code, sum, date):
    new_expi = date+timedelta(days=sum)
    update_member = Parking_member.query.filter_by(card_id=cid,parking_code=parking_code).first()
    update_member.card_expire_date = new_expi
    db.session.commit()
    return new_expi


def get_numofMonth(year, month):  # จำนวนวันแต่ละเดือน
    first_weekday, num_days_in_month = calendar.monthrange(year, month)
    print(num_days_in_month)
    return num_days_in_month-1


def cal_numofMonth(year, month,count_month):
    count = count_month  # จำนวนเดือนที่ลูกค้าต่อ
    sum = 0
    month = month+1
    for i in range(count):
        month = month+1
        if month > 12:
            year = year + 1
            month = 1
        sum = sum + get_numofMonth(year, month)
    return sum


