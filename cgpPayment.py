import requests,datetime
from flask import session
import xml.etree.ElementTree as ET
from db_config import mysql
from find_log import find_last_log
from app import Parking_manage,Ktb_detail

cert_file_path = "C:/D/certFor_CGP_payment/clientuatws1.crt"
key_file_path = "C:/D/certFor_CGP_payment/clientuatws1_key.pem"
url = "https://uat-ws1.ktb.co.th/CGPAppWeb/"


def check_timeout(ref2):
     cursor = mysql.connection.cursor()
     sql = "SELECT error_payment FROM parking_log WHERE orderNumber = %s "
     val = (ref2,)
     cursor.execute(sql, val)
     result = cursor.fetchone()
     if result:
      code = result[0]
      if code == "PT002": #code Time out
           return "Y"
 
     return "N"

def update_status(code,ref2,today):
     cursor= mysql.connection.cursor()
     status = "0"
     if code == "IC000":
      status = "1"
      sql = "UPDATE parking_log SET error_payment= %s ,payment_status = %s,payment_date=%s WHERE orderNumber = %s"
      val = (code,status,today,ref2)
      cursor.execute(sql, val)
     else:
      sql = "UPDATE parking_log SET error_payment= %s ,payment_status = %s WHERE orderNumber = %s"
      val = (code,status,ref2)
      cursor.execute(sql, val)
     mysql.connection.commit()
     cursor.close()

def paymentCGP(ref1,total,ref2,payRef): #payRef gen from term_seq gen ใหม่ทุกครั้งที่ทำรายการ
     print("CGPPAYMENT",ref2)
     cursor = mysql.connection.cursor()
     sql = "SELECT accountNumber FROM account_number_ktb WHERE identity_card = %s AND accountStatus = %s"
     val = (ref1,"Active")
     cursor.execute(sql, val)
     result = cursor.fetchone()
     ac_ref = result[0]
     amount = total
     x = datetime.datetime.now()
     now = x.time()
     format = '%H:%M:%S' # The format
     time_cutoff = '17:00:00' #uat
     timeCutoff_str = datetime.datetime.strptime(time_cutoff, format)
     today = x.date()
     if now >= timeCutoff_str.time():
      tomorrow = x.date()+ datetime.timedelta(days=1)
      today = tomorrow

     today = today.strftime('%Y''%m''%d') #YYYYMMDD 
     resend_flag = check_timeout(ref2)
     # #######################################################################################
     # N” = Normal transaction 
     # หากมีการส่งค่า Payment Reference ชำระมาภายในวัน ระบบจะปฏิเสธการทํารายการ
     # นั้นด้วย Error EM001 Duplicate Request Payment Reference Number
     # “Y” = Resend transaction กรณี Time out
     #isp_id, vendor_id :ธนาคารกำหนดให้ 98427
     # ########################################################################################
     latest_log = find_last_log(ref1)[0]
     parking_code = latest_log.parking_code
     line = Parking_manage.query.filter_by(parking_code=parking_code).first().line_name
     ktb_detail = Ktb_detail.query.filter_by(line=line).first()
    
     transaction_type = latest_log.transaction_type
     terminal_id_dict = {
        '1': ktb_detail.tid_register,
        '2': ktb_detail.tid_renew,
        '4': ktb_detail.tid_reserve,
        '5': ktb_detail.tid_daily
     }
     terminal_id = terminal_id_dict.get(transaction_type)
     if not terminal_id:
        raise Exception('Invalid transaction type')
     params = {"ac_ref": ac_ref, "amount": amount, "cust_id": ref1, "db_ac_curr_code": "THB", "db_bank_code": "006", "isp_id": terminal_id, "pay_ref": payRef,"pay_service": "EPAYNET","ref1": ref1,"ref_date":today ,"resend_flag": resend_flag,"tran_sub_type": "M","tran_type": "01","vendor_id": terminal_id,"ref2":ref2 }
     cert = (cert_file_path, key_file_path)
     response = requests.get(url, params=params, cert=cert)
     encoded = (response.text).encode("utf8")
     print(response.status_code)
     print(response.text.encode('utf8'))
     print('response from cgp payment')
     root = ET.fromstring(encoded)
     for child in  root.iter():
      tag = child.tag[36:]
      if tag == "PAY_REF":
           pay_ref = child.text
      elif tag == "CUST_ID":
           cust_id = child.text
      elif tag == "REF1":
           ref1 = child.text
      elif tag == "REF2":
           ref2 = child.text
      elif tag == "AC_REF":
           ac_ref = child.text
      elif tag == "AMOUNT":
           amount = child.text
      elif tag == "RESEND_FLAG":
           resend_flag = child.text
      elif tag == "POST_DATE":
           date = child.text
      elif tag == "TRAN_TIME":
           time = child.text
      elif tag == "RSP_CODE":
           code = child.text
           print(code)
           
     update_status(code,ref2,x)
     if code == "IC000":
          return "Payment is Executed Successfully"
     else:
          return code




# KTB_PAY_RSP
# PAY_SERVICE
# TRAN_TYPE
# TRAN_SUB_TYPE
# PAY_REF
# KTB_REF
# VENDOR_ID
# ISP_ID
# CUST_ID
# REF1
# REF2
# DB_BANK_CODE
# DB_AC_CURR_CODE
# AC_REF
# AMOUNT
# RESEND_FLAG
# FEE
# POST_DATE
# TRAN_TIME
# RSP_CODE
# RSP_MSG

#<epay:RSP_CODE>EA001</epay:RSP_CODE>
#     <epay:RSP_MSG>Other Error from Backend System</epay:RSP_MSG>

# <epay:KTB_PAY_RSP xmlns:epay="http://kcs.com/cgp/xml/EpayNet.xsd">
#     <epay:PAY_SERVICE>EPAYNET</epay:PAY_SERVICE>
#     <epay:TRAN_TYPE>01</epay:TRAN_TYPE>
#     <epay:TRAN_SUB_TYPE>M</epay:TRAN_SUB_TYPE>
#     <epay:PAY_REF>46</epay:PAY_REF>
#     <epay:KTB_REF>0</epay:KTB_REF>
#     <epay:VENDOR_ID>21630</epay:VENDOR_ID>
#     <epay:ISP_ID>21630</epay:ISP_ID>
#     <epay:CUST_ID>620779</epay:CUST_ID>
#     <epay:REF1>ref1</epay:REF1>
#     <epay:REF2>ref2</epay:REF2>
#     <epay:REF3>ref3</epay:REF3>
#     <epay:DB_BANK_CODE>006</epay:DB_BANK_CODE>
#     <epay:DB_AC_CURR_CODE>THB</epay:DB_AC_CURR_CODE>
#     <epay:AC_REF>3286005355</epay:AC_REF>
#     <epay:AMOUNT>1.01</epay:AMOUNT>
#     <epay:RESEND_FLAG>Y</epay:RESEND_FLAG>
#     <epay:FEE>0</epay:FEE>
#     <epay:POST_DATE>20210705</epay:POST_DATE>
#     <epay:TRAN_TIME>13283401</epay:TRAN_TIME>
#     <epay:RSP_CODE>EA001</epay:RSP_CODE>
#     <epay:RSP_MSG>Other Error from Backend System</epay:RSP_MSG>
# </epay:KTB_PAY_RSP>