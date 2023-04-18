from app import (
    Parking_manage, Policy, app,Parking_log as pl
)
from flask_login import login_required, current_user
from flask import render_template,request,session,redirect, jsonify,url_for
from getReserveParking import get_reserve_parking_json, policy_station, reserve_period_price, insert_reserve_log, gen_securityKey_pd,payment_timeout, remaining_time, payment_exp_date, gen_qrcode_opengate, gen_qr_parking_log
import datetime
import multiprocessing as mp
from ktb_Qrcode import text_qr
from db_config import mysql 
import datetime
import multiprocessing as mp
from apiBooking import api_bookin_log, api_bookout_log
from form import Reserve_step3
from province import get_district, get_postcode, get_province, get_subdistrict


#ploy
@app.route('/reserve-step1', methods=['GET', 'POST'])
@login_required
def reserve_step1():
    if request.method == 'GET':
        data = get_reserve_parking_json()
        print(data[0]['button'])
        print(data[0]['reserve_floor'])
        return render_template('/reserve-step1.html', parkings=data)

    elif request.method == 'POST':
        floor = request.form.get('floor')
        station = request.form.get('submit_floor')
        session['station'] = station
        session['floor'] = floor
        # print(floor)
        return redirect('/reserve-step2')

#ploy
@app.route('/reserve-step2', methods=['GET', 'POST'])
@login_required
def reserve_step2():
    station = session.get('station')
    policy = policy_station(station)
    detail = reserve_period_price(station)
    return render_template('reserve-step2.html', policy= policy, detail=detail)

#ploy
@app.route('/reserve-step3', methods=['GET', 'POST'])
def reserve_step3():
    station = session.get('station')
    floor = session.get('floor')
    form = Reserve_step3()
    reserve_station_detail = reserve_period_price(station)
    if request.method == 'GET':
        current_date =  datetime.datetime.now().strftime('%d/%m/%Y')
        session['reserve_station_detail'] = reserve_station_detail
        province = get_province()
        form.province_home.choices = [(i, i) for i in province]
        form.province_company.choices = [(i, i) for i in province]

        return render_template('reserve-step3.html', form=form, reserve_station_detail=reserve_station_detail, current_date=current_date, floor=floor)

    elif request.method == 'POST':
        reserve_log = insert_reserve_log(station,floor,form)
        session['reserve_log'] = reserve_log
        if(__name__=='reserveParking'):
            sec = 60*reserve_station_detail['reserve_payment_period']
            p = mp.Process(target=payment_timeout, args=(reserve_log['orderNumber'],sec,))
            p.start()
            return redirect('/payment-reserve')

@app.route('/payment-reserve', methods=['GET', 'POST'])
def payment_reserve():
    ref1 = session.get('reserve_log')['identity_card']
    ref2 = session.get('reserve_log')['orderNumber']
    
    total = session.get('reserve_log')['total']
    securityKey = gen_securityKey_pd(ref2,total)
    reserve_station_detail = session.get('reserve_station_detail')
    current_date =  datetime.datetime.now().strftime('%d/%m/%Y')
    remaining=remaining_time(ref2,reserve_station_detail['reserve_payment_period'])

    return render_template('payment-reserve.html',ref1=ref1,ref2=ref2,total=total,securityKey=securityKey, reserve_station_detail = reserve_station_detail, current_date=current_date, remaining=remaining)


@app.route('/qrcode-reserve-payment', methods=['GET', 'POST'])
def qrcode_reserve_pay():
    ref1 = session.get('reserve_log')['identity_card']
    ref2 = session.get('reserve_log')['orderNumber']
    total = str(session.get('reserve_log')['total'])
#    payment_exp = payment_exp_date(ref2, station)
#    now = datetime.datetime.now()
#    if now < payment_exp:
    qrcode = text_qr(total, ref1, ref2)  # (money,ref1,ref2)
    reserve_station_detail = session.get('reserve_station_detail')
    remaining = remaining_time(ref2,reserve_station_detail['reserve_payment_period'])
    # print(qrcode)
    return render_template('qrcode-reserve-payment.html',qrcode=qrcode, remaining=remaining)
 
 

@app.route('/qrcode-opengate')
def qrcode_opengate():
    today = datetime.datetime.now()
    sample = pl.query.filter(
        (pl.identity_card == current_user.identity_card)&\
        (pl.transaction_type == '4')
    ).order_by(pl.Id.desc()).first()
    parking = Parking_manage.query.filter_by(parking_code = sample.parking_code).first()
    text_qrcode = gen_qrcode_opengate(sample.identity_card, sample.orderNumber,parking.parking_name_eng,sample.reserve_floor)
    
    
    reserve_log = pl.query.with_entities(pl.parking_name,pl.qr_code_exprie)\
        .filter_by(orderNumber= sample.orderNumber)\
        .filter(pl.transaction_type == '4').filter(pl.qr_show_exp >= today).all()
    if reserve_log:
        data = []
        log = list(reserve_log[-1])
        checkin_exp = sample.qr_code_exprie
        datecalculate = checkin_exp - today
        remaining = datecalculate.total_seconds()
        if remaining > 0:
            checkin_exp = checkin_exp.strftime('%H:%M:%S')
            remaining = int(remaining)
            hours = str(remaining // 3600).zfill(2)
            minute = str(remaining % 3600 //60).zfill(2)
            countdowntimer = f'{hours}:{minute}:00'
            # print(countdowntimer)
            log.append(countdowntimer)
            data.append(log)
        else:
            checkin_exp = '00:00:00'
            countdowntimer = '00:00:00'
            log.append(countdowntimer)
            data.append(log)
    else:
        data = []
    # print(data)
    return render_template('qrcode-opengate.html',data=data,text_qrcode=text_qrcode, reserve_station_detail=parking.parking_name,floor=sample.reserve_floor)

@app.route('/pay/success')
def update_paymentsuccess():
    return render_template('success-payment-Reserve.html')

@app.route('/pay/fail')
def update_paymentfail():
    return render_template('fail-payment-Reserve.html')

@app.route('/pay/cancel')
def update_paymentcancel():
    return render_template('cancel-payment-Reserve.html')


 

@app.route('/v1/booking/in', methods=['POST'])
def booking_in():
    res = api_bookin_log()
    return res

@app.route('/v1/booking/out', methods=['POST'])
def booking_out():
    res = api_bookout_log()
    return res

@app.route('/api/check-qr-status')
def check_qr_status():
    Parking = pl.query.filter(pl.identity_card == current_user.identity_card).order_by(
            pl.payment_date.desc()).first()
    if Parking.qr_code_gatein_status == "1":
        return jsonify({'message':'success'})
    else :
        return jsonify({'message':'fail'})

@app.route('/api/gen-qrcode', methods=['GET', 'POST'])
def api_gen_qrcode():
    res = gen_qr_parking_log()
    return res

@app.route('/api/query-reserve-address', methods=['GET', 'POST'])
def query_reserve_address():
    try:
        log = pl.query.filter_by(identity_card = current_user.identity_card).order_by(
        pl.Id.desc()).first()
        print(log)
        # log = pl.query.filter_by(Id = 6666).order_by(pl.Id.desc()).first()
        data = {
            'address_no':log.address_no,
            'unit_home':log.unit_home,
            'village':log.village,
            'alley':log.alley,
            'street':log.street,
            'sub_district':log.sub_district,
            'district':log.district,
            'province':log.province,
            'postal_code':log.postal_code,
            
            'company_name':log.company_name,
            'company_no':log.company_no,
            'company_unit':log.company_unit,
            'identity_com':log.identity_com,
            'company_village':log.company_village,
            'company_alley':log.company_alley,
            'company_street':log.company_street,
            'company_sub_district':log.company_sub_district,
            'company_district':log.company_district,
            'company_province':log.company_province,
            'company_postal_code':log.company_postal_code,
        }
    except:
        data={}
    return jsonify(data)