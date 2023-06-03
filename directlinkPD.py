
from nturl2path import url2pathname
from flask import Flask,request, make_response ,json
from renewTAFF import renew_card_TAFF_orAll
from db_config import mysql
from app import app,Parking_log, Parking_manage, Parking_member, db
import datetime
import base64
from updatecapacity import capacity_count
import multiprocessing as mp
from getReserveParking import qr_opengate_timeout
from db_config import mysql 
from user_owned_card import checkCardNotRandom, checkCardNotReMem
from apiMember import ApiMember
from threading import Thread
from updatecapacity import genday 


user = 'ktb'
password = 'Mrta6146*'
comCode = '98426'
st_userPass = user+':'+password
_bytes = st_userPass.encode('ascii')
base64_bytes = base64.b64encode(_bytes)
base64_ = base64_bytes.decode('ascii')

headers = {
  'Authorization': 'Basic '+base64_,
  'Content-Type': 'application/json'
}

print(base64_)
print(headers.get('Authorization'))

def getDirectlink_pd():
    print('******************getDirectlink_pd***************************')
    print(request.json)
    if request.headers['Authorization'] == headers.get('Authorization') and request.json['comCode'] == comCode:
        amount = request.json['amount']
        ref1 = request.json['ref1']
        ref2 = request.json['ref2']
        if request.json['command'] == 'Approval': #ตรวจสอบ จำนวนเงินและสถานะการจ่าย จากนั้นอัปเดตสถานะ Approval
            #print(1)
            response = approval(amount,ref2,ref1)
        elif request.json['command'] == 'Payment': #ตรวจสอบสถานะการ Approval, สถานะpayment ก่อน จากนั้นค่อยให้ทำรายการชำระได้ เปลี่ยนสถานะการชำระ เป็นชำระแล้ว
            #print(2)
            response = payment(amount,ref2,ref1)

        return response


    return make_response('could not verify',  401, {'parking.mrta.co.th': 'Basic realm: "login required"'})

def approval(amount,ref2,ref1):
    today = datetime.datetime.now().date()
    cursor = mysql.connection.cursor()
    query = "select id,total,payment_status,lastdate_pay,parking_reserve_date,transaction_type from parking_log where identity_card = %s AND orderNumber = %s"
    val = (ref1,ref2)
    cursor.execute(query,val)
    result = cursor.fetchone()
    print(result)
    print("***************************appr***********************")
    if result:
     id = result[0]
     amountDB = result[1]
     paymentStatus = result[2]
     lastdate_pay = result[3]
     parking_reserve_date = result[4]
     transaction_type = result[5]
     
     if transaction_type == '4':
        timeout = (datetime.datetime.now()-parking_reserve_date).total_seconds() / 60
        print(timeout)
        if timeout >= 10:
              #print(''*40,'transaction=4','-'*40)
              data = {
              'tranxId': id,
              'bankRef': request.json['bankRef'],
              'respCode': '999',
              'respMsg': 'Transacti on is expired',
              'balance': amount
              }
          
              response = app.response_class(
                response = json.dumps(data),
                mimetype='application/json'
                )
              return response
   
     if amount == amountDB and (paymentStatus is None or paymentStatus == '0'): 
        if lastdate_pay is None or (today<=lastdate_pay):
      
          update_approval_status(ref2)
     
          data = {
            'tranxId': id,
            'bankRef': request.json['bankRef'],
            'respCode': '0',
            'respMsg': 'Successful',
            'balance': amount
          }
          
          response = app.response_class(
            response = json.dumps(data),
            mimetype='application/json'
         )
        else:
            print("h")
            data = {
            'tranxId': id,
            'bankRef': request.json['bankRef'],
            'respCode': '999',
            'respMsg': 'Transaction is expired',
            'balance': amount
          }
            response = app.response_class(
              response = json.dumps(data),
               mimetype='application/json'
          )
        
     elif amount != amountDB :
        data = {
          'tranxId': id,
          'bankRef': request.json['bankRef'],
          'respCode': '108',
          'respMsg': 'Invalid price or amount',
          'balance': amount
        }
        response = app.response_class(
        	response = json.dumps(data),
	      	mimetype='application/json'
       )
     elif amount == amountDB and paymentStatus == '1':
        data = {
          'tranxId': id,
          'bankRef': request.json['bankRef'],
          'respCode': '106',
          'respMsg': 'Transaction number duplicate',
          'balance': amount
        }
        response = app.response_class(
        	response = json.dumps(data),
	      	mimetype='application/json'
       )
    else:
        #000000 หาข้อมูลไม่เจอ
        data = {
          'tranxId': '000000',
          'bankRef': request.json['bankRef'],
          'respCode': '104',
          'respMsg': 'Invalid reference'
        }
        response = app.response_class(
        	response = json.dumps(data),
	      	mimetype='application/json'
       )	

    return response

def payment(amount,ref2,ref1):
    today = datetime.datetime.now().date()
    cursor = mysql.connection.cursor()
    query = "select id,total,payment_status,approval_status,lastdate_pay,parking_type_name,card_id,month,identity_card,parking_code from parking_log  where identity_card = %s AND orderNumber = %s"
    val = (ref1,ref2)
    cursor.execute(query,val)
    result = cursor.fetchone()
    if result:
     id = result[0]
     amountDB = result[1]
     paymentStatus = result[2]
     approval_status = result[3]
     lastdate_pay = result[4]
     typeCard=  result[5]
     cid = result[6]
     count_month=result[7]
     identity_card = result[8]
     parking_code = result[9]
     if amount == amountDB and (paymentStatus is None or paymentStatus == '0'): 
       if lastdate_pay is None or (today<=lastdate_pay):
          print('**********if payment is None*******')
          update_payment_status(ref2,parking_code)
          renew_card_TAFF_orAll(cid,count_month,'0',identity_card,parking_code)
          data = {
            'tranxId': id,
            'bankRef': request.json['bankRef'],
            'respCode': '0',
            'respMsg': 'Successful',
            'balance': amount
          }
          response = app.response_class(
            response = json.dumps(data),
            mimetype='application/json'
          )
       else:
            data = {
            'tranxId': id,
            'bankRef': request.json['bankRef'],
            'respCode': '999',
            'respMsg': 'Transaction is expired',
            'balance': amount
          }
            response = app.response_class(
              response = json.dumps(data),
               mimetype='application/json'
          )
     elif amount != amountDB :
        data = {
          'tranxId': id,
          'bankRef': request.json['bankRef'],
          'respCode': '108',
          'respMsg': 'Invalid price or amount',
          'balance': amount
        }
        response = app.response_class(
    	    response = json.dumps(data),
		      mimetype='application/json'
       )
     elif amount == amountDB and paymentStatus == '1':
        data = {
          'tranxId': id,
          'bankRef': request.json['bankRef'],
          'respCode': '106',
          'respMsg': 'Transaction number duplicate',
          'balance': amount
        }
        response = app.response_class(
    	    response = json.dumps(data),
		      mimetype='application/json'
       )
 
     else:
        data = {
          'tranxId': id,
          'bankRef': request.json['bankRef'],
          'respCode': '0',
          'respMsg': 'Successful',
          'balance': amount
        }
        response = app.response_class(
    	    response = json.dumps(data),
		      mimetype='application/json'
       )	
    else:
        #000000 หาข้อมูลไม่เจอ
        data = {
          'tranxId': '000000',
          'bankRef': request.json['bankRef'],
          'respCode': '104',
          'respMsg': 'Invalid reference'
        }
        response = app.response_class(
    	    response = json.dumps(data),
		      mimetype='application/json'
       )	

    return response


def update_payment_status(orderNumber,parking_code):
    log_update = Parking_log.query.filter_by(orderNumber=orderNumber).first()
    log_update.payment_status = '1'
    log_update.payment_name = '3'
    log_update.payment_date = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    log_update.comments = 'directlinkPD'+ ' ' + datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    db.session.commit()
    # cursor = mysql.connection.cursor()
    # sql = "UPDATE parking_log SET payment_status = %s,payment_name='3',payment_date=%s WHERE orderNumber = %s"
    # val = ('1',today,orderNumber)
    # cursor.execute(sql, val)
    # mysql.connection.commit()
    id_ = Parking_log.query.filter_by(orderNumber=orderNumber).first().Id
    
    capacity_count(parking_code,id_)

    if log_update.transaction_type == "4":
      print("transaction_type == 4")
      reserve_checkin_period = int(Parking_manage.query.filter_by(parking_name=log_update.parking_name).first(
        ).reserve_checkin_period)
      log_update.qr_show_exp = log_update.payment_date  + datetime.timedelta(days=1)
      log_update.qr_code_exprie = log_update.payment_date + datetime.timedelta(minutes=reserve_checkin_period)
      db.session.commit() 
      if(__name__=='directlink'):
        sec = 60*reserve_checkin_period
        p = mp.Process(target=qr_opengate_timeout, args=(orderNumber,sec,))
        p.start()
    elif log_update.transaction_type in ['1','2']:
      print('*******api Member*********')
      card_id = log_update.card_id
      mem = Parking_member.query.filter_by(card_id=card_id)\
          .filter(Parking_member.parking_code == log_update.parking_code).first()
      service = log_update.service_start_date
      card_expire_date = service + datetime.timedelta(genday(int(log_update.month),service.strftime('%Y-%m-%d')))
      print('*********',card_expire_date)
      data = {
              "parking_code": log_update.parking_code,    
              "first_name": log_update.first_name,
              "last_name": log_update.last_name,
              "card_id": card_id,
              "license_plate1": mem.license_plate1,
              "license_plate2": mem.license_plate2,
              "card_expire_date": card_expire_date,
              "service_start_date": log_update.service_start_date,
          }
      api = ApiMember(data)
      api.from_orm(mem)
      if log_update.transaction_type == "1":
          true_card_id = checkCardNotRandom(card_id)
          not_re_mem = checkCardNotReMem(log_update)
          print('true card id: ',true_card_id)
          if true_card_id:
              if not_re_mem:
                  res = api.request_insert()[1]
                  if res == 404:
                      update_token_thread = Thread(target=api.try_to_request,args=('insert',))
                      update_token_thread.start()
              else:
                  res = api.request_update()[1]
                  if res == 404:
                      update_token_thread = Thread(target=api.try_to_request,args=('update',))
                      update_token_thread.start()
      elif log_update.transaction_type == "2":
          res = api.request_update()[1]
          if res == 404:
              update_token_thread = Thread(target=api.try_to_request,args=('update',))
              update_token_thread.start()
    return "update pay"

def update_approval_status(orderNumber):
    cursor = mysql.connection.cursor()
    sql = "UPDATE parking_log SET approval_status = %s WHERE orderNumber = %s"
    val = ('done',orderNumber)
    cursor.execute(sql, val)
    mysql.connection.commit()
    return "update appov"

#update_payment_status('REVN10130000006886','N1013')
