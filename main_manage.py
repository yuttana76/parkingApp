# from os import path
# from re import U
# from main import parking_info
# from crypt import methods
from types import MethodWrapperType
from apiBooking import response_api
from create_address_taxinv import create_address, create_address_company
from directlink import payment
from app import *
from flask import json, render_template, request, redirect, url_for, session, jsonify
from datetime import date, datetime
#passachon###################
from voidFastpay import void_fastpay
# from suds.client import Client
from datetime import timedelta
import datetime
import calendar
from ref2 import genRef2
from renewTAFF import renew_card_TAFF_orAll
#passachon###################
from db_config import mysql  # import sql
#ittipon#####################
from province import get_district, get_postcode, get_province, get_subdistrict
from payment_card import check_status_card
from file_customize import custom_file
from sqlalchemy import or_,extract
from flask_login import logout_user, current_user, login_user
from get_cus_id import generate_cus_id
from thaibath import ThaiBahtConversion,change_to_thaitime
from flask_mail import Message
from updatecapacity import capacity_count, genday, month_to_day
from dateutil.relativedelta import relativedelta
import json
from greenline.cardlost.usecase import send_card_lost_data_to_cit
from greenline.returncard.usecase import send_card_return_data_to_cit
#ittipon#####################
from user_owned_card import checkCardNotRandom
from apiMember import ApiMember
from senddatatolocal import send_data_to_publish_service_with_ordernumber
from mail_notification import change_verify_status_notification
import urllib.parse


@app.route('/manage/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        # url = 'http://103.196.158.19:81/LeaveService.svc?wsdl'  
        # client = Client(url)
        # suds_object = client.service.AuthenticateUserFromAD(username,password)
        # if suds_object.AuthenticateUserFromADResult is None:
        #     print(suds_object.errorMessage)
        #     print("IN AD")
        # else:
        #     return redirect(url_for('dashboard')) 
        cursor = mysql.connection.cursor()
        sql = "SELECT role_id FROM user_manage where username =%s AND password =%s"
        val = (username, password)
        cursor.execute(sql, val)
        account = cursor.fetchone()
        if account:
            session['username'] = username #passachon
            if account[0] == 5:
                user_log = Login_logout_log(user=username,login_type='manage',ip_address=request.remote_addr,login_datetime=datetime.datetime.today())
                db.session.add(user_log)
                db.session.commit()
                return redirect(url_for('extend_card'))
            else:
                cursor = mysql.connection.cursor()
                cursor.execute("SELECT permission_page_no FROM user_role where role_id =%s",str(account[0]))
                per_page =  cursor.fetchone()
                per_page = per_page[0].split(',')
                session['per_page'] = per_page
                user_log = Login_logout_log(user=username,login_type='manage',ip_address=request.remote_addr,login_datetime=datetime.datetime.today())
                db.session.add(user_log)
                db.session.commit()
                return redirect(url_for('dashboard'))
        else:
            sql = "SELECT * FROM user_manage where username =%s"
            val = (username,)
            cursor.execute(sql, val)
            account = cursor.fetchone()
            if account:
                error = 'รหัสผ่านไม่ถูกต้อง!'
            else:
                error = 'ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง!'
    return render_template('manage/login-backoffice.html', error=error)


@app.route('/manage/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'GET':
        month = datetime.datetime.now().month
        year = datetime.datetime.now().year
        listcode = get_codePark()
        format_strings = ','.join(['%s'] * (len(listcode)))
        cursor = mysql.connection.cursor()
        cursor.execute('select SUM(total) from parking_log WHERE payment_status="1" AND DATE(payment_date)=CURDATE() AND parking_code IN ({listcode}) AND void IS NULL'.format(listcode=format_strings),listcode)
        result = cursor.fetchone()
        total_today = result[0]
      
        query_params = listcode
        query_params.append(month)
        query_params.append(year)
        cursor = mysql.connection.cursor()
        cursor.execute('select COUNT(id) from parking_log WHERE transaction_type="1" AND  parking_code IN ({listcode}) AND MONTH(parking_register_date)=%s AND YEAR(parking_register_date)=%s AND (verify_status="2" OR verify_status IS NULL) '.format(listcode=format_strings),query_params)
        result = cursor.fetchone()
        count_new = result[0]
        cursor = mysql.connection.cursor()
        cursor.execute('select COUNT(id) from parking_log WHERE transaction_type="2" AND parking_code IN ({listcode}) AND MONTH(approve_date)=%s AND YEAR(approve_date)=%s'.format(listcode=format_strings),query_params)
        result = cursor.fetchone()
        count_old = result[0]
        cursor = mysql.connection.cursor()
        cursor.execute('select SUM(total) from parking_log WHERE payment_status="1" AND parking_code IN ({listcode}) AND MONTH(payment_date)=%s AND YEAR(payment_date)=%s AND void IS NULL'.format(listcode=format_strings),query_params)
        result = cursor.fetchone()
        total_month = result[0]
        count_q = '-'
        if total_month is None:
            total_month = 0
        if total_today is None:
            total_today= 0
 
        return render_template('manage/dashboard.html',count_new=count_new,count_old=count_old,total_month=total_month,total_today=total_today,count_q=count_q)
 
 ############################################################ittipon##############################################################
    if request.method == 'POST':
        print(request.form)
        service_type = request.form.get('service_type')
        station = Parking_manage.query.filter_by(
            Id=request.form.get('parking_station')).first()
        parking_code = station.parking_code
        parking_name = station.parking_name
        print(parking_name)
        # register_date = request.form.get('register_date')
        identity_card = request.form.get('identity_card')
        first_name = request.form.get('first_name_th')
        last_name = request.form.get('last_name_th')
        phone = request.form.get('phone')
        # home address
        address_no = request.form.get('address_no')
        village = request.form.get('village')
        alley = request.form.get('alley')
        street = request.form.get('street')
        province = request.form.get('province') if request.form.get('province') != '' else None
        district = request.form.get('district') if request.form.get('district') != '' else None
        sub_district = request.form.get('sub_district') if request.form.get('sub_district') != '' else None
        postal_code = request.form.get('postal_code') if request.form.get('postal_code') != '' else None
        # company address
        company_name = request.form.get('company_name')
        company_no = request.form.get('company_no')
        company_village = request.form.get('company_village')
        company_alley = request.form.get('company_alley')
        company_street = request.form.get('company_street')
        company_province = request.form.get('company_province') if request.form.get('company_province') != '' else None
        company_district = request.form.get('company_district') if request.form.get('company_district') != '' else None
        company_sub_district = request.form.get('company_sub_district') if request.form.get('company_sub_district') != '' else None
        company_postal_code = request.form.get('company_postal_code') if request.form.get('company_postal_code') != '' else None
        identity_com = request.form.get('identity_com')
        # car1
        license_plate1 = request.form.get('license_plate1')
        province_car1 = request.form.get('province_car1')
        brand_name1 = request.form.get('brand_name1')
        color1 = request.form.get('color1')
        # car2
        license_plate2 = request.form.get('license_plate2')
        province_car2 = request.form.get('province_car2')
        brand_name2 = request.form.get('brand_name2')
        color2 = request.form.get('color2')
        # card
        card_id = request.form.get('card_id')
        vcard_type = request.form.get('vcard_type')
        months = request.form.get('inputmonths')
        service_start_date = request.form.get('inputdate')
        deposit_amount = float(request.form.get('deposit')) if request.form.get('deposit').isnumeric() else 0.0
        price = request.form.get('price')
        total = request.form.get('total')
        if service_type != 'ยกเลิก':
            price = round(((float(total) - float(deposit_amount)) * (100/107)),2) 
            vat = round(((float(total) - float(deposit_amount)) - price),2)
        verify_status = request.form.get('status-select2')
        address_type = request.form.get('address_type')
        # แจ้งเตือน******************
        notification = request.form.get('notification')
        payment_name = request.form.get('payment_name3')
        payment_status = request.form.get('payment_status')
        payment_date = request.form.get('payment_date')
        if payment_date == '':
            payment_date = None
        card_last_read_date = request.form.get('card_last_read_date')
        return_card = request.form.get('return_card_2')
        comment = request.form.get('comment')
        if verify_status == '1':
            approve_date = datetime.datetime.today()
            lastdate_pay = approve_date + datetime.timedelta(7)
        else:
            approve_date = None
            lastdate_pay = None
        # file
        print('file')
        copy_id_card = request.files['copy_id_card']
        copy_doc_car1 = request.files['copy_doc_car1']
        print(copy_id_card)
        copy_id_card = custom_file(
            file=copy_id_card, card_id=identity_card, filename='id_card')
        copy_doc_car1 = custom_file(
            file=copy_doc_car1, card_id=identity_card, filename='car1')
        # check user
        id_ = Parking_log.query.filter(Parking_log.Id >= 0).order_by(Parking_log.Id.desc()).first().Id+1
        check_user = Parking_member.query.filter_by(
            identity_card=identity_card).first()
        if check_user:
            check_user = 1
        elif not check_user:
            check_user = 0
        if service_type == 'สมัครใหม่':
            if payment_status == '1':
                
                card_expire_date = datetime.datetime.strptime(service_start_date,'%Y-%m-%d') + datetime.timedelta(genday(int(months),service_start_date))
                capacity_count(parking_code,None)
                last_invoice = station.start_inv_no
                invoice = last_invoice.split('/')[0]+ '/' + station.parking_branch+'/' +str(int(last_invoice.split('/')[-1])+1).zfill(3)
                station.start_inv_no = invoice
                same_branch = Parking_manage.query.filter_by(parking_branch = station.parking_branch).all()
                if same_branch != []:
                        for branchs in same_branch:
                            branchs.start_inv_no = invoice
                if deposit_amount != 0:
                    invoice2 = invoice.split('/')[0]+ '/' + station.parking_branch+'/' +str(int(invoice.split('/')[-1])+1).zfill(3)
                    station.start_inv_no = invoice2
                    same_branch2 = Parking_manage.query.filter_by(parking_branch = station.parking_branch).all()
                    if same_branch2 != []:
                        for branchs in same_branch2:
                            branchs.start_inv_no = invoice2
                else:
                    invoice2 = None
                    

            else:
                card_expire_date = None
                invoice = None
                invoice2 = None

            if deposit_amount == 0:
                deposit_address_type = None
            else:
                deposit_address_type = request.form.get('address_type_deposit')
            
            if payment_name == '5':
                cheque_no = request.form.get('cheque_no')
                cheque_date = request.form.get('cheque_date')
                bank_name = request.form.get('bank_name')
                bank_branch = request.form.get('bank_branch')
            else:
                cheque_no = None
                cheque_date = None
                bank_name = None
                bank_branch = None
                                

            new_member = Parking_member(
                card_id=card_id,
                identity_card=identity_card,
                first_name_th=first_name,
                last_name_th=last_name,
                phone=phone,
                parking_code=parking_code,
                parking_register_date=datetime.datetime.today(),
                vcard_type=vcard_type,


                # car registration 1

                license_plate1=license_plate1,
                province_car1=province_car1,
                brand_name1=brand_name1,
                color1=color1,

                # car registration 2

                license_plate2=license_plate2,
                province_car2=province_car2,
                brand_name2=brand_name2,
                color2=color2,

                # tax invoice home

                address_no=address_no,
                province=province ,
                district=district,
                sub_district=sub_district,
                postal_code=postal_code,
                village=village,
                alley=alley,
                street=street,

                # tax invoice company
                identity_com=identity_com,
                company_name=company_name,
                company_no=company_no,
                company_village=company_village,
                company_alley=company_alley,
                company_street=company_street,
                company_sub_district=company_sub_district,
                company_district=company_district,
                company_province=company_province ,
                company_postal_code=company_postal_code,
                card_expire_date=card_expire_date,

                # file
                copy_id_card=copy_id_card,
                copy_doc_car1=copy_doc_car1,
                card_last_read_date=card_last_read_date,
                user_create = session.get('username'),
                user_create_date = datetime.datetime.today()
            )
            new_log = Parking_log(
                Id=id_,
                card_id=card_id,
                input_type=2,
                transaction_type=1,
                identity_card=identity_card,
                last_name=last_name,
                first_name=first_name,
                phone=phone,
                parking_code=parking_code,
                parking_name=parking_name,
                parking_type_name=vcard_type,
                amount=price,
                vat=vat,
                orderNumber=genRef2(a=check_user, id_=id_,
                                    station=parking_code),
                parking_register_date=datetime.datetime.today(),
                month=int(months),
                service_start_date=service_start_date,
                deposit_amount=deposit_amount,
                total=total,
                verify_status=verify_status,
                payment_name=payment_name,
                payment_status=payment_status,
                payment_date=datetime.datetime.strptime(payment_date, '%Y-%m-%dT%H:%M'),
                approve_date=approve_date,
                lastdate_pay=lastdate_pay,
                address_type=address_type,
                comments=comment,invoice_no=invoice,
                invoice_deposit=invoice2,
                deposit_address_type=deposit_address_type,
                cheque_no=cheque_no,cheque_date=cheque_date,
                bank_name=bank_name,bank_branch=bank_branch
                
            )
            db.session.add(new_member)
            db.session.add(new_log)
            data = {
                        "parking_code": parking_code,    
                        "first_name": first_name,
                        "last_name": last_name,
                        "card_id": card_id,
                        "license_plate1": license_plate1,
                        "license_plate2": license_plate2,
                        "card_expire_date": card_expire_date,
                        "service_start_date": service_start_date,
                    }
            api = ApiMember(data)
            api.from_orm(new_member)
            res = api.request_insert()[0]
            print('response Api: ',res)
            # send_data_to_publish_service_with_ordernumber(new_log.orderNumber)
            if res.get('status') == False:
                return jsonify(res)
            db.session.commit()        
            # api_member(' /v1/member/register', api_json)
        elif service_type == 'ต่ออายุ':
            
            if payment_status == '1':
                
                card_expire_date = datetime.datetime.strptime(service_start_date,'%Y-%m-%d') + datetime.timedelta(genday(int(months),service_start_date))
                capacity_count(parking_code,None)
                last_invoice = station.start_inv_no
                invoice = last_invoice.split('/')[0]+ '/' + station.parking_branch+'/' +str(int(last_invoice.split('/')[-1])+1).zfill(3)
                station.start_inv_no = invoice
                same_branch = Parking_manage.query.filter_by(parking_branch = station.parking_branch).all()
                if same_branch != []:
                        for branchs in same_branch:
                            branchs.start_inv_no = invoice
                if deposit_amount != 0:
                    invoice2 = invoice.split('/')[0]+ '/' + station.parking_branch+'/' +str(int(invoice.split('/')[-1])+1).zfill(3)
                    station.start_inv_no = invoice2
                    same_branch2 = Parking_manage.query.filter_by(parking_branch = station.parking_branch).all()
                    if same_branch2 != []:
                        for branchs in same_branch2:
                            branchs.start_inv_no = invoice2
                else:
                    invoice2 = None

            else:
                card_expire_date = None
                invoice = None
                invoice2 = None  

            if payment_name == '5':
                cheque_no = request.form.get('cheque_no')
                cheque_date = request.form.get('cheque_date')
                bank_name = request.form.get('bank_name')
                bank_branch = request.form.get('bank_branch')
            else:
                cheque_no = None
                cheque_date = None
                bank_name = None
                bank_branch = None

                       
            
            update_member = Parking_member.query.filter_by(card_id=card_id).filter(
                Parking_member.parking_code == parking_code)\
                    .filter(Parking_member.identity_card==identity_card).first()

            data = {
                        "parking_code": parking_code,     
                        "first_name": first_name,
                        "last_name": last_name,
                        "card_id": card_id,
                        "license_plate1": license_plate1,
                        "license_plate2": license_plate2,
                        "card_expire_date": card_expire_date,
                        "service_start_date": service_start_date,
                    }
            api = ApiMember(data)
            api.from_orm(update_member)
            res = api.request_update()[0]
            print('response Api: ',res)
            if res.get('status') == False:
                return res

            new_log = Parking_log(verify_status=verify_status,
                    card_id=card_id,
                    input_type = 2,transaction_type = 2,
                    identity_card = identity_card,
                    last_name = last_name,
                    first_name = first_name,
                    phone = phone,
                    parking_code = parking_code,
                    parking_name = parking_name,
                    parking_type_name = vcard_type,
                    amount = price,#orderNumber = genRef2(a=1, id_=Parking_log.query.order_by(Parking_log.Id.desc()).first().Id +1,station=parking_code)
                    vat=vat,
                    parking_register_date = update_member.parking_register_date,
                    approve_date = approve_date,lastdate_pay = lastdate_pay,payment_name=payment_name,
                    payment_status = payment_status,service_start_date = service_start_date,
                    total = total,deposit_amount=deposit_amount,
                    month = int(months),address_type=address_type,payment_date=datetime.datetime.strptime(payment_date, '%Y-%m-%dT%H:%M'),comments=comment,
                    invoice_no=invoice,invoice_deposit=invoice2,cheque_no=cheque_no,cheque_date=cheque_date,
                    bank_name=bank_name,bank_branch=bank_branch
                )
            
            for key,value in request.form.to_dict().items():
                if key in Parking_member.__table__.columns.keys():
                    if key == 'card_status':
                        continue
                    elif getattr(update_member,key) != value:
                        setattr(update_member,key,value if value != '' else None)

            update_member.user_edit = session.get('username')
            update_member.user_edit_date = datetime.datetime.today()
            update_member.card_status = '1'
            if card_expire_date != None:
                update_member.card_expire_date = card_expire_date
            db.session.add(new_log)
            db.session.flush()
            new_log.orderNumber = genRef2(a=1, id_=new_log.Id,station=parking_code)
            db.session.commit()
            # send_data_to_publish_service_with_ordernumber(new_log.orderNumber)
            
        #RENEWAL_API
        #    renewal_api = {
        #        "username":"jparkapi",
        #        "password":"123456",
        #        "stationCode":parking_code,
        #        "memberCode":format_memberCode(identity_card),
        #        "memberCardName":card_id,
        #        "memberCardExpire":card_expire_date,
        #        "actionBy":"UJK001",
        #        "actionTimestamp":datetime.datetime.now()
        #    }
        #    return response_api()    
            
        elif service_type == 'ยกเลิก':
            
            update_member = Parking_member.query.filter_by(card_id=card_id).filter(
                Parking_member.parking_code == parking_code)\
                .filter(Parking_member.identity_card==identity_card).first()

            if parking_code in ['N1013','N1014']:
                status = send_card_return_data_to_cit(
                            stationCode=parking_code,
                            token_id=update_member.token_id,
                            memberCardName=card_id,
                            )
                if status != True:
                    response = {'status':False,'message':status}
                    return response
            
            new_log = Parking_log(
                Id=id_,
                cus_id=Parking_log.query.filter(Parking_log.card_id==card_id).order_by(Parking_log.Id.desc()).first().cus_id,
                card_id=card_id,
                input_type=2,
                transaction_type=3,
                identity_card=identity_card,
                last_name=last_name,
                first_name=first_name,
                phone=phone,
                parking_code=parking_code,
                parking_name=parking_name,
                parking_type_name=vcard_type,
                parking_register_date=update_member.parking_register_date,
                verify_status=verify_status,
                payment_name=payment_name,
                payment_status=payment_status,
                payment_date=payment_date,comments=comment,
                orderNumber=id_
            )
            
            update_member.card_status = '0'
            update_member.card_last_read_date = card_last_read_date
            if request.form.get('deposit_return') != '':
                update_member.deposit_return = request.form.get('deposit_return')
                update_member.deposit_status = '1'
            update_member.return_card = return_card
            db.session.add(new_log)
            db.session.commit()
            # send_data_to_publish_service_with_ordernumber(new_log.orderNumber)

        elif service_type == 'บัตรหาย':
            
            old_id = request.form.get('search')
            old_log = Parking_log.query.filter_by(card_id=old_id).filter(Parking_log.parking_code==parking_code)\
                .order_by(Parking_log.Id.desc()).first()
            old_member = Parking_member.query.filter_by(card_id=old_id).filter(Parking_member.parking_code==parking_code)\
                .filter(or_(Parking_member.card_status=='1',Parking_member.card_status==None))\
                    .first()
            
            if parking_code in ['N1013','N1014']:
                status = send_card_lost_data_to_cit(
                            stationCode=parking_code,
                            token_id=old_member.token_id,
                            memberCardNamNew=card_id,
                            memberCardNamOld=old_member.card_id
                            )
                if status != True:
                    response = {'status':False,'message':status}
                    return response
            
            if payment_name == '5':
                cheque_no = request.form.get('cheque_no')
                cheque_date = request.form.get('cheque_date')
                bank_name = request.form.get('bank_name')
                bank_branch = request.form.get('bank_branch')
            else:
                cheque_no = None
                cheque_date = None
                bank_name = None
                bank_branch = None
            if deposit_amount != 0:
                invoice = station.start_inv_no
                invoice2 = invoice.split('/')[0]+ '/' + station.parking_branch+'/' +str(int(invoice.split('/')[-1])+1).zfill(3)
                station.start_inv_no = invoice2
                same_branch2 = Parking_manage.query.filter_by(parking_branch = station.parking_branch).all()
                if same_branch2 != []:
                    for branchs in same_branch2:
                        branchs.start_inv_no = invoice2
                deposit_address_type = request.form.get('address_type_deposit')
            else:
                invoice2 = None
                deposit_address_type = None
            
            new_member = Parking_member(
                
                card_id=card_id,
                identity_card=identity_card,
                first_name_th=first_name,
                last_name_th=last_name,
                phone=phone,
                parking_code=parking_code,
                parking_register_date=datetime.datetime.today(),
                vcard_type=vcard_type,


                # car registration 1

                license_plate1=license_plate1,
                province_car1=province_car1,
                brand_name1=brand_name1,
                color1=color1,

                # car registration 2

                license_plate2=license_plate2,
                province_car2=province_car2,
                brand_name2=brand_name2,
                color2=color2,

                # tax invoice home

                address_no=address_no,
                province=province ,
                district=district,
                sub_district=sub_district,
                postal_code=postal_code,
                village=village,
                alley=alley,
                street=street,

                # tax invoice company
                identity_com=identity_com,
                company_name=company_name,
                company_no=company_no,
                company_village=company_village,
                company_alley=company_alley,
                company_street=company_street,
                company_sub_district=company_sub_district,
                company_district=company_district,
                company_province=company_province ,
                company_postal_code=company_postal_code,
                card_expire_date=old_member.card_expire_date,

                # file
                copy_id_card=copy_id_card,
                copy_doc_car1=copy_doc_car1,
                card_last_read_date=card_last_read_date,
                user_create = session.get('username'),
                user_create_date = datetime.datetime.today()
            )
            new_log = Parking_log(
                Id=id_,
                card_id=card_id,
                input_type=2,
                transaction_type=1,
                identity_card=identity_card,
                last_name=last_name,
                first_name=first_name,
                phone=phone,
                parking_code=parking_code,
                parking_name=parking_name,
                parking_type_name=vcard_type,
                amount=0,
                vat=0,
                orderNumber=genRef2(a=check_user, id_=id_,
                                    station=parking_code),
                parking_register_date=datetime.datetime.today(),
                month=old_log.month,
                service_start_date=old_log.service_start_date,
                deposit_amount=deposit_amount,
                total=total,
                verify_status=verify_status,
                payment_name=payment_name,
                payment_status=payment_status,
                payment_date=datetime.datetime.strptime(payment_date, '%Y-%m-%dT%H:%M'),
                approve_date=approve_date,
                lastdate_pay=lastdate_pay,
                address_type=address_type,
                comments=comment,invoice_no=old_log.invoice_no,
                invoice_deposit=invoice2,
                deposit_address_type=deposit_address_type,
                cheque_no=cheque_no,cheque_date=cheque_date,
                bank_name=bank_name,bank_branch=bank_branch
                
            )
            db.session.add(new_member)
            db.session.add(new_log)
            db.session.commit()
            # send_data_to_publish_service_with_ordernumber(old_log.orderNumber)
            # send_data_to_publish_service_with_ordernumber(new_log.orderNumber)
            
        return jsonify({'status':True, 'message':'บันทึกเรียบร้อย'})



@app.route("/manage/insert", methods=['POST'])
def insert():
    if request.method == "POST":
        cus_id = request.form['cus_id']
        card_id = request.form['card_id']
        parking_register_date = request.form['parking_register_date']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        phone = request.form['phone']
        parking_name = request.form['parking_name']
        parking_type_name = request.form['parking_type_name']
        month = request.form['month']
        amount = request.form['amount']
        vat = request.form['vat']
        total = request.form['total']
        # !-------------------------------------------
        copy_id_card = request.form['copy_id_card']
        copy_doc_car1 = request.form['copy_doc_car1']
        # !-------------------------------------------
        verify_status = request.form['verify_status']
        alert = request.form['alert']
        payment_name = request.form['payment_name']
        payment_status = request.form['payment_status']
        payment_date = request.form['payment_date']
        payment_expected_date = request.form['payment_expected_date']

        with mysql.connection.cursor() as cursor:
            sql = """Insert into `parking_log` (`cus_id`,`card_id`,`parking_register_date`,`first_name`,
            `last_name`,`phone`,`parking_name`,`parking_type_name`,`month`,`amount`,`vat`,`total`,
            `verify_statu`,`alert`,`payment_name`,`payment_status`,`payment_date`,`payment_expected_date`) 
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cursor.execute(sql, (cus_id, card_id, parking_register_date, first_name, last_name, phone, parking_name, parking_type_name, month, amount, vat, total, verify_status, alert, payment_name,
                                 payment_status, payment_date, payment_expected_date))
            cursor.execute()
            mysql.commit()
        return redirect(url_for('dashboard.html'))



@app.route("/manage/insert_user_manage", methods=['POST'])
def insert_user_manage():
    if request.method == "POST":

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        codes = request.form.getlist('parking_code')
        parking_code = ''
        for code in codes:
            if len(codes) == codes.index(code) + 1:
                parking_code += code 
            else :
                parking_code += code + ',' 
        password = request.form['password']
        dep_name = request.form['dep_name']
        role_name = request.form['role_name']
        line_token = request.form['line_token']

        user_create_date = request.form['user_create_date']
        # user_create = request.form['user_create']
        # user_edit = request.form['user_edit']

        with mysql.connection.cursor() as cursor:
            sql = """Insert into `user_manage` (`first_name`,`last_name`,`username`,
            `password`,`dep_id`,`role_id`,`parking_code`,`line_token`,
            `user_create_date`)
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cursor.execute(sql, (first_name, last_name, username,
                                 password, dep_name, role_name,parking_code, line_token,
                                 user_create_date))
            mysql.connection.commit()
        return redirect(url_for('user_manage'))


@app.route("/manage/insert_user_profile", methods=['POST'])
def insert_user_profile():
    if request.method == "POST":

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']

        password = request.form['password']
        line_token = request.form['line_token']

        with mysql.connection.cursor() as cursor:
            sql = """Insert into `user_manage` (`first_name`,`last_name`,`username`,
            `password`,`line_token`)
            values(%s,%s,%s,%s,%s)"""
            cursor.execute(sql, (first_name, last_name,
                                 username, password, line_token))
            mysql.connection.commit()
        return redirect('user-profile')
###########################################################ittipon###############################################################

@app.route('/manage/customer_manage')
def customer_manage():
    return render_template('manage/customer-manage.html')

@app.route('/manage/datacustomer')
def datacustomer():
    rows = Parking_member.query.all()
    data = []
    for row in rows:  
        user = {}
        user['Id'] = row.Id
        user['first_name_th'] = row.first_name_th
        user['last_name_th'] = row.last_name_th
        user['phone'] = row.phone
        
        user['address_no'] = f'{str(row.address_no or "")} {str(row.unit_home or "")} {str("หมู่." + row.village if row.village else "")} '
        user['address_no'] += f'{str("ซ." + row.alley if row.alley else "")} {str("ถ." + row.street if row.street else "")} {str("ต." + row.sub_district if row.sub_district else "")} '
        user['address_no'] += f'{str("อ." + row.district if row.district else "")} {str("จ." + row.province if row.province else "")} {str(row.postal_code or "")}'
        
        user['address_com'] = f'{str(row.company_no or "")} {str(row.company_unit or "")} {str("หมู่." + row.company_village if row.company_village else "")} '
        user['address_com'] += f'{str("ซ." + row.company_alley if row.company_alley else "")} {str("ถ." + row.company_street if row.company_street else "")} '
        user['address_com'] += f'{str("ต." + row.company_sub_district if row.company_sub_district else "")} {str("อ." + row.company_district if row.company_district else "")} '
        user['address_com'] += f'{str("จ." + row.company_province if row.company_province else "")} {str(row.company_postal_code or "")}'
        
        user['identity_card'] = row.identity_card
        user['identity_com'] = row.identity_com
        user['parking_code'] = Parking_manage.query.filter_by(parking_code=row.parking_code).first().parking_name
        user['card_id'] = row.card_id
        user['parking_register_date'] = row.parking_register_date
        user['card_last_read_date'] = row.card_last_read_date
        user['card_expire_date'] = row.card_expire_date
        user['user_edit_date'] = row.user_edit_date
        user['button'] = f'<button class="btn btn-warning-del" data-toggle="modal" data-whatever="{row.Id}"'
        user['button'] +='data-target="#Modaledit"><i class="fas fa-edit"></i>แก้ไข</button>'
        if user['parking_register_date'] != None:
            user['parking_register_date'] = row.parking_register_date.strftime('%d/%m/%Y')
        if user['card_last_read_date'] != None:
            user['card_last_read_date'] = row.card_last_read_date.strftime('%d/%m/%Y')
        if user['card_expire_date'] !=None:
            user['card_expire_date'] = row.card_expire_date.strftime('%d/%m/%Y')
        if user['user_edit_date'] != None:
            user['user_edit_date'] = row.user_edit_date.strftime('%d/%m/%Y')
        
        data.append(user)
    return jsonify(data)

@app.route('/manage/modal_customer',methods=['POST'])
def modal_customer():
    user_id = request.form['id']
    row = Parking_member.query.filter_by(Id=user_id).first()
    data = Parking_member.to_json([row])
    if data[0]['user_edit_date']:
        data[0]['user_edit_date'] = data[0]['user_edit_date'].strftime('%d/%m/%Y')
    if data[0]['card_expire_date']:
        data[0]['card_expire_date'] = data[0]['card_expire_date'].strftime('%Y-%m-%d')
    return jsonify(data)

##############################################ittipon##################################
@app.route('/manage/parking-manage')
def parking_manage():
    rows = Parking_manage.query.all()
    data = []
    for row in rows:
        d = {}
        for col in row.__table__.columns.keys():
            d[col] = getattr(row,col)
        d['button'] = f'<button class="btn btn-warning-del" id="udmd" data-toggle="modal"'
        d['button'] += f'data-target="#Modaledit" onclick="showdataupdate({row.Id})">'
        d['button'] += '<i class="fas fa-edit"></i> แก้ไข</button>'
        if d['user_edit_date'] != None:
            d['user_edit_date'] = d['user_edit_date'].strftime('%d/%m/%Y')
        if d['user_create_date'] != None:
            d['user_create_date'] = d['user_create_date'].strftime('%d/%m/%Y')
        data.append(d)
    return render_template('manage/parking-manage.html', data=data)

##########################################################ittipon###########################
@app.route('/manage/modal_parking',methods=['POST'])
def modal_parking():
    id_ = request.form.get('id')
    row = Parking_manage.query.filter_by(Id=id_).first()
    data = []
    d = {}
    for i in row.__table__.columns.keys():
        d[i] = getattr(row,i)
    data.append(d)
    if data[0]['over_night'] != None:
        data[0]['over_night'] = int(data[0]['over_night'])
    if data[0]['deposit_amount'] != None:
        data[0]['deposit_amount'] = int(data[0]['deposit_amount'])
    if data[0]['parking_price'] != None:
        data[0]['parking_price'] = int(data[0]['parking_price'])
    if data[0]['parking_discount'] != None:
        data[0]['parking_discount'] = int(data[0]['parking_discount'])
    if data[0]['user_create_date'] != None:
        data[0]['user_create_date'] = data[0]['user_create_date'].strftime('%d/%m/%Y')
    if data[0]['user_edit_date'] != None:
        data[0]['user_edit_date'] = data[0]['user_edit_date'].strftime('%d/%m/%Y')
    return jsonify(data)

###############################################ittipon#############################################
@app.route("/manage/update_parking_manage", methods=['POST'])
def update_parking_manage():
    if request.method == "POST":
        id_ = request.form.get('id')
        parking_name = request.form.get('parking_name')
        parking_price = request.form.get('parking_price')
        parking_discount = request.form.get('parking_discount')
        line_name = request.form.get('line_name')
        parking_type_name = request.form.get('vcard_type')
        policy_des = request.form.get('policy_des')
        parking_status = request.form.get('parking_status')
        line_token = request.form.get('line_token')
        user_edit_date = datetime.datetime.today()
        parking_code = request.form.get('parking_code')
        parking_image = request.files['file']
        if parking_price == '':
            parking_price = None
        if parking_discount == '':
            parking_discount = None
            
        parking_image_path = r'C:\D\project_mrta_parkingApp\mrta-app\static\image\manage\station/'+parking_image.filename
        if parking_image.filename !='':
            parking_image.save(parking_image_path)
            Parking_manage.query.filter_by(Id=id_).update({
                Parking_manage.parking_name:parking_name,Parking_manage.parking_price:parking_price,
                Parking_manage.parking_discount:parking_discount,Parking_manage.line_name:line_name,
                Parking_manage.parking_type_name:parking_type_name,Parking_manage.policy_des:policy_des,
                Parking_manage.parking_status:parking_status,Parking_manage.line_token:line_token
                ,Parking_manage.user_edit_date:user_edit_date,Parking_member.vcard_type:parking_type_name,
                Parking_manage.parking_image:parking_image.filename,Parking_manage.parking_code:parking_code
            })
            db.session.commit()
        elif parking_image.filename == '':
            Parking_manage.query.filter_by(Id=id_).update({
                Parking_manage.parking_name:parking_name,Parking_manage.parking_price:parking_price,
                Parking_manage.parking_discount:parking_discount,Parking_manage.line_name:line_name,
                Parking_manage.parking_type_name:parking_type_name,Parking_manage.policy_des:policy_des,
                Parking_manage.parking_status:parking_status,Parking_manage.line_token:line_token,
                Parking_manage.user_edit_date:user_edit_date,Parking_member.vcard_type:parking_type_name,
                Parking_manage.parking_code:parking_code
            })
        Carpacity_manage.query.filter_by(parking_code=Parking_manage.query.filter_by(Id=id_).first().parking_code).update({
            Carpacity_manage.parking_code:parking_code,Carpacity_manage.parking_name:parking_name,
            Carpacity_manage.user_edit_date:user_edit_date
        })
        db.session.commit()        
        return redirect(url_for('parking_manage'))

##############################################################ittipon################################################
@app.route("/manage/insert-parking-manage2", methods=['POST'])
def insert_parking_manage2():
    if request.method == "POST":
        parking_image=request.files['parking_image']
        parking_name = request.form['parking_name']
        parking_name_en = request.form['parking_name_en']
        parking_price = request.form['parking_price']
        parking_discount = request.form['parking_discount']
        line_name = request.form['line_name']
        parking_type_name = request.form['parking_type_name']
        policy_des = request.form['policy_des']
        parking_status = request.form['parking_status']
        # line_token = request.form['line_token']
        user_create_date = request.form['user_create_date']
        user_edit_date = datetime.datetime.today()
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        deposit = request.form.get('deposit')
        over_night = request.form.get('over_night')
        parking_code = request.form.get('parking_code')
        parking_image_path = r'C:\D\project_mrta_parkingApp\mrta-app\static\image\manage\station/'+parking_image.filename
        parking_image.save(parking_image_path)
        new_station = Parking_manage(
            parking_image=parking_image.filename,parking_name=parking_name,
            parking_price=parking_price,parking_discount=parking_discount,
            line_name=line_name,parking_type_name=parking_type_name,
            policy_des=policy_des,parking_status=parking_status,
            user_create_date=user_create_date,user_edit_date=user_edit_date,
            latitude=latitude,longitude=longitude,parking_name_eng=parking_name_en,
            deposit_amount=deposit,over_night=over_night,parking_code=parking_code,vcard_type=parking_type_name
        )    
        new_capacity = Carpacity_manage(
            parking_name=parking_name,parking_code=parking_code,
            user_create_date=user_create_date,member_limit=0) 
        db.session.add(new_capacity) 
        db.session.add(new_station)
        db.session.commit()
        
        return redirect(url_for('parking_manage'))

# @app.route('')
@app.route('/manage/permission')
def permission():
    data_all = User_manage.query.all()

    datas = []

    for data in data_all:
        user = {}
        user["id"] = data.Id
        user["first_name"] = data.first_name
        user["last_name"] = data.last_name
        user["username"] = data.username
        user["role_id"] = data.role_id
        user["parking_code"] = data.parking_code
        user["user_create_date"] = data.user_create_date
        user["user_edit_date"] = data.user_edit_date

        datas.append(user)

    return render_template('manage/permission.html', datas=datas)


@app.route('/manage/permission')
def insert_permission():

    return


@app.route('/monthly-carpark')
def monthly_carpark():
    return render_template('/monthly-carpark.html')

@app.route('/manage/news-manage')
def news_manage():
    rows = News_manage.query.all()
    data = []
    for row in rows:
        d = {}
        for col in row.__table__.columns.keys():
            d[col] = getattr(row,col)
        d['button'] = f'<button class="btn btn-warning-del" id="udmd" data-toggle="modal"'
        d['button'] += f'data-target="#Modaledit" onclick="showdataupdate({row.Id})">'
        d['button'] += '<i class="fas fa-edit"></i> แก้ไข</button>'
        if d['user_edit_date'] != None:
            d['user_edit_date'] = d['user_edit_date'].strftime('%d/%m/%Y')
        if d['user_create_date'] != None:
            d['user_create_date'] = d['user_create_date'].strftime('%d/%m/%Y')
        data.append(d)
    return render_template('manage/news-manage.html', data=data)

##############################################ittipon#################################################
@app.route('/manage/modal_news',methods=['POST'])
def modal_news():
    id_ = request.form.get('id')
    row = News_manage.query.filter_by(Id = id_).first()
    data = []
    d = {}
    for i in row.__table__.columns.keys():
        d[i] = getattr(row,i)
    data.append(d)
    data[0]['user_create_date'] = data[0]['user_create_date'].strftime('%d/%m/%Y')
    if data[0]['user_edit_date'] != None:
        data[0]['user_edit_date'] = data[0]['user_edit_date'].strftime('%d/%m/%Y')
    if data[0]['news_date'] != None:
        data[0]['news_date'] = data[0]['news_date'].strftime('%Y-%m-%d')
    if data[0]['end_date'] != None:
        data[0]['end_date'] = data[0]['end_date'].strftime('%Y-%m-%d')
    return jsonify(data)

#########################################################ittipon##################################
@app.route("/manage/update_news", methods=['POST'])
def update_news():
    if request.method == "POST":
        id_ = request.form['id']
        news_image = request.files['news_image']
        news_image_path = r"C:\D\project_mrta_parkingApp\mrta-app\static\image\allnews\news/"+ news_image.filename

        news_name = request.form['news_name']
        news_des = request.form['news_des']
        news_type=request.form['news_type']
        news_status = request.form['news_status']
        news_name_eng = request.form['news_name_eng']
        news_des_eng = request.form['news_des_eng']
        news_date = request.form['news_date']
        end_date = request.form['end_date']
        
        if news_image.filename != '':
            news_image.save(news_image_path)
            News_manage.query.filter_by(Id = id_).update({
                News_manage.news_image:news_image.filename,News_manage.news_name:news_name,News_manage.news_des:news_des,
                News_manage.news_status:news_status,News_manage.news_type:news_type,
                News_manage.user_edit_date:datetime.datetime.today(),News_manage.news_des_eng:news_des_eng,
                News_manage.news_name_eng:news_name_eng,News_manage.news_date:news_date,
                News_manage.end_date:end_date
            })
            db.session.commit()
        elif news_image.filename == '':
            News_manage.query.filter_by(Id = id_).update({
                News_manage.news_name:news_name,News_manage.news_des:news_des,News_manage.news_type:news_type,
                News_manage.news_status:news_status,
                News_manage.user_edit_date:datetime.datetime.today(),News_manage.news_des_eng:news_des_eng,
                News_manage.news_name_eng:news_name_eng,News_manage.news_date:news_date,
                News_manage.end_date:end_date
            })
            db.session.commit()

        return redirect('news-manage')

@app.route("/manage/insert_new_manage", methods=['POST'])
def insert_new_manage():
    if request.method == "POST":

        news_image = request.files['news_image']
        news_image_path = r"C:\D\project_mrta_parkingApp\mrta-app\static\image\allnews\news/"+ news_image.filename
        news_image.save(news_image_path)

        news_name = request.form['news_name']
        news_des = request.form['news_des']
        news_name_eng = request.form['news_name_eng']
        news_des_eng = request.form['news_des_eng']
        news_type = request.form['news_type']
        news_status = request.form['news_status']
        user_create_date = request.form['user_create_date']
        news_date = request.form['news_date']
        end_date = request.form['end_date']
        with mysql.connection.cursor() as cursor:
            sql = """Insert into `news_manage` (`news_image`,`news_name`,`news_des`,`news_type`,`news_status`,`user_create_date`,`news_date`,`news_name_eng`,`news_des_eng`,`end_date`) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cursor.execute(sql, (news_image.filename, news_name, news_des,
                                 news_type, news_status, user_create_date,news_date,news_name_eng,news_des_eng,end_date))
            mysql.connection.commit()

        return redirect(url_for('news_manage'))

@app.route("/manage/update_user_manage", methods=['POST'])
def update_user_manage():
    if request.method == "POST":
        id = request.form['id']

        parking_name = request.form['parking_name']
        parking_price = request.form['parking_price']
        parking_discount = request.form['parking_discount']
        line_name = request.form['line_name']
        parking_type_name = request.form['parking_type_name']
        policy_des = request.form['policy_des']
        parking_status = request.form['parking_status']
        line_token = request.form['line_token']

        user_create_date = request.form['user_create_date']
        # user_create = request.form['user_create']
        # user_edit = request.form['user_edit']

        with mysql.connection.cursor() as cursor:
            sql = """ UPDATE parking_manage SET parking_name=%s, parking_price=%s, parking_discount=%s, line_name=%s,
            parking_type_name=%s, policy_des=%s, parking_status=%s, line_token=%s,
            user_create_date=%s, user_edit_date=NOW() WHERE id=%s """
            cursor.execute(sql, (parking_name, parking_price, parking_discount, line_name, parking_type_name,
                                 policy_des, parking_status, line_token,
                                 user_create_date, id))
            mysql.connection.commit()
        return redirect('parking-manage')



@app.route("/manage/update_customer_manage", methods=['POST'])
def update_customer_manage():
    if request.method == "POST":
        id = request.form['id']
        customer_update = Parking_member.query.filter_by(Id=id).first()
        log_update = Parking_log.query.filter_by(card_id=customer_update.card_id).filter(Parking_log.parking_code==customer_update.parking_code)\
            .order_by(Parking_log.Id.desc()).first()
        for key,value in request.form.to_dict().items():
            if key not in ['id','user_edit_date']:
                if getattr(customer_update,key) != value:
                    if key == 'card_id':
                        setattr(log_update,key,value)
                    if key == 'card_expire_date':
                        if value != '' and customer_update.card_expire_date:
                            exp = datetime.datetime.strptime(value,'%Y-%m-%d')
                            day_plus_to_service_start = exp.date() - customer_update.card_expire_date 
                            log_update.service_start_date = log_update.service_start_date + datetime.timedelta(day_plus_to_service_start.days)
                    setattr(customer_update,key,value if value != '' else None)
        customer_update.user_edit_date = datetime.datetime.today()
        if log_update.transaction_type in ['1','2']:
            data = {
                        "parking_code": log_update.parking_code,    
                        "first_name": log_update.first_name,
                        "last_name": log_update.last_name,
                        "card_id": log_update.card_id,
                        "license_plate1": customer_update.license_plate1,
                        "license_plate2": customer_update.license_plate2,
                        "card_expire_date": customer_update.card_expire_date,
                        "service_start_date": log_update.service_start_date,
                    }
            api = ApiMember(data)
            api.from_orm(customer_update)
            if log_update.payment_status == '1':
                card_id = request.form['card_id']
                true_card_id = checkCardNotRandom(card_id)
                if true_card_id and customer_update.api_member_status != '1':
                    res = api.request_insert()[0]
                    print('response Api',res)
                    if res.get('status') == False:
                        return res
                else:
                    res = api.request_update()[0]
                    print('response Api',res)
                    if res.get('status') == False:
                        return res
            elif log_update.transaction_type == '2':
                res = api.request_update()[0]
                print('response Api',res)
                if res.get('status') == False:
                    return res
        db.session.commit()
        return jsonify({'status':True, 'message':'บันทึกเรียบร้อย'})


#################################################ittipon###########################
@app.route('/manage/activity-manage')
def activity_manage():
    rows = Activity_manage.query.all()
    data = []
    for row in rows:
        d = {}
        for col in row.__table__.columns.keys():
            d[col] = getattr(row,col)
        d['button'] = f'<button class="btn btn-warning-del" id="udmd" data-toggle="modal"'
        d['button'] += f'data-target="#Modaledit" onclick="showdataupdate({row.Id})">'
        d['button'] += '<i class="fas fa-edit"></i> แก้ไข</button>'
        d['user_edit_date'] = d['user_edit_date'].strftime('%d/%m/%Y')
        d['user_create_date'] = d['user_create_date'].strftime('%d/%m/%Y')
        data.append(d)
    return render_template('manage/activity-manage.html', data=data)
#############################################itipon#################################
@app.route('/manage/modal_activity',methods=['POST'])
def modal_activity():
    id_ = request.form.get('id')
    row = Activity_manage.query.filter_by(Id = id_).first()
    data = []
    d = {}
    for i in row.__table__.columns.keys():
        d[i] = getattr(row,i)
    data.append(d)
    data[0]['user_create_date'] = data[0]['user_create_date'].strftime('%d/%m/%Y')
    if data[0]['user_edit_date'] != None:
        data[0]['user_edit_date'] = data[0]['user_edit_date'].strftime('%d/%m/%Y')
    if data[0]['activity_date'] != None:
        data[0]['activity_date'] = data[0]['activity_date'].strftime('%Y-%m-%d')
    if data[0]['end_activity'] != None:
        data[0]['end_activity'] = data[0]['end_activity'].strftime('%Y-%m-%d')
    return jsonify(data)

###################################################ittipon#######################################################
@app.route("/manage/update_activity", methods=['POST'])
def update_activity():
    if request.method == "POST":
        id_ = request.form['id']
        activity_image = request.files['activity_image']
        activity_image_path = r"C:\D\project_mrta_parkingApp\mrta-app\static\image\allnews\activities/"+ activity_image.filename
        

        activity_name = request.form['activity_name']
        activity_des = request.form['activity_des']
        activity_name_eng = request.form['activity_name_eng']
        activity_des_eng = request.form['activity_des_eng']
        activity_type = request.form['activity_type']
        activity_status = request.form['activity_status']
        activity_date = request.form['activity_date']
        end_activity = request.form['end_activity']
        
        if activity_image.filename !='':
            activity_image.save(activity_image_path)
            
            Activity_manage.query.filter_by(Id=id_).update({
                Activity_manage.activity_image:activity_image.filename,Activity_manage.activity_name:activity_name,
                Activity_manage.activity_des:activity_des,Activity_manage.activity_status:activity_status,
                Activity_manage.activity_type:activity_type,Activity_manage.activity_des_eng:activity_des_eng,
                Activity_manage.user_edit_date:datetime.datetime.today(),Activity_manage.activity_name_eng:activity_name_eng,
                Activity_manage.activity_date:activity_date,Activity_manage.end_activity:end_activity
            })
            db.session.commit()
        elif activity_image.filename =='':
           
            Activity_manage.query.filter_by(Id=id_).update({
                Activity_manage.activity_name:activity_name,
                Activity_manage.activity_des:activity_des,Activity_manage.activity_status:activity_status,
                Activity_manage.activity_type:activity_type,Activity_manage.activity_des_eng:activity_des_eng,
                Activity_manage.user_edit_date:datetime.datetime.today(),Activity_manage.activity_name_eng:activity_name_eng,
                Activity_manage.activity_date:activity_date,Activity_manage.end_activity:end_activity
            })
            db.session.commit()
        return redirect('activity-manage')

@app.route("/manage/insert_activity_manage", methods=['POST'])
def insert_activity_manage():
    if request.method == "POST":
        activity_image = request.files['activity_image']
        activity_image_path = r"C:\D\project_mrta_parkingApp\mrta-app\static\image\allnews\activities/"+ activity_image.filename
        activity_image.save(activity_image_path)

        activity_type = request.form['activity_type']
        activity_name = request.form['activity_name']
        activity_des = request.form['activity_des']
        activity_name_eng = request.form['activity_name_eng']
        activity_des_eng = request.form['activity_des_eng']
        activity_status = request.form['activity_status']
        user_create_date = request.form['user_create_date']
        activity_date = request.form['activity_date']
        end_activity = request.form['end_activity']
        

        with mysql.connection.cursor() as cursor:
            sql = """Insert into `activity_manage` (`activity_image`,`activity_name`,`activity_des`, `activity_status`, `user_create_date`,`activity_type`,`activity_date`,`activity_name_eng`,`activity_des_eng`,`end_activity`)
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cursor.execute(sql, (activity_image.filename, activity_name,
                                 activity_des, activity_status, user_create_date,activity_type,activity_date,activity_name_eng,activity_des_eng,end_activity))
            mysql.connection.commit()
        return redirect(url_for('activity_manage'))


@app.route('/manage/user-manage')
def user_manage():
    rows = User_manage.query.all()
    cur1 = mysql.connection.cursor()
    cur1.execute(""" select * from capacity_manage """)
    row1 = cur1.fetchall()
    mysql.connection.commit()
    cur1.close()
    data=[]
    for row in rows:
        d = {}
        for col in row.__table__.columns.keys():
            d[col] = getattr(row,col)
        d['button'] = f'<button class="btn btn-warning-del" id="udmd" data-toggle="modal"'
        d['button'] += f'data-target="#Modaledit" onclick="showdataupdate({row.Id})">'
        d['button'] += '<i class="fas fa-edit"></i> แก้ไข</button>'
        if d['user_edit_date'] != None:
            d['user_edit_date'] = d['user_edit_date'].strftime('%d/%m/%Y')
        if d['user_create_date'] != None:
            d['user_create_date'] = d['user_create_date'].strftime('%d/%m/%Y')
        data.append(d)
    return render_template('manage/user-manage.html', datas=data, datas1=row1)

##################################################ittipon##############################################
@app.route('/manage/update-user-manage2',methods=['POST'])
def update_user_manage2():
    id_ = request.form.get('id')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    username = request.form.get('username')
    password = request.form.get('password')
    dep_id = request.form.get('dep_name')
    role_id = request.form.get('role_name')
    codes = request.form.getlist('parking_code')
    parking_code = ''
    for code in codes:
        if len(codes) == codes.index(code) + 1:
            parking_code += code 
        else :
            parking_code += code + ',' 
    line_token = request.form.get('line_token')
    user_edit_date = datetime.datetime.today()
    user = User_manage.query.filter_by(Id=id_).first()
    user.first_name = first_name
    user.last_name = last_name
    user.username = username
    user.password = password
    user.dep_id = dep_id
    user.role_id = role_id
    user.line_token = line_token
    user.user_edit_date = user_edit_date
    if parking_code != '':
        user.parking_code = parking_code
    db.session.commit()
    return redirect(url_for('user_manage'))


##########################################passachon#######################################################################
@app.route("/click_void",methods=['POST'])
def click_void():
    data = request.get_json()
    data = data.split(",")
    payRef  =   data[0]
    comment =   data[1]
   
    resp = void_fastpay(payRef)
    if resp['status'] == 'success': #void สำเร็จ นำวันหมดอายุเดิมไปupdate parking_member กรณีเป็นบัตร TAFF
     cursor = mysql.connection.cursor()
     cursor.execute('select reexpire_after_void,parking_type_name,card_id from parking_log where orderNumber = %s and payRef_ktb= %s',(resp['ref2'],payRef))
     result = cursor.fetchone()
     expire = result[0]
     typeCard = result[1]
     card_id = result[2]
     total = '-'+str(resp['amount'])
     cursor = mysql.connection.cursor()
     cursor.execute('update parking_log set void=%s,comment=%s where card_id=%s AND orderNumber=%s',(total,comment,card_id,resp['ref2']))
     mysql.connection.commit()
     if typeCard == 'TAFF':
        cursor = mysql.connection.cursor()
        if expire is not None:
         cursor.execute('update parking_member set card_expire_date=%s,card_status="0" where card_id=%s and vcard_type="TAFF" ',(expire,card_id))
        else:
         cursor.execute('update parking_member set card_expire_date = NULL,card_status="0"  where card_id=%s and vcard_type="TAFF" ',card_id)
        mysql.connection.commit()
     else:
        cursor.execute('update parking_member set card_status="0" where card_id=%s and vcard_type=%s ',card_id,typeCard)
        mysql.connection.commit()

     return 'success'
    else:
     return 'fail'

@app.route("/count_InLine", methods=['POST'])
def count_InLine():
    listcode = request.get_json()
    lenlist = 0
    if isinstance(listcode, str):
        listcode = [listcode]
        lenlist = 1
    
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    format_strings = ','.join(['%s'] * (len(listcode)))
 
    
    cursor = mysql.connection.cursor()
    cursor.execute('select SUM(total) from parking_log WHERE payment_status="1" AND DATE(payment_date)=CURDATE() AND parking_name IN ({listcode}) AND void IS NULL'.format(listcode=format_strings),listcode)
    result = cursor.fetchone()
    total_today = result[0]

    query_params = listcode
    query_params.append(month)
    query_params.append(year)
    cursor = mysql.connection.cursor()
    cursor.execute('select COUNT(id) from parking_log WHERE transaction_type="1" AND  parking_name IN ({listcode}) AND MONTH(parking_register_date)=%s AND YEAR(parking_register_date)=%s AND (verify_status="2" OR verify_status IS NULL) '.format(listcode=format_strings),query_params)
    result = cursor.fetchone()
    count_new = result[0]
    cursor = mysql.connection.cursor()
    cursor.execute('select COUNT(id) from parking_log WHERE transaction_type="2" AND parking_name IN ({listcode}) AND MONTH(approve_date)=%s AND YEAR(approve_date)=%s'.format(listcode=format_strings),query_params)
    result = cursor.fetchone()
    count_old = result[0]
    cursor = mysql.connection.cursor()
    cursor.execute('select SUM(total) from parking_log WHERE payment_status="1" AND parking_name IN ({listcode}) AND MONTH(payment_date)=%s AND YEAR(payment_date)=%s AND void IS NULL'.format(listcode=format_strings),query_params)
    result = cursor.fetchone()
    total_month = result[0]
    cursor = mysql.connection.cursor()
    cursor.execute('select q_up from parking_log WHERE q_up IS NOT NULL AND parking_name IN ({listcode}) AND MONTH(parking_register_date)=%s AND YEAR(parking_register_date)=%s ORDER BY Id DESC'.format(listcode=format_strings),query_params)
    result = cursor.fetchone()
    if result:
     count_q = result[0]
    else:
       count_q = '-'
    if total_month is None:
     total_month = 0
    if total_today is None:
     total_today= 0
    if lenlist == 0:
        count_q = '-'
    
    data = str(total_today)+','+str(count_new)+','+str(count_old)+','+str(total_month)+','+str(count_q)
   
    return  jsonify(data)

@app.route('/check-member-remainning', methods=['POST'])
def check_member_remainning():
    data = request.get_json()
    load_data = json.loads(data['data'])
    id = load_data['id']
    verify_status = load_data['verify_status']

    parking_code = Parking_log.query.filter_by(Id = id).first().parking_code
    remainning = Carpacity_manage.query.filter_by(parking_code=parking_code).first().member_remaining
    if remainning == 0 and verify_status=='ผ่านการตรวจสอบ':
        return jsonify({'status':False})
    else:
        return jsonify({'status':True})

@app.route("/update_newCus", methods=['POST'])
def update_dashboard():
    data = request.get_json()
    data = json.dumps(data)
    loaded_data = json.loads(data)
    x = datetime.datetime.now()
    date = x.date()
    today = date.strftime('%Y-%m-%d')
    #today_time = x.strftime("%Y-%m-%d, %H:%M:%S")
    id_ = loaded_data['id']
    comment = loaded_data['comment_verify']
    verify_status = loaded_data['verify_status']
    if verify_status == "รอจองคิว":
        cursor = mysql.connection.cursor()
        cursor.execute('update parking_log set verify_status="3" where id=%s',(id_,))
        mysql.connection.commit() 
        change_verify_status_notification(verify_status=verify_status,id=id_)
        return 'success'
    elif verify_status == 'รอให้คิว':
        cursor = mysql.connection.cursor()
        cursor.execute('update parking_log set verify_status="6" where id=%s',(id_,))
        mysql.connection.commit() 
        change_verify_status_notification(verify_status=verify_status,id=id_)
        return 'success'
    elif verify_status == 'ไม่ผ่านการตรวจสอบ':
        cursor = mysql.connection.cursor()
        cursor.execute('update parking_log set verify_status="2" where id=%s',(id_,))
        mysql.connection.commit() 
        change_verify_status_notification(verify_status=verify_status,id=id_)
        return 'success'
    cursor = mysql.connection.cursor()
    cursor.execute('select verify_status,card_id,payment_status,month,identity_card,parking_code,parking_name,first_name,last_name,phone,service_start_date from parking_log where id=%s',(id_,))
    result = cursor.fetchone()
    if result:
     verify = result[0]
     card_id = result[1]
     check_pay_status =result[2]
     month = result[3]
     identity_card=result[4]
     parking_code = result[5]
     
     if verify_status == 'ยกเลิก':
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO parking_log(card_id,input_type,transaction_type,verify_status,payment_status,identity_card,parking_code,parking_name,first_name,last_name,phone) VALUES (%s,"2","3","5",%s, %s,%s,%s,%s,%s,%s)',(card_id,check_pay_status,identity_card,parking_code,result[6],result[7],result[8],result[9]))
        mysql.connection.commit()
        cursor = mysql.connection.cursor()
        cursor.execute('update parking_member set card_status="0" where card_id=%s AND parking_code=%s',(card_id,parking_code))
        mysql.connection.commit() 
     if (verify is None) or (verify == '2') or (verify==""): 
        lastdate_pay = date+timedelta(days=7) #หมดอายุเมื่อลูกค้าไม่จ่ายหลังวันอนุมัติ7วัน
        newcursor = mysql.connection.cursor()
        if verify_status == "ผ่านการตรวจสอบ":
         newcursor.execute('update parking_log set approve_date =%s,lastdate_pay=%s,verify_status=%s where id=%s',(today,lastdate_pay,'1',id_)) #ผ่าน
         mysql.connection.commit()
        else:
          if comment != "":
             newcursor.execute('update parking_log set verify_status=%s,comment=%s where id=%s',("2",comment,id_)) #ไม่ผ่าน
             mysql.connection.commit() 
          else: 
               newcursor.execute('update parking_log set verify_status=%s where id=%s',('2',id_)) #ไม่ผ่าน
               mysql.connection.commit() 
     else:
        payment_name = loaded_data['payment_name']
        if payment_name != "" :
            if  payment_name == "เงินสด":
                payment_name ="1"
            elif payment_name == "บัตรเครดิต/เดบิต":
                payment_name ="2"
            elif payment_name =="Qr code":
                payment_name ="3"
            elif payment_name == "ผูกบัญชีกับธนาคาร":
                payment_name ="4" 
            else:
                payment_name = "xx"
        payment_status = loaded_data['payment_status']
        if payment_status != "" :
            if payment_status == "ชำระแล้ว":
                payment_status ="1"
        else:
            payment_status="0"  
        if payment_name != "xx" and (payment_status =='1'):
            cursor = mysql.connection.cursor()
            cursor.execute('update parking_log set payment_name=%s, payment_status=%s where id=%s',(payment_name,payment_status,id_))
            mysql.connection.commit() 

        payment_date = loaded_data['payment_date']
        split_paydate = payment_date.split("-")
        if 'T' in payment_date: #พนักงานกรอกวันที่ชำระ
            if len(split_paydate[0]) > 4:
                payment_date = datetime.datetime.strptime(payment_date,'%Y-%m-%dT%H:%M')
            cursor = mysql.connection.cursor()
            cursor.execute('update parking_log set payment_date=%s where id=%s',(payment_date,id_))
            mysql.connection.commit()

        card_last_read_date = loaded_data['card_last_read_date']
        if card_last_read_date != "": #พนักงานกรอกวันที่อ่านล่าสุด
            if result[10]:
                service_start_date = result[10].date()
                if date > service_start_date:
                    cursor = mysql.connection.cursor()
                    cursor.execute('update parking_log set service_start_date=%s where id=%s',(date,id_))
                    mysql.connection.commit()
            cur = mysql.connection.cursor()
            cur.execute('select card_expire_date,card_last_read_date from parking_member where card_id=%s AND parking_code=%s  ORDER BY Id DESC',(card_id,parking_code))
            res = cur.fetchone()
            check_expi = res[0]
            check_read = res[1]
            cursorMem = mysql.connection.cursor()
            if '-' in card_last_read_date:
                card_last_read_date = datetime.datetime.strptime(card_last_read_date,'%Y-%m-%d')
            else:
                card_last_read_date = datetime.datetime.strptime(card_last_read_date,'%d/%m/%Y')
            cursorMem.execute('update parking_member set card_last_read_date=%s where card_id=%s',(card_last_read_date,card_id))
            mysql.connection.commit()
            #ต่ออายุบัตร
            if payment_name == '1':
                if check_pay_status is None or(check_pay_status=='0') and (payment_status=='1') :
                 capacity_count(parking_code,id_)
                 renew_card_TAFF_orAll(card_id,month,'1',identity_card,parking_code)  
           
            else:
                if check_pay_status == '1':
                    renew_card_TAFF_orAll(card_id,month,'1',identity_card,parking_code)
            if  check_read is None and (check_expi is None) or (check_expi is None):
                 renew_card_TAFF_orAll(card_id,month,'1',identity_card,parking_code)
            #################################### send email ######################################
    change_verify_status_notification(verify_status=verify_status,id=id_)
    return "success"


@app.route("/update_oldcus", methods=['POST'])
def update_oldcus():
    x = datetime.datetime.now()
    date = x.date()
    data = request.get_json()
    data = json.dumps(data)
    loaded_data = json.loads(data)
    # print(loaded_data)
    id = loaded_data['id']
    cursor = mysql.connection.cursor()
    cursor.execute('select card_id,payment_status,month,identity_card,parking_code,service_start_date from parking_log where id=%s',(id,))
    result = cursor.fetchone()
    if result:
        card_id = result[0]
        check_pay_status = result[1]
        month = result[2]
        identity_card=result[3]
        parking_code = result[4]
        service_start_date = result[5].date()
        payment_name = loaded_data['payment_name']
        if  payment_name == "เงินสด":
            payment_name ="1"
        elif payment_name =="Qr code":
            payment_name ="3"
        elif payment_name == "ผูกบัญชีกับธนาคาร":
            payment_name ="4"
        elif payment_name == "บัตรเครดิต/เดบิต":
            payment_name ="2"
        else:
            payment_name = "xx"
        payment_status = loaded_data['payment_status']
        if payment_status == "ชำระแล้ว":
            payment_status ="1"
        else:
            payment_status="0"

        if payment_name != "xx" : #and (payment_status =='1')
            cursor = mysql.connection.cursor()
            print(payment_status)
            cursor.execute('update parking_log set payment_name=%s, payment_status=%s where id=%s',(payment_name,payment_status,id))
            mysql.connection.commit() 

        payment_date = loaded_data['payment_date']
        split_paydate = payment_date.split("-")
        print(len(split_paydate[0]))
        if 'T' in payment_date: #พนักงานกรอกวันที่ชำระ
            if len(split_paydate[0])>4:
                payment_date = datetime.datetime.strptime(payment_date,'%Y-%m-%dT%H:%M')
            cursor = mysql.connection.cursor()
            cursor.execute('update parking_log set payment_date=%s where id=%s',(payment_date,id))
            mysql.connection.commit()

        card_last_read_date = loaded_data['card_last_read_date']
        if card_last_read_date != "": #พนักงานกรอกวันที่อ่านล่าสุด
            # if date > service_start_date:
            #     cursor = mysql.connection.cursor()
            #     cursor.execute('update parking_log set service_start_date=%s where id=%s',(date,id))
            #     mysql.connection.commit()
            cur = mysql.connection.cursor()
            cur.execute('select card_expire_date,card_last_read_date from parking_member where card_id=%s AND parking_code=%s  ORDER BY Id DESC',(card_id,parking_code))
            res = cur.fetchone()
            if '-' in card_last_read_date:
                card_last_read_date = datetime.datetime.strptime(card_last_read_date,'%Y-%m-%d')
            else:
                card_last_read_date = datetime.datetime.strptime(card_last_read_date,'%d/%m/%Y')
            check_expi = res[0]
            check_read = res[1]
            cursorMem = mysql.connection.cursor()
            cursorMem.execute('update parking_member set card_last_read_date=%s where card_id=%s',(card_last_read_date,card_id))
            mysql.connection.commit() 

            #ต่ออายุบัตร
            if payment_name == '1': #ถ้าเลือกช่องทางเงินสด
                print('11')
                if check_pay_status is None or(check_pay_status=='0') and (payment_status=='1') :
                    capacity_count(parking_code,id)
                    renew_card_TAFF_orAll(card_id,month,'1',identity_card,parking_code)     
            else:
                print('22')
                capacity_count(parking_code,id)
                card_expire_date = result[5] + datetime.timedelta(genday(int(result[2]),result[5].strftime('%Y-%m-%d')))
                mem = Parking_member.query.filter_by(card_id=card_id).filter(Parking_member.parking_code==parking_code)\
                    .filter(Parking_member.identity_card==identity_card).first()
                mem.card_expire_date = card_expire_date
            
                db.session.commit()
                # if check_pay_status == '1':
                #     renew_card_TAFF_orAll(card_id,month,'1',identity_card,parking_code)
            if  check_read is None and (check_expi is None) or (check_expi is None):
                print('33')
                renew_card_TAFF_orAll(card_id,month,'1',identity_card,parking_code)

    return "success"
    
@app.route("/update_cancleCus", methods=['POST'])
def update_cancleCus():
    data = request.get_json()
    data = json.dumps(data)
    loaded_data = json.loads(data)
    id = loaded_data['id']
    cursor = mysql.connection.cursor()
    cursor.execute('select card_id from parking_log where id=%s',(id,))
    result = cursor.fetchone()
    card_id = result[0]
    depositStatus = loaded_data['depositStatus']
    if depositStatus == 'คืนแล้ว':
        depositStatus = '1'
    else:
        depositStatus = '2'
    return_card = loaded_data['return_card']
    if return_card == 'คืนแล้ว':
        return_card = '1'
    else:
        return_card = '2'
    comment = loaded_data['comment']
    cursor = mysql.connection.cursor()
    cursor.execute('update parking_member set deposit_status=%s, return_card=%s where card_id=%s',(depositStatus,return_card,card_id))
    mysql.connection.commit()

    cursor2 = mysql.connection.cursor()
    cursor2.execute('update parking_log set deposit_status=%s ,comment = %s where id=%s',(depositStatus,comment,id))
    mysql.connection.commit()

    return "success"
    
@app.route('/tableOld_cus',methods=["POST"])
def tableOld_cus():
    month = datetime.datetime.now().month  
    year =  datetime.datetime.now().year 
    data = request.get_json()
    data = data.split(",")
    today = datetime.datetime.today()
    before_month = today + relativedelta(months=-1)
    show_date = before_month.replace(day=calendar.monthrange(before_month.year,before_month.month)[1])
    show_date = show_date - datetime.timedelta(7)
    cursor = mysql.connection.cursor()
    if len(data)>2:
        del data[0]  
        format_strings = ','.join(['%s'] * (len(data)))
        query_params = data
        query_params.append(show_date)
        # query_params.append(month)
        query_params.append(year)
        cursor.execute('select pk.card_id,pk.approve_date,pk.first_name,pk.last_name,pk.phone,pk.parking_name,pk.parking_type_name,pk.month,\
        pk.total,pk.payment_name,pk.payment_status,pk.id,pk.payment_date,pk.service_start_date,mem.card_last_read_date,pk.payRef_ktb,mem.card_expire_date,pk.input_type FROM parking_log as pk left join parking_member as mem on pk.card_id =  mem.card_id  AND pk.parking_code = mem.parking_code AND pk.identity_card = mem.identity_card AND (mem.card_status IS NULL OR mem.card_status = "1") AND (mem.return_card IS NULL OR mem.return_card = "0")\
        WHERE pk.transaction_type="2" AND pk.parking_name IN ({data})  AND pk.approve_date>=%s AND YEAR(pk.lastdate_pay)>=%s AND pk.void IS NULL ORDER BY pk.id DESC'.format(data=format_strings),query_params)
        result = cursor.fetchall() 
        print(1)  
    else:
        line = data[0]
        park = data[1]
        if line == "ทั้งหมด":
            listcode = get_codePark()
            format_strings = ','.join(['%s'] * (len(listcode)))
            query_params = listcode
            query_params.append(show_date)
            # query_params.append(month)
            query_params.append(year)
            cursor.execute('select pk.card_id,pk.approve_date,pk.first_name,pk.last_name,pk.phone,pk.parking_name,pk.parking_type_name,pk.month,\
            pk.total,pk.payment_name,pk.payment_status,pk.id,pk.payment_date,pk.service_start_date,mem.card_last_read_date,pk.payRef_ktb,mem.card_expire_date,pk.input_type  FROM parking_log as pk left join parking_member as mem on pk.card_id =  mem.card_id  AND pk.parking_code = mem.parking_code AND pk.identity_card = mem.identity_card AND (mem.card_status IS NULL OR mem.card_status = "1") AND (mem.return_card IS NULL OR mem.return_card = "0")\
            WHERE pk.transaction_type="2"AND pk.parking_code IN ({listcode}) AND pk.approve_date>=%s AND YEAR(pk.lastdate_pay)>=%s AND pk.void IS NULL ORDER BY pk.id DESC'.format(listcode=format_strings),query_params)
            result = cursor.fetchall()
            
        else:
            cursor.execute('select pk.card_id,pk.approve_date,pk.first_name,pk.last_name,pk.phone,pk.parking_name,pk.parking_type_name,pk.month,\
            pk.total,pk.payment_name,pk.payment_status,pk.id,pk.payment_date,pk.service_start_date,mem.card_last_read_date,pk.payRef_ktb,mem.card_expire_date ,pk.input_type FROM parking_log as pk left join parking_member as mem on pk.card_id =  mem.card_id AND pk.parking_code = mem.parking_code AND pk.identity_card = mem.identity_card AND (mem.card_status IS NULL OR mem.card_status = "1") AND (mem.return_card IS NULL OR mem.return_card = "0")\
            WHERE pk.transaction_type="2" AND pk.approve_date>=%s AND YEAR(pk.lastdate_pay)>=%s AND pk.parking_name=%s AND pk.void IS NULL ORDER BY pk.id DESC',(show_date,year,park))
            result = cursor.fetchall()
            print(show_date)
            print(year)
            print(park)
       
    
    return  jsonify(result)


@app.route('/tableCancle_cus',methods=["POST"])
def tableCancle_cus():
    data = request.get_json()
    data = data.split(",")
    cursor = mysql.connection.cursor()
    if len(data)>2:
        del data[0]  
        format_strings = ','.join(['%s'] * (len(data)))
        query_params = data
        cursor.execute('select pk.card_id,pk.parking_register_date,mem.card_expire_date,pk.first_name,pk.last_name,pk.phone,pk.parking_name,pk.parking_type_name,\
        mem.deposit_amount,mem.deposit_status,mem.return_card,pk.comments,pk.id,pk.input_type FROM parking_log as pk left join parking_member as mem on pk.card_id =  mem.card_id AND pk.parking_code = mem.parking_code AND pk.identity_card = mem.identity_card AND mem.card_status = 0\
        WHERE pk.transaction_type="3" AND pk.parking_name IN ({data}) ORDER BY pk.id DESC'.format(data=format_strings),query_params)
        result = cursor.fetchall()  
    else:
        line = data[0]
        park = data[1]
        if line == "ทั้งหมด":
            listcode = get_codePark()
            format_strings = ','.join(['%s'] * (len(listcode)))
            query_params = listcode
          
            cursor.execute('select pk.card_id,pk.parking_register_date,mem.card_expire_date,pk.first_name,pk.last_name,pk.phone,pk.parking_name,pk.parking_type_name,\
            mem.deposit_amount,mem.deposit_status,mem.return_card,pk.comments,pk.id,pk.input_type FROM parking_log as pk left join parking_member as mem on pk.card_id =  mem.card_id AND pk.parking_code = mem.parking_code AND pk.identity_card = mem.identity_card AND mem.card_status = 0\
            WHERE pk.transaction_type="3" AND pk.parking_code IN ({listcode}) ORDER BY pk.id DESC'.format(listcode=format_strings),query_params)
            result = cursor.fetchall()
         
        else:
            cursor.execute('select pk.card_id,pk.parking_register_date,mem.card_expire_date,pk.first_name,pk.last_name,pk.phone,pk.parking_name,pk.parking_type_name,\
            mem.deposit_amount,mem.deposit_status,mem.return_card,pk.comments,pk.id,pk.input_type FROM parking_log as pk left join parking_member as mem on pk.card_id =  mem.card_id AND pk.parking_code = mem.parking_code AND pk.identity_card = mem.identity_card AND mem.card_status = 0\
            WHERE pk.transaction_type="3" AND pk.parking_name=%s ORDER BY pk.id DESC',(park,))
            result = cursor.fetchall()
    return  jsonify(result)

@app.route('/tableExpire_cus',methods=["POST"])
def tableExpire_cus():
    data = request.get_json()
    data = data.split(",")
    cursor = mysql.connection.cursor()
    if len(data)>2:
        del data[0]  
        format_strings = ','.join(['%s'] * (len(data)))
        cursor.execute('select mem.card_id,mem.parking_register_date,mem.first_name_th,mem.last_name_th,mem.phone,park.parking_name,mem.card_last_read_date,mem.card_expire_date FROM parking_member as mem left join parking_manage as park\
        on mem.parking_code=park.parking_code where park.parking_name IN ({data}) AND CURDATE()-mem.card_expire_date<= 7 AND CURDATE()-mem.card_expire_date >= 0 '.format(data=format_strings),data)
        result = cursor.fetchall() 
    else:
        line = data[0]
        park = data[1]
        if line == "ทั้งหมด":
            listcode = get_codePark()
            print(listcode)
            format_strings = ','.join(['%s'] * (len(listcode)))
            cursor.execute('select mem.card_id,mem.parking_register_date,mem.first_name_th,mem.last_name_th,mem.phone,park.parking_name,mem.card_last_read_date,mem.card_expire_date FROM parking_member as mem \
            left join parking_manage as park on mem.parking_code=park.parking_code WHERE mem.parking_code IN ({listcode}) AND CURDATE()-mem.card_expire_date<= 7 AND CURDATE()-mem.card_expire_date >= 0 '.format(listcode=format_strings),listcode)
            result = cursor.fetchall()
        else:
            cursor.execute('select mem.card_id,mem.parking_register_date,mem.first_name_th,mem.last_name_th,mem.phone,park.parking_name,mem.card_last_read_date,mem.card_expire_date FROM parking_member as mem\
            left join parking_manage as park on mem.parking_code=park.parking_code WHERE park.parking_name=%s AND CURDATE()-mem.card_expire_date<= 7 AND CURDATE()-mem.card_expire_date >= 0 ',(park,))
            result = cursor.fetchall()

    return  jsonify(result)
    
@app.route('/tablePending_cus',methods=["POST"])
def tablePending_cus():
    data = request.get_json()
    data = data.split(",")
    cursor = mysql.connection.cursor()
    if len(data)>2:
        del data[0]  
        format_strings = ','.join(['%s'] * (len(data)))
        cursor.execute('select pk.card_id,pk.parking_register_date,pk.first_name,pk.last_name,pk.phone,pk.parking_name,pk.payment_date,mem.card_last_read_date,mem.card_expire_date,pk.id,pk.input_type FROM parking_log as pk left join parking_member as mem on pk.card_id =  mem.card_id AND pk.parking_code = mem.parking_code\
        WHERE DATE(pk.payment_date) > DATE(mem.card_last_read_date) AND pk.payment_status="1" AND pk.parking_name IN ({data}) ORDER BY pk.id DESC'.format(data=format_strings),data)
        result = cursor.fetchall()
    else:
        line = data[0]
        park = data[1]
        if line == "ทั้งหมด":
            listcode = get_codePark()
            format_strings = ','.join(['%s'] * (len(listcode)))
            cursor.execute('select pk.card_id,pk.parking_register_date,pk.first_name,pk.last_name,pk.phone,pk.parking_name,pk.payment_date,mem.card_last_read_date,mem.card_expire_date,pk.id,pk.input_type FROM parking_log as pk left join parking_member as mem on pk.card_id =  mem.card_id AND pk.parking_code = mem.parking_code\
            left join parking_manage as line on pk.parking_name=line.parking_name WHERE DATE(pk.payment_date) > DATE(mem.card_last_read_date) AND pk.payment_status="1"  AND pk.parking_code IN ({listcode}) ORDER BY pk.id DESC'.format(listcode=format_strings),listcode)
            result = cursor.fetchall()
        else:
            cursor.execute('select pk.card_id,pk.parking_register_date,pk.first_name,pk.last_name,pk.phone,pk.parking_name,pk.payment_date,mem.card_last_read_date,mem.card_expire_date,pk.id,pk.input_type FROM parking_log as pk left join parking_member as mem on pk.card_id =  mem.card_id AND pk.parking_code = mem.parking_code\
            WHERE DATE(pk.payment_date) > DATE(mem.card_last_read_date) AND pk.payment_status="1" AND pk.parking_name=%s ORDER BY pk.id DESC',(park,))
            result = cursor.fetchall()
    return  jsonify(result)

@app.route('/manage/autopark')  # หน้าdashboard
def autoParking():
    listpark=get_codePark()
    cursor = mysql.connection.cursor()
    cursor.execute('select parking_name,line_name,parking_code FROM parking_manage')
    result = cursor.fetchall()
    return jsonify(result,listpark)

@app.route('/search_line',methods=["POST","GET"]) # หน้าdashboard
def  search_line():
    month = datetime.datetime.now().month    
    year =  datetime.datetime.now().year
    data = request.get_json()
    data = data.split(",")
    today = datetime.datetime.today()
    before_month = today + relativedelta(months=-1)
    show_date = before_month.replace(day=calendar.monthrange(before_month.year,before_month.month)[1])
    show_date = show_date - datetime.timedelta(10)
    print(show_date)
    cursor = mysql.connection.cursor()
    if len(data)>2:
        del data[0]  
        format_strings = ','.join(['%s'] * (len(data)))
        query_params = data 
        query_params.append(show_date)
        # query_params.append(year)
        cursor.execute('select pk.card_id,pk.parking_register_date,pk.first_name,pk.last_name,pk.phone,pk.parking_name,pk.parking_type_name,pk.month,\
        pk.total,mem.copy_id_card,mem.copy_doc_car1,pk.verify_status,pk.q_no,pk.q_up,pk.payment_name,pk.payment_status,pk.id,pk.payment_date,mem.card_last_read_date,pk.payRef_ktb,mem.copy_doc_car2,mem.card_member_copy,pk.service_start_date,mem.card_expire_date,pk.deposit_amount,pk.input_type FROM parking_log as pk left join parking_member as mem on pk.card_id =  mem.card_id AND pk.identity_card = mem.identity_card AND pk.parking_code = mem.parking_code AND (mem.card_status IS NULL OR mem.card_status = 1) AND (mem.return_card IS NULL OR mem.return_card = "0")\
        WHERE pk.transaction_type="1" AND pk.parking_name IN ({data}) AND (pk.parking_register_date>=%s OR pk.verify_status="6") AND pk.void IS NULL ORDER BY pk.id DESC'.format(data=format_strings),query_params)
        result = cursor.fetchall()       
    else:
     line = data[0]
     park = data[1]
     if line == "ทั้งหมด":
        listcode = get_codePark()
        format_strings = ','.join(['%s'] * (len(listcode)))
        query_params = listcode
        query_params.append(show_date)
        # query_params.append(year)
        cursor.execute('select pk.card_id,pk.parking_register_date,pk.first_name,pk.last_name,pk.phone,pk.parking_name,pk.parking_type_name,pk.month,\
        pk.total,mem.copy_id_card,mem.copy_doc_car1,pk.verify_status,pk.q_no,pk.q_up,pk.payment_name,pk.payment_status,pk.id,pk.payment_date,mem.card_last_read_date,pk.payRef_ktb,mem.copy_doc_car2,mem.card_member_copy,pk.service_start_date,mem.card_expire_date,pk.deposit_amount,pk.input_type FROM parking_log as pk left join parking_member as mem on pk.card_id =  mem.card_id AND pk.identity_card = mem.identity_card AND pk.parking_code = mem.parking_code AND (mem.card_status IS NULL OR mem.card_status = 1) AND (mem.return_card IS NULL OR mem.return_card = "0") \
        WHERE pk.transaction_type="1" AND pk.parking_code IN ({listcode}) AND (pk.parking_register_date>=%s OR pk.verify_status="6") AND pk.void IS NULL ORDER BY pk.id DESC'.format(listcode=format_strings),query_params)
        result = cursor.fetchall()
     else:
        cursor.execute('select pk.card_id,pk.parking_register_date,pk.first_name,pk.last_name,pk.phone,pk.parking_name,pk.parking_type_name,pk.month,\
        pk.total,mem.copy_id_card,mem.copy_doc_car1,pk.verify_status,pk.q_no,pk.q_up,pk.payment_name,pk.payment_status,pk.id,pk.payment_date,mem.card_last_read_date,pk.payRef_ktb,mem.copy_doc_car2,mem.card_member_copy,pk.service_start_date,mem.card_expire_date,pk.deposit_amount,pk.input_type FROM parking_log as pk left join parking_member as mem on pk.card_id =  mem.card_id AND pk.identity_card = mem.identity_card AND pk.parking_code = mem.parking_code AND (mem.card_status IS NULL OR mem.card_status = 1) AND (mem.return_card IS NULL OR mem.return_card = "0") \
        WHERE pk.transaction_type="1" AND pk.parking_name = %s AND (pk.parking_register_date>=%s OR pk.verify_status="6") AND pk.void IS NULL ORDER BY pk.id DESC',(park,show_date))
        result = cursor.fetchall()
    return  jsonify(result)

def get_codePark():
    cur = mysql.connection.cursor()
    cur.execute('select parking_code FROM user_manage WHERE username=%s',(session['username'],))
    listpark = cur.fetchone()
    listpark = listpark[0].split(",")
    return listpark

def check_parking():
    user = session['username']
    cursor = mysql.connection.cursor()
    sql = "SELECT parking_code FROM user_manage WHERE username = %s"
    val = (user,)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    parking = result[0]
    return parking


@app.route('/manage/extend-card')
def extend_card():
    session['cid'] = " "
    return render_template('/manage/extend-card3.html')


@app.route('/search', methods=["POST", "GET"])  # passachon
def search():
   cid = request.args.get('search')
   cid = str(cid)
   session['cid'] = cid
   parking = check_parking()
   x = datetime.datetime.now()
   date = x.date()
   paytoday = date.strftime('%d/%m/%Y')
   cursor = mysql.connection.cursor()
   sql = "SELECT pk.payment_name,pk.payment_status,pk.payment_date,pk.lastdate_pay,pk.orderNumber,pk.month,pk.parking_type_name,mem.card_last_read_date FROM parking_log as pk left join parking_member as mem on pk.card_id =  mem.card_id AND pk.parking_code = mem.parking_code AND (mem.card_status IS NULL OR mem.card_status = 1) AND (mem.return_card IS NULL OR mem.return_card = '0')\
      WHERE pk.card_id = %s AND pk.parking_code = %s ORDER BY pk.id DESC limit 1"
   val = (cid, parking)
   cursor.execute(sql, val)
   result = cursor.fetchone()
   if result:
        paytype = result[0]
        status = result[1]
        payment_date = result[2]
        lastdate_pay = result[3]
        session['ref2'] = result[4]
        session['month'] = result[5]
        typeCard = result[6]
        last_read_date = result[7]
        if paytype is None:
            paytype = '-'
        elif paytype != '1' or (paytype is None):
            if paytype == '2':
                paytype = "เครดิต/เดบิต"
            elif paytype == '3':
                paytype = "คิวอาร์โค้ด" 
            elif paytype == '4':
                paytype = "ผูกบัญชี"
        else:
           paytype = "เงินสด" 
        if status == '0' or(status is None):
            status = 'ยังไม่ชำระ'
        else:
            status = 'ชำระแล้ว'
        if payment_date is None or(str(payment_date) == "1899-12-29 00:00:00"):
           payment_date = "-"
        else:
         payment_date = result[2].date()
         check_date = (date-payment_date).days
        if typeCard == "TAFF":
            cid = "ขออภัย ไม่สามารถทำรายการให้กับบัตรประเภท TAFF "
            return render_template('/manage/extend-card3.html', paytype="", status="", payment_date="", cid=cid)
        if lastdate_pay:
            if date > lastdate_pay:
                cid = "รายการล่าสุดหมดอายุ กรุณาแจ้งลูกค้าหมายเลขบัตร: "+cid
                return render_template('/manage/extend-card3.html', paytype=paytype, status=status, payment_date=payment_date, cid=cid)
        if paytype != 'เงินสด':
            if payment_date  == '-':
                return render_template('/manage/extend-card3.html', paytype=paytype, status=status, payment_date=payment_date, cid=cid)
            if check_date>7:#จ่ายมาเกิน7วันไม่มาต่ออายุบัตร
                cid = "รายการล่าสุดไม่ได้นำบัตรมาต่ออายุเกินระยะเวลาที่กำหนด"
                return render_template('/manage/extend-card3.html', paytype=paytype, status=status, payment_date=payment_date, cid=cid)
            if last_read_date:
                last_read_date = result[7].date()
                if last_read_date > payment_date:
                    cid = "รายการล่าสุดถูกต่ออายุไปเมื่อวันที่ "+ str(last_read_date)+ " ไม่สามารถต่ออายุซ้ำให้กับลูกค้าหมายเลขบัตร: "+cid
                    return render_template('/manage/extend-card3.html', paytype=paytype, status=status, payment_date=payment_date, cid=cid)
                elif last_read_date == payment_date:
                    cid = "ต่ออายุบัตรให้กับลูกค้าหมายเลขบัตร: "+cid+" เรียบร้อยแล้ว"
                    return render_template('/manage/extend-card3.html', paytype=paytype, status=status, payment_date=payment_date, cid=cid)
                return render_template('/manage/extend-card2.html', paytype=paytype, status=status, payment_date=payment_date, cid=cid)
            return render_template('/manage/extend-card2.html', paytype=paytype, status=status, payment_date=payment_date, cid=cid)#ไม่มีฟิลด์ card_last_read_dateไม่ต้องเช็ก แสดงเลย
        #เงินสด
        if status == "ชำระแล้ว": 
            print(last_read_date,payment_date)
            if last_read_date:
                last_read_date = result[7].date() 
                if check_date>7:#จ่ายมาเกิน7วันไม่มาต่ออายุบัตร
                 cid = "รายการล่าสุดไม่ได้นำบัตรมาต่ออายุเกินระยะเวลาที่กำหนด"
                 return render_template('/manage/extend-card3.html', paytype=paytype, status=status, payment_date=payment_date, cid=cid)
                if last_read_date > payment_date:
                    cid = "รายการล่าสุดถูกต่ออายุไปเมื่อวันที่ "+ str(last_read_date)+ " ไม่สามารถต่ออายุซ้ำให้กับลูกค้าหมายเลขบัตร: "+cid
                    return render_template('/manage/extend-card3.html', paytype=paytype, status=status, payment_date=payment_date, cid=cid)
                elif last_read_date == payment_date:
                    cid = "ต่ออายุบัตรให้กับลูกค้าหมายเลขบัตร: "+cid+" เรียบร้อยแล้ว"
                    return render_template('/manage/extend-card3.html', paytype=paytype, status=status, payment_date=payment_date, cid=cid)
                return render_template('/manage/extend-card2.html', paytype=paytype, status=status, payment_date=payment_date, cid=cid)
            return render_template('/manage/extend-card2.html', paytype=paytype, status=status, payment_date=payment_date, cid=cid)#ไม่มีฟิลด์ card_last_read_dateไม่ต้องเช็ก แสดงเลยกรณีสมัครใหม่

        paytoday = "วันที่ชำระเงินสด "+paytoday
        return render_template('/manage/extend-card.html', paytype=paytype, status=status, payment_date=payment_date, cid=cid, paytoday=paytoday)
   return render_template('/manage/extend-card3.html', cid="ไม่พบข้อมูลลูกค้า")


@app.route('/update', methods=["POST", "GET"])  # passachon
def update():
    parking = check_parking()
    x = datetime.datetime.now()
    date = x.date()
    date = date.strftime('%Y-%m-%d')
    cursor = mysql.connection.cursor()
    sql = "UPDATE parking_log SET payment_status= %s,payment_date=%s WHERE card_id = %s AND parking_code=%s ORDER BY id DESC limit 1"#AND orderNumber = %s
    val = ('1', date, session['cid'],parking)#, session['ref2']
    cursor.execute(sql, val)
    mysql.connection.commit()
    return redirect(url_for('search'))

@app.route('/renew_card', methods=["POST", "GET"])
def renew_card():
    parking = check_parking()
    today = datetime.datetime.now().date()
    year_today = today.year
    month_today = today.month
    cursor = mysql.connection.cursor()
    sql = "SELECT card_expire_date FROM parking_member WHERE card_id = %s AND parking_code =%s"
    val = (session['cid'],parking)
    cursor.execute(sql, val)
    result = cursor.fetchone()

    cur = mysql.connection.cursor()
    q = "SELECT service_start_date FROM parking_log WHERE card_id = %s AND parking_code =%s ORDER BY id DESC limit 1"
    cur.execute(q, val)
    res = cur.fetchone()
    print(res[0])
    if res[0] is None:
        print("hello")
    else:
        service = res[0].date()
        if today > service:
            year =  year_today 
            month = month_today
        else:
            year = service.year
            month = service.month
        sum_ = cal_numofMonth(year,month)
        new_expi = update_renewCard(sum_,service,today)
        new_expi = "วันที่หมดอายุล่าสุด "+new_expi.strftime('%d/%m/%Y')
        return new_expi
    if result:
        if  result[0]:
            expireDate = result[0].date()
            year = expireDate.year
            month = expireDate.month
            diffday = (expireDate-today).days
            if diffday < 0:  # เช็คว่าถึงวันหมดอายุรึยัง ถ้าหมดแล้ว ต่ออายุจากวันที่่มาต่ออายุ
             sum_ = cal_numofMonth(year_today, month_today)
             new_expi = update_renewCard(sum_, today, today)
            else:  # ยังไม่หมดอายุ ต่ออายุจากวันหมดอายุเดิม
             sum_ = cal_numofMonth(year, month)
             new_expi = update_renewCard(sum_, expireDate, today)
        else:
            sum_ = cal_numofMonth(year_today, month_today)
            new_expi = update_renewCard(sum_, today, today)
        new_expi = "วันที่หมดอายุล่าสุด "+new_expi.strftime('%d/%m/%Y')
        return new_expi
    return "error"



def update_renewCard(sum, date, today):
    parking = check_parking()
    new_expi = date+timedelta(days=sum)
    cursor = mysql.connection.cursor()
    sql = "UPDATE parking_member SET card_last_read_date = %s,card_expire_date=%s WHERE card_id =%s AND parking_code = %s"
    val = (today, new_expi, session['cid'],parking)
    cursor.execute(sql, val)
    mysql.connection.commit()
    return new_expi


def get_numofMonth(year, month):  # จำนวนวันแต่ละเดือน
    first_weekday, num_days_in_month = calendar.monthrange(year, month)
    return num_days_in_month


def cal_numofMonth(year, month):
    count = session['month']  # จำนวนเดือนที่ลูกค้าต่อ
    sum = 0
    for i in range(count):
        month = month+1
        if month > 12:
            year = year + 1
            month = 1
        sum = sum + get_numofMonth(year, month)

    return sum
###############################################ittipon####################################################################


@app.route('/manage/capacity-member')
def capacity_member():
    today = datetime.datetime.today()
    rows = Carpacity_manage.query.all()
    data = []
    for row in rows:
        d = {}
        for col in row.__table__.columns.keys():
            # if col == 'count_online':
                
            #     d[col] = 0 
            #     all_member1 = Parking_member.query.filter(Parking_member.card_expire_date > today).filter(Parking_member.parking_code==row.parking_code).all()
            #     for member in all_member1:
            #         check_log = Parking_log.query.filter_by(card_id=member.card_id).filter(Parking_log.parking_code == member.parking_code)\
            #             .filter(Parking_log.transaction_type != '3').filter(Parking_log.service_start_date < today).order_by(Parking_log.Id.desc()).first()
            #         if check_log:
            #             if check_log.input_type == '1' and check_log.service_start_date <= today:
            #                 d[col] +=1
            #     setattr(row,col,d[col])
            # elif col == 'count_contect_site':
                
            #     n = 0
            #     all_member = Parking_member.query.filter(Parking_member.card_expire_date > today).filter(Parking_member.parking_code==row.parking_code).all()
            #     for member in all_member:
            #         check_log = Parking_log.query.filter_by(card_id=member.card_id).filter(Parking_log.parking_code == member.parking_code)\
            #             .filter(Parking_log.transaction_type != '3').filter(Parking_log.service_start_date < today).order_by(Parking_log.Id.desc()).first()
            #         if check_log:
            #             if check_log.input_type == '2' and check_log.service_start_date <= today:
            #                 n +=1
            #     d[col] = n
            #     setattr(row,col,d[col])
            # elif col == 'member_remaining':
            #     d[col] = row.member_limit - d['count_online'] - d['count_contect_site'] + row.adjust_member
            #     setattr(row,col,d[col])
            if col == 'user_edit_date':
                if getattr(row,col):
                    d[col] = getattr(row,col).strftime('%d/%m/%Y') 
                else:
                    d[col] = getattr(row,col)   
            else:   
                d[col] = getattr(row,col)
        data.append(d)
        
    db.session.commit()
    return render_template('manage/capacity-member.html', datas=data)


@app.route('/manage/update_capacity_menage', methods=['POST'])
def update_capacity_manage():
    if request.method == 'POST':
        Id = request.form.get('id')
        user_edit_date = datetime.datetime.today()
        
        ct = Carpacity_manage.query.filter_by(Id=Id).first()
        for key,value in request.form.to_dict().items():
            if key != 'id':
                if value != '':
                    if getattr(ct,key) != value:
                        setattr(ct,key,value)
        setattr(ct,'member_remaining',int(ct.member_limit) - ct.count_online - ct.count_contect_site + int(ct.adjust_member))               
        ct.user_edit = session.get('username')
        ct.user_edit_date = user_edit_date
        db.session.commit()
        return redirect(url_for('capacity_member'))


@app.route('/manage/tax-invoice/<id_>')
def tax_invoice(id_):
    tax_log = Parking_log.query.filter_by(Id = id_).first()
    if tax_log.transaction_type == '4':
        if tax_log.address_type == '2':
            identity_card = f'{tax_log.identity_com[:1]} {tax_log.identity_com[1:5]} {tax_log.identity_com[5:10]} {tax_log.identity_com[10:12]} {tax_log.identity_com[12:]}'
            address = create_address_company(tax_log)
            name = tax_log.company_name
        else :
            identity_card = f'{tax_log.identity_card[:1]} {tax_log.identity_card[1:5]} {tax_log.identity_card[5:10]} {tax_log.identity_card[10:12]} {tax_log.identity_card[12:]}'
            address = create_address(tax_log)
            name = f'{tax_log.first_name} {tax_log.last_name}'
        station = Parking_manage.query.filter_by(parking_code=tax_log.parking_code).first()
        branch = station.parking_branch.zfill(5)
        vat = f'{tax_log.vat:,.2f}'
        total = f'{tax_log.total:,.2f}'
        amount = f'{tax_log.amount:,.2f}'
        thaibath = ThaiBahtConversion(float(total))
        thaidate = change_to_thaitime(tax_log.payment_date.strftime('%d-%m-%Y'))
        payment_name =  paymentName(tax_log.payment_name)
        start_inv_no = station.start_inv_no
        invoice_db = start_inv_no.split('/')
        invoice = f'{invoice_db[0]}/01/{invoice_db[1]}/{invoice_db[2]}'
        return render_template(
            'manage/tax-invoice.html',tax_log=tax_log,payment_name=payment_name,
            identity_card=identity_card,branch=branch,vat=vat,amount=amount,address=address,
            total=total,thaibath=thaibath,thaidate=thaidate,invoice=invoice,name=name)

    else:
        tax_mem = Parking_member.query.filter_by(card_id = tax_log.card_id).filter(Parking_member.identity_card == tax_log.identity_card)\
            .filter(Parking_member.parking_code == tax_log.parking_code)\
            .filter(or_(Parking_member.card_status == '1',Parking_member.card_status == None)).first()
        if tax_log.address_type == 'home':
            identity_card = f'{tax_mem.identity_card[:1]} {tax_mem.identity_card[1:5]} {tax_mem.identity_card[5:10]} {tax_mem.identity_card[10:12]} {tax_mem.identity_card[12:]}'
            address = create_address(tax_mem)
        else:
            address = create_address_company(tax_mem)
            if tax_mem.identity_com:
                identity_card = f'{tax_mem.identity_com[:1]} {tax_mem.identity_com[1:5]} {tax_mem.identity_com[5:10]} {tax_mem.identity_com[10:12]} {tax_mem.identity_com[12:]}'
            else:
                identity_card = 'กรุณาเพิ่มเลขที่ผู้เสียภาษีที่หน้าจัดการข้อมูล Customer'
        station = Parking_manage.query.filter_by(parking_code=tax_log.parking_code).first()
        branch = station.parking_branch.zfill(5)
        vat = f'{tax_log.vat:,.2f}'
        total = tax_log.total - tax_log.deposit_amount
        amount = f'{tax_log.amount:,.2f}'
        thaibath = ThaiBahtConversion(float(total))
        thaidate = change_to_thaitime(tax_log.payment_date.strftime('%d-%m-%Y'))
        total = f'{total:,.2f}'
        if tax_log.payment_name == '5':
            payment_name = 'เช็ค'
        else :
            payment_name = 'เงินสด'
        invoice = tax_log.invoice_no
        if tax_log.deposit_amount == 0:
            return render_template(
                'manage/tax-invoice.html',tax_log=tax_log,tax_mem=tax_mem,payment_name=payment_name,
                identity_card=identity_card,branch=branch,vat=vat,amount=amount,address=address,
                total=total,thaibath=thaibath,thaidate=thaidate,invoice=invoice)
        else:
            if tax_log.deposit_address_type == 'company':
                address2 = create_address_company(tax_mem)
                if tax_mem.identity_com:
                    identity_card2 = f'{tax_mem.identity_com[:1]} {tax_mem.identity_com[1:5]} {tax_mem.identity_com[5:10]} {tax_mem.identity_com[10:12]} {tax_mem.identity_com[12:]}'
                else:
                    identity_card2 = 'กรุณาเพิ่มเลขที่ผู้เสียภาษีที่หน้าจัดการข้อมูล Customer'
            else:
                address2 = create_address(tax_mem)
                identity_card2 = f'{tax_mem.identity_card[:1]} {tax_mem.identity_card[1:5]} {tax_mem.identity_card[5:10]} {tax_mem.identity_card[10:12]} {tax_mem.identity_card[12:]}'
            deposit = round((float(tax_log.deposit_amount) * (100/107)),2)
            thaibath2 = ThaiBahtConversion(float(tax_log.deposit_amount))
            vat2 = round(((float(tax_log.deposit_amount)) - deposit),2)
            total2 = f'{tax_log.deposit_amount:,.2f}'
            if tax_log.invoice_deposit:
                invoice2 = tax_log.invoice_deposit
            else:
                invoice2 = None
            return render_template(
                'manage/tax-invoice.html',tax_log=tax_log,tax_mem=tax_mem,payment_name=payment_name,
                identity_card=identity_card,branch=branch,vat=vat,amount=amount,address=address,
                total=total,thaibath=thaibath,thaidate=thaidate,invoice=invoice,address2=address2,
                identity_card2=identity_card2,deposit=deposit,thaibath2=thaibath2,
                vat2=vat2,invoice2=invoice2,total2=total2)


@app.route('/manage/user-profile')
def user_profile():
    cur = mysql.connection.cursor()
    cur.execute(""" select id, first_name, last_name, username, password, line_token
                    from user_manage """)
    row = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return render_template('manage/user-profile.html', datas=row)


def caldiff():
    cur = mysql.connection.cursor()
    cur.execute(
        """ update parking_log SET diffdate=DATEDIFF(card_expire_date,now()) """)
    mysql.connection.commit()
    cur.close()


def beforeaffter():
    cur = mysql.connection.cursor()
    cur.execute("""  update parking_log SET before7=if(diffdate>=0 and diffdate<=7,"1","0"),
                     after7=if(diffdate<=0 and diffdate>=-7,"1","0") """)
    mysql.connection.commit()
    cur.close()

    return redirect(url_for())


@app.route('/manage/station_id/<station_id>/<station>')
def station_id(station_id,station):
    parking_code = Parking_manage.query.filter_by(Id=station).first().parking_code
    member = Parking_member.query.filter_by(card_id=station_id).filter(Parking_member.parking_code==parking_code)\
        .filter(or_(Parking_member.return_card =='0',Parking_member.return_card==None)).first()
    parking_id = station
    print(parking_code)
    print(member)
    if member:
        dict_ = {}
        dict_['card_expire_date'] = member.card_expire_date
        dict_['parking_id'] = parking_id
        dict_['status'] = check_status_card(member.card_expire_date)
        dict_['fetch_status'] = 'success'
    else:
        dict_ = {}
        dict_['fetch_status'] = 'faill'

    return jsonify(dict_)


@app.route('/manage/card_id_/<id_>/<station>')
def card_id_(id_,station):
    parking_code = Parking_manage.query.filter_by(Id=station).first().parking_code
    data = Parking_member.query.filter_by(card_id=id_).filter(Parking_member.parking_code==parking_code).order_by(Parking_member.Id.desc())\
        .filter(or_(Parking_member.return_card =='0',Parking_member.return_card==None)).first()
    user = {}
    province = get_province()
    # user
    user['card_id'] = data.card_id
    user['cus_id'] = data.cus_id
    user['first_name'] = data.first_name_th
    user['last_name'] = data.last_name_th
    user['phone'] = data.phone
    user['identity_card'] = data.identity_card
    # car1
    user['brand_name1'] = data.brand_name1
    user['color1'] = data.color1
    user['license_plate1'] = data.license_plate1
    user['province_car1'] = data.province_car1
    # car2
    user['brand_name2'] = data.brand_name2
    user['color2'] = data.color2
    user['license_plate2'] = data.license_plate2
    user['province_car2'] = data.province_car2
    # home address
    user['unit_home'] = data.unit_home
    user['address_no'] = data.address_no
    user['village'] = data.village
    user['alley'] = data.alley
    user['street'] = data.street
    user['sub_district'] = data.sub_district
    user['district'] = data.district
    user['province'] = data.province
    user['postal_code'] = data.postal_code
    # company address
    user['company_unit'] = data.company_unit
    user['identity_com'] = data.identity_com
    user['company_no'] = data.company_no
    user['company_name'] = data.company_name
    user['company_village'] = data.company_village
    user['company_alley'] = data.company_alley
    user['company_street'] = data.company_street
    user['company_sub_district'] = data.company_sub_district
    user['company_district'] = data.company_district
    user['company_province'] = data.company_province
    user['company_postal_code'] = data.company_postal_code
    user['province_all'] = province
    brand = Brand.query.all()
    data_list = []
    for i in brand:
        brand_d = {}
        brand_d['brand'] = i.brand_name
        data_list.append(brand_d)
    user['brand'] = data_list
    # status
    user['status'] = check_status_card(data.card_expire_date)
    return jsonify(user)

@app.route('/manage/identity_id_/<id_>')
def identity_id_(id_):
    data = Parking_member.query.filter_by(identity_card=id_).first()
    user = {}
    # user
    user['card_id'] = data.card_id
    user['cus_id'] = data.cus_id
    user['first_name'] = data.first_name_th
    user['last_name'] = data.last_name_th
    user['phone'] = data.phone
    user['identity_card'] = data.identity_card
    # car1
    user['brand_name1'] = data.brand_name1
    user['color1'] = data.color1
    user['license_plate1'] = data.license_plate1
    user['province_car1'] = data.province_car1
    # car2
    user['brand_name2'] = data.brand_name2
    user['color2'] = data.color2
    user['license_plate2'] = data.license_plate2
    user['province_car2'] = data.province_car2
    # home address
    user['unit_home'] = data.unit_home
    user['address_no'] = data.address_no
    user['village'] = data.village
    user['alley'] = data.alley
    user['street'] = data.street
    user['sub_district'] = data.sub_district
    user['district'] = data.district
    user['province'] = data.province
    user['postal_code'] = data.postal_code
    # company address
    user['company_unit'] = data.company_unit
    user['identity_com'] = data.identity_com
    user['company_no'] = data.company_no
    user['company_name'] = data.company_name
    user['company_village'] = data.company_village
    user['company_alley'] = data.company_alley
    user['company_street'] = data.company_street
    user['company_sub_district'] = data.company_sub_district
    user['company_district'] = data.company_district
    user['company_province'] = data.company_province
    user['company_postal_code'] = data.company_postal_code
    brand = Brand.query.all()
    data_list = []
    for i in brand:
        brand_d = {}
        brand_d['brand'] = i.brand_name
        data_list.append(brand_d)
    user['brand'] = data_list
    return jsonify(user)

@app.route('/manage/total/<station>')
def total_manage(station):
    station_ = Parking_manage.query.filter_by(Id=station).first()
    total = {}
    if station_.deposit_amount:
        total['deposit'] = int(station_.deposit_amount)
    else:
        total['deposit'] = 0
    total['price'] = int(station_.parking_price)
    total['vcard_type'] = station_.vcard_type
    total['line_name'] = station_.line_name
    return jsonify(total)


@app.route('/manage/station')
def station_manage():
    station = [{'name': '', 'id': 0}]
    for i in Parking_manage.query.filter(Parking_manage.parking_status=='active').all():
        dict1 = {}
        dict1['name'] = i.parking_name
        dict1['id'] = i.Id
        station.append(dict1)
    all_data = {}
    all_data['station'] = station
    all_data['verify_status'] = [
        {'name':'','id':''},
        {'name':'ผ่านการตรวจสอบ','id':'1'},
        {'name':'ไม่ผ่านการตรวจสอบ','id':'2'},
        {'name':'รอจองคิว','id':'3'},
        {'name':'จองคิว','id':'4'},
        {'name':'ยกเลิก','id':'5'},]
    all_data['payment_name'] = [
        {'name':'','id':''},
        {'name':'เงินสด','id':'1'},
        {'name':'บัตรเครดิต','id':'2'},
    ]
    return jsonify(all_data)

@app.route('/manage/brand_name')
def brand():
    data = Brand.query.all()
    data_list = []
    for i in data:
        brand_d = {}
        brand_d['brand'] = i.brand_name
        data_list.append(brand_d)
    return jsonify(data_list)

@app.route('/manage/status/<id_>')
def status_log(id_):
    data = Parking_log.query.filter_by(card_id=id_).order_by(Parking_log.Id.desc()).first()
    json_data = {}
    if data.verify_status == '1':
        json_data['verify_status'] = 1
    elif data.verify_status == '2':
        json_data['verify_status'] = 2
    elif data.verify_status == '3':
        json_data['verify_status'] = 3
    elif data.verify_status == '4':
        json_data['verify_status'] = 4
    elif data.verify_status == '5':
        json_data['verify_status'] = 5
    else :
        json_data['verify_status'] = ''

    if data.payment_name == '1':
        json_data['payment_name'] = 1
    elif data.payment_name =='2':
        json_data['payment_name'] = 2
    else :
        json_data['payment_name'] = ''
    print(data.payment_name)
    print('-'*20)
    return jsonify(json_data)



@app.route('/manage/province')
def province_manage():
    province = get_province()
    return jsonify({'province': province})


@app.route('/manage/district/<province>')
def district_manage(province):
    if province == '':
        province = None
    district = get_district(province)
    return jsonify({'districtlist': district})


@app.route('/manage/subdistrict/<province>/<district>')
def subdistrict_manage(province,district):
    subdistrict = get_subdistrict(province,district)

    return jsonify({'subdistrictlist': subdistrict})


@app.route('/manage/postcode/<province>/<district>/<subdistrict>')
def postcode_manage(province,district,subdistrict):
    postcode = get_postcode(province,district,subdistrict)
    return jsonify({'postcodelist': postcode})


@app.route('/manage/test')
def test():
    resault = Parking_member.query.all()
    data = []
    for i in resault:
        station = {}
        station['id'] = i.Id
        station['first_name'] = i.first_name_th
        station['last_name'] = i.last_name_th
        station['phone'] = i.phone
        station['address_no'] = i.address_no
        station['village'] = i.village
        station['alley'] = i.alley
        station['street'] = i.street
        station['sub_district'] = i.sub_district
        station['district'] = i.district
        station['province'] = i.province
        station['parking_code'] = i.parking_code
        station['card_id'] = i.card_id
        station['parking_register_date'] = i.parking_register_date
        station['card_last_read_date'] = i.card_last_read_date
        station['card_expire_date'] = i.card_expire_date
        station['user_edit_date'] = i.user_edit_date
        station['user_edit'] = i.user_edit
        data.append(station)
    return jsonify(data)


@app.route('/manage/checkdupcard/<id_card>/<station>')
def check_card_id(id_card,station):
    parking_code = Parking_manage.query.filter_by(Id=station).first().parking_code
    card = Parking_member.query.filter_by(card_id=id_card).filter(Parking_member.parking_code == parking_code)\
        .filter(or_(Parking_member.card_status =='1',Parking_member.card_status==None)).first()
    print(card)
    if card :
        return jsonify({'status':'dup'})
    else:
        return jsonify({'status':'not dup'})

# Logout Manage
@app.route('/manage/logout')
def logout_manage():
    user_log = Login_logout_log.query.filter_by(user=session.get('username')).order_by(Login_logout_log.Id.desc()).first()
    user_log.logout_datetime = datetime.datetime.today()
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))

# สำหรับเพิ่ม report และกำหนด field จาก Database
@app.route('/manage/report')
def manage_report():
    # report 1
    cursor = mysql.connection.cursor()
    sqlreport = "select id, first_name, last_name, parking_name, parking_type_name, FORMAT(round(deposit_amount),0), FORMAT(round(amount),0), FORMAT(round(vat),0), FORMAT(round(total),0), card_id, invoice_no, receipt_no, payment_date, payment_name, input_type, transaction_type from parking_log "
    cursor.execute(sqlreport)
    row = cursor.fetchall()

    #สำหรับดึงข้อมูลลูกค้าด้วย email
    # cursor = mysql.connection.cursor()
    # sqlreport = "select pl.id, pl.first_name, pl.last_name, pl.parking_name, pl.parking_type_name, FORMAT(round(pl.deposit_amount),0), FORMAT(round(pl.amount),0), FORMAT(round(pl.vat),0), FORMAT(round(pl.total),0), pl.card_id, pl.invoice_no, pl.receipt_no, pl.payment_date, pl.payment_name, pl.input_type, pl.transaction_type, cr.identity_card, cr.email from parking_log as pl INNER JOIN customer_register as cr ON pl.identity_card=cr.identity_card"
    # cursor.execute(sqlreport)
    # row = cursor.fetchall()
    #print(row)
    
    

    # report 2
    cursor2 = mysql.connection.cursor()
    sqlreport2 = "select id, first_name, last_name, username, password, user_create_date, user_edit_date, user_create, user_edit from user_manage"
    cursor2.execute(sqlreport2)
    row2 = cursor2.fetchall()
    mysql.connection.commit()
    # cursor.close()
    print(len(row))
    print(len(row2))
    return render_template('manage/manage-report.html', datas=row, datas2=row2)

# Update เลขที่ใบกำกับภาษีเต็มรูป
@app.route('/manage/update_receiptno',methods=['POST'])
def update_receiptno():
    id_ = request.form.get('id')
    print(id_)
    receipt_no = request.form.get('receipt')
    print(receipt_no)
    update_log = Parking_log.query.filter_by(Id = id_).first()
    update_log.receipt_no = receipt_no
    db.session.commit()
    print('success')
    return 'SUCCESS'

@app.route('/manage/update_address_type',methods=['POSt'])
def update_address_type():
    id_ = request.form.get('id')
    print(id_)
    address_type = request.form.get('address_type')
    deposit_address_type = request.form.get('deposit_address_type')
    update_log = Parking_log.query.filter_by(Id=id_).first()
    if address_type not in ['',' ',None]:
        update_log.address_type = address_type
    if deposit_address_type not in ['',' ',None]:
        update_log.deposit_address_type = deposit_address_type
    db.session.commit()
    return 'SUCCESS'

def paymentName(type):
    if type == '1':
        return 'เงินสด'
    elif type == '2':
        return 'บัตรเครดิต'
    elif type == '3':
        return 'Qr code'
    elif type == '4':
        return 'ผูกบัญชี'
    elif type == '5':
        return 'เช็ค'
    else:
        return 'ยังไม่ได้ระบุการชำระเงิน'

@app.route('/tableReserve_cus', methods=['POST'])
def tableRecerve_cus():
    data = request.get_json().split(',')
    line = data[0]
    park = data[1]
    parking = Parking_manage.query.filter_by(reserve_status = "active").all()
    parking_list = []
    for i in parking:
        parking_list.append(i.parking_name)

    res=[]
    if line == 'ทั้งหมด':
        parking_log = Parking_log.query.filter(Parking_log.transaction_type == '4').order_by(Parking_log.Id.desc()).all()

    elif  line == 'สายสีเขียว' and park == 'ทั้งหมด':
        parking_log = Parking_log.query.filter(Parking_log.transaction_type == '4').order_by(Parking_log.Id.desc()).all()

    elif park in parking_list:
        parking_log = Parking_log.query.filter((Parking_log.transaction_type == '4')&\
            (Parking_log.parking_name == park)).order_by(Parking_log.Id.desc()).all() 

    else:
        return json.dumps(res)

    for i,row in enumerate(parking_log):
        user = {}
        user['no'] = i+1
        user['date'] = str(row.parking_reserve_date)
        user['firstname'] = row.first_name
        user['lastname'] = row.last_name
        user['phone'] = row.phone
        user['station'] = row.parking_name
        user['total'] = str(row.total)
        user['payment_name'] = paymentName(row.payment_name)
        user['reserve_by'] = 'app'
        user['payment_status'] = 'ชำระแล้ว' if row.payment_status == '1' else 'ยังไม่ได้ชำระ'
        user['payment_date'] = str(row.payment_date)
        user['qr_code_exprie'] = str(row.qr_code_exprie)
        user['id'] = str(row.Id)
        res.append(user)

    return json.dumps(res)

@app.route('/change-address', methods=['POST'])
def change_address():
    data = request.get_json()
    log = Parking_log.query.filter_by(Id = int(data['id'])).first()
    log.address_type = data['address_type']
    db.session.commit()
    # print(type(data['id']))
    return 'success'

# =========== Jirameth - Add on date 11-07-2023 ===========
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

@app.route('/manage/cud_holiday_settings', methods=['POST', 'DELETE', 'PATCH'])
def cud_holiday_settings():
    try:
        if request.method == 'POST':
            holiday = {}
            data = request.get_json()
            if data is None:
                return jsonify(error='Invalid JSON data'), 400
            holiday['description'] = data['description']
            holiday['holiday_date'] = data['holidayDate']
            holiday['parking_name'] = data['parkingSelect']
            with mysql.connection.cursor() as cursor:
                cursor.execute("insert into `holiday_settings` (`description`,`holiday_date`,`parking_name`) values('{}', '{}', '{}')".format(holiday['description'], holiday['holiday_date'], holiday['parking_name']))
                mysql.connection.commit()

            return jsonify(success=True)
        if request.method == 'DELETE':
            data = request.get_json()
            holidaySettingId = data['holidaySettingsId']  # Update the variable name to match the JavaScript code
            with mysql.connection.cursor() as cursor:
                # Delete the row from the holiday_settings table based on holidaySettingId
                cursor.execute("DELETE FROM `holiday_settings` WHERE `holiday_settings_id` = '{}'".format(holidaySettingId))
                mysql.connection.commit()

            return jsonify(success=True)
        if request.method == 'PATCH':
            data = request.get_json()

            # Extract the fields to be updated
            holidaySettingId = data['holidaySettingsId']
            description = data['description']
            holidayDate = data['holidayDate']

            with mysql.connection.cursor() as cursor:
                cursor.execute("""
                UPDATE holiday_settings
                    SET description = '{}', holiday_date = '{}'
                WHERE holiday_settings_id = '{}'
                """.format(description, holidayDate, holidaySettingId))
                mysql.connection.commit()

            return jsonify(success=True)
    except Exception as e:
        return jsonify(error="An error occurred while inserting the holiday settings"), 500

@app.route('/manage/holiday_settings', methods=['GET', 'POST'])
def holiday_settings():
    # Access the search parameters using the keys in search_data dictionary
    filters={};
    try:
        if request.method == 'POST':
            data = request.get_json()
            if data is None:
                return jsonify(error='Invalid JSON data'), 400
            filters['year'] = data['yearSelect']
            filters['parking_name'] = data['parkingSelect']
        elif request.method == 'GET':
            year = datetime.datetime.now().strftime("%Y")
            filters['year'] = year
            filters['parking_name'] = 'All'
    except:
        print("Error in member_info_report function.")

    whereStr = ''
    if filters:
        if filters['year']:
            whereStr += "\nand year(holiday_date) = '%s'" % filters['year']
        if filters['parking_name']:
            if filters['parking_name'] != 'All':
                whereStr += "\nand parking_name = '%s'" % filters['parking_name']

    cursor = mysql.connection.cursor()
    cursor.execute("""
    select
        holiday_settings_id as holidaySettingsId,
        description,
        holiday_date as holidayDate
    from holiday_settings
    where holiday_settings_id is not null{}
    order by holiday_date asc
    """.format(whereStr))
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result = [dict(zip(columns, row)) for row in data]
    json_data = json.dumps(result, ensure_ascii=False, cls=CustomJSONEncoder)
    encoded_data = urllib.parse.quote(json_data)
    if request.method == 'POST':
        return jsonify(encode_data=encoded_data)
    return render_template('/manage/settings/holiday-settings.html', data=encoded_data)

@app.route('/manage/member_info_report', methods=['GET', 'POST'])
def member_info_report():
    # Access the search parameters using the keys in search_data dictionary
    filters={};
    try:
        if request.method == 'POST':
            data = request.get_json()
            if data is None:
                return jsonify(error='Invalid JSON data'), 400
            filters['line'] = data['lineSelect']
            filters['parking_name'] = data['parkingSelect']
            filters['visitor_type'] = data['customerTypeSelect']
            filters['from_date'] = data['fromDate']
            filters['to_date'] = data['toDate']
        elif request.method == 'GET':
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            minusOneMonthDate = (datetime.datetime.now() - relativedelta(months=1)).strftime("%Y-%m-%d")
            filters = {
                'line': "All",
                'parking_name': 'All',
                'visitor_type': 'All',
                'from_date': minusOneMonthDate,
                'to_date': today,
            }
    except:
        print("Error in member_info_report function.")
    print("Filters: {}".format(filters))

    whereStr = ''
    if filters:
        if 'line' in filters:
            if filters['line'] != 'All':
                whereStr += "\nand pmang.line_name = '%s'" % filters['line']
        if 'parking_name' in filters:
            if filters['parking_name'] != 'All':
                whereStr += "\nand pmang.parking_name = '%s'" % filters['parking_name']
        if 'visitor_type' in filters:
            if filters['visitor_type'] == 'Visitor':
                whereStr += "\nand pmem.id IS NULL"
            elif filters['visitor_type'] == 'Member':
                whereStr += "\nand pmem.id IS NOT NULL"
        if 'from_date' in filters or 'to_date' in filters:
            if 'from_date' in filters and 'to_date' in filters:
                whereStr += "\nand DATE(pm.parking_register_date) between '%s' and '%s'" % (filters['from_date'], filters['to_date'])
            elif 'from_date' in filters and 'to_date' not in filters:
                whereStr += "\nand DATE(pm.parking_register_date) between '%s' and '%s'" % (filters['from_date'], filters['from_date'])
            else:
                whereStr += "\nand DATE(pm.parking_register_date) between '%s' and '%s'" % (filters['to_date'], filters['to_date'])
    print("Where Condition: {}".format(whereStr))

    cursor = mysql.connection.cursor()
    cursor.execute("""
    select 
        CAST(pm.id as CHAR) as 'member_id',
        '-' as 'card_type',
        pm.card_id as 'card_no',
        "รถยนต์" as 'vehicle_type',
        case
        	when pm.license_plate2 is not null and pm.license_plate2 != '' then concat(pm.license_plate1, ', ', pm.license_plate2)
        	else pm.license_plate1
        end as 'license_plate',
        pm.first_name_th as 'first_name',
        pm.last_name_th as 'last_name',
        IFNULL(DATE(pm.parking_register_date), '-') as 'card_start_date',
        IFNULL(pm.card_expire_date, '-') as "card_end_date",
        '-' as 'remark'
    from parking_member pm
    left join parking_manage pmang
        on pm.parking_code = pmang.parking_code
    where pm.id is not null{}
    order by DATE(pm.parking_register_date) desc
    """.format(whereStr))
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result = [dict(zip(columns, row)) for row in data]
    json_data = json.dumps(result, ensure_ascii=False)
    encoded_data = urllib.parse.quote(json_data)
    if request.method == 'POST':
        return jsonify(encode_data=encoded_data)
    return render_template('/manage/reports/member-info-report.html', data=encoded_data)

@app.route('/manage/income_summary_report', methods=['GET', 'POST'])
def income_summary_report():
   # Access the search parameters using the keys in search_data dictionary
    filters = {};
    try:
        if request.method == 'POST':
            data = request.get_json()
            if data is None:
                return jsonify(error='Invalid JSON data'), 400
            filters['line'] = data['lineSelect']
            filters['parking_name'] = data['parkingSelect']
            filters['from_date'] = data['fromDate']
            filters['to_date'] = data['toDate']
        elif request.method == 'GET':
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            minusOneMonthDate = (datetime.datetime.now() - relativedelta(months=1)).strftime("%Y-%m-%d")
            filters = {
                'line': "All",
                'parking_name': 'All',
                'from_date': minusOneMonthDate,
                'to_date': today,
            }
    except:
        print("Error in income_summary_report function.")

    print("Filters: {}".format(filters))

    whereStr = ''
    if filters:
        if 'line' in filters:
            if filters['line'] != 'All':
                whereStr += "\nand pm.line_name = '%s'" % filters['line']
        if 'parking_name' in filters:
            if filters['parking_name'] != 'All':
                whereStr += "\nand pm.parking_name = '%s'" % filters['parking_name']
        if 'from_date' in filters or 'to_date' in filters:
            if 'from_date' in filters and 'to_date' in filters:
                whereStr += "\nand pl.payment_date between '%s' and '%s'" % (filters['from_date'], filters['to_date'])
            elif 'from_date' in filters and 'to_date' not in filters:
                whereStr += "\nand pl.payment_date between '%s' and '%s'" % (filters['from_date'], filters['from_date'])
            else:
                whereStr += "\nand pl.payment_date between '%s' and '%s'" % (filters['to_date'], filters['to_date'])

    print("Where Condition: {}".format(whereStr))

    cursor = mysql.connection.cursor()
    cursor.execute("""
    select 
        IFNULL(bd.payment_date, '-') as payment_date,
        (case 
            when DAYNAME(bd.payment_date) = 'Sunday' then 'วันอาทิตย์'
            when DAYNAME(bd.payment_date) = 'Monday' then 'วันจันทร์'
            when DAYNAME(bd.payment_date) = 'Tuesday' then 'วันอังคาร'
            when DAYNAME(bd.payment_date) = 'Wednesday' then 'วันพุธ'
            when DAYNAME(bd.payment_date) = 'Thursday' then 'วันพฤหัสบดี'
            when DAYNAME(bd.payment_date) = 'Friday' then 'วันศุกร์'
            else 'วันเสาร์'
        end
        ) as payment_day_name,
        (select ifnull(sum(total), 0) from parking_log where cast(payment_date as DATE) = bd.payment_date and payment_name = 1 and ifnull(fine, 0) = 0) as 'cash',
        (select ifnull(sum(total), 0) from parking_log where cast(payment_date as DATE) = bd.payment_date and payment_name = 3 and ifnull(fine, 0) = 0) as 'qr_code',
        (select ifnull(sum(total), 0) from parking_log where cast(payment_date as DATE) = bd.payment_date and payment_name = 2 and ifnull(fine, 0) = 0) as 'cr',
        (select ifnull(sum(total), 0) from parking_log where cast(payment_date as DATE) = bd.payment_date and payment_name = 4 and ifnull(fine, 0) = 0) as 'ktb_bank',
        (select ifnull(sum(total), 0) from parking_log where cast(payment_date as DATE) = bd.payment_date and payment_name = 5 and ifnull(fine, 0) = 0) as 'cheque',
        (select ifnull(sum(total), 0) from parking_log where cast(payment_date as DATE) = bd.payment_date) as 'total',
        (select ifnull(sum(fine), 0) from parking_log where cast(payment_date as DATE) = bd.payment_date and ifnull(fine, 0) > 0) as 'fine'
    from (
    select 
        CAST(pl.payment_date AS DATE) AS payment_date
    from parking_log pl
    left join parking_manage pm 
    	on pl.parking_code = pm.parking_code
    where pl.payment_status = 1
    and pl.payment_date is not null{}
    group by CAST(pl.payment_date AS DATE)
    ) bd
    order by bd.payment_date desc
    """.format(whereStr))
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result = [dict(zip(columns, row)) for row in data]
    json_data = json.dumps(result, ensure_ascii=False)
    encoded_data = urllib.parse.quote(json_data)
    if request.method == 'POST':
        return jsonify(encode_data=encoded_data)
    return render_template('/manage/reports/income-summary-report.html', data=encoded_data)

@app.route('/manage/car_in_out_report', methods=['GET', 'POST'])
def car_in_out_report():
    # Access the search parameters using the keys in search_data dictionary
    filters={};
    try:
        print("request method name: " + request.method)
        if request.method == 'POST':
            data = request.get_json()
            if data is None:
                return jsonify(error='Invalid JSON data'), 400
            filters['line'] = data['lineSelect']
            filters['parking_name'] = data['parkingSelect']
            filters['visitor_type'] = data['customerTypeSelect']
            filters['period'] = data['periodSelect']
            filters['from_date'] = data['fromDate']
            filters['to_date'] = data['toDate']
            filters['from_time'] = data['fromTime']
            filters['to_time'] = data['toTime']
        elif request.method == 'GET':
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            minusOneMonthDate = (datetime.datetime.now() - relativedelta(months=1)).strftime("%Y-%m-%d")
            filters = {
                'line': "All",
                'parking_name': 'All',
                'visitor_type': 'All',
                'period': 'All',
                'from_date': minusOneMonthDate,
                'to_date': today,
                'from_time': '09:00',
                'to_time': '18:00',
            }
    except:
        print("Error in car_in_out_report function.")

    print(filters)

    whereStr = ''
    joinStr = ''
    if filters:
        if 'line' in filters:
            if filters['line'] != 'All':
                whereStr += "\nand pm.line_name = '%s'" % filters['line']
        if 'parking_name' in filters:
            if filters['parking_name'] != 'All':
                whereStr += "\nand pm.parking_name = '%s'" % filters['parking_name']
        if 'visitor_type' in filters:
            if filters['visitor_type'] == 'Visitor':
                whereStr += "\nand pmem.id IS NULL"
            elif filters['visitor_type'] == 'Member':
                whereStr += "\nand pmem.id IS NOT NULL"
        if 'period' in filters:
            if filters['period'] == 'วันทำการ':
                whereStr += '\nand hs.holiday_date is null'
            if filters['period'] == 'วันหยุดนักขัตฤกษ์':
                whereStr += '\nand hs.holiday_date is not null'
            if filters['period'] == 'วันเสาร์-อาทิตย์':
                whereStr += "\nand (DAYOFWEEK(plv.time_in) = 1 OR DAYOFWEEK(plv.time_in) = 7)"
        if 'from_date' in filters or 'to_date' in filters:
            if 'from_date' in filters and 'to_date' in filters:
                whereStr += "\nand plv.time_in between '%s' and '%s'" % (filters['from_date'], filters['to_date'])
            elif 'from_date' in filters and 'to_date' not in filters:
                whereStr += "\nand plv.time_in between '%s' and '%s'" % (filters['from_date'], filters['from_date'])
            else:
                whereStr += "\nand plv.time_in between '%s' and '%s'" % (filters['to_date'], filters['to_date'])
        if 'from_time' in filters or 'to_time' in filters:
            if 'from_time' in filters and 'to_time' in filters:
                whereStr += "\nand TIME(plv.time_in) between '%s' and '%s'" % (filters['from_time'], filters['to_time'])
            elif 'from_time' in filters and 'to_time' not in filters:
                whereStr += "\nand TIME(plv.time_in) between '%s' and '%s'" % (filters['from_time'], filters['from_time'])
            else:
                whereStr += "\nand TIME(plv.time_in) between '%s' and '%s'" % (filters['to_time'], filters['to_time'])

    cursor = mysql.connection.cursor()
    cursor.execute("""
    select
        plv.id as 'tran_id',
        (case when pmem.id is not null then 'MEMBER'
        else 'VISITOR' end) as 'card_type',
        "รถยนต์" as 'vehicle_type',
        IFNULL(pmem.card_id, '-') as 'card_id',
        IFNULL(plv.license_plate, '-') as 'license_plate_no',
        "-" as 'payment_type',
        IFNULL(plv.time_in, "-") as 'time_in',
	    IFNULL(plv.time_out, "-") as 'time_out',
        DATE_FORMAT(timediff(ifnull(plv.time_out, now()), plv.time_in), '%T') as 'parking_time',
        (case when plv.estamp is not null then 'ใช้บริการรถไฟฟ้า'
            else 'ไม่ใช้บริการรถไฟฟ้า' end) as 'visitor_type'
    from parking_logvisitor plv
    left join parking_manage pm
        on plv.parking_code = pm.parking_code
    left join parking_member pmem
        on plv.license_plate in (pmem.license_plate1, pmem.license_plate2) and plv.parking_code = pmem.parking_code
    left join holiday_settings hs
    	on pm.parking_name = hs.parking_name and date(plv.time_in) = hs.holiday_date
    where plv.type = 1{}
    order by plv.time_in DESC""".format(whereStr))
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result = [dict(zip(columns, row)) for row in data]
    json_data = json.dumps(result, ensure_ascii=False)
    encoded_data = urllib.parse.quote(json_data)
    if request.method == 'POST':
        return jsonify(encode_data=encoded_data)
    return render_template('/manage/reports/car-in-out-report.html', data=encoded_data)

# =========== Jirameth - Add on date 11-07-2023 ===========

if __name__ == '__main__':
    app.run(debug=True)
