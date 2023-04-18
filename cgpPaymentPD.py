import requests,datetime
from flask import session
import xml.etree.ElementTree as ET
from db_config import mysql

bundle="C:/D/certFor_CGP_payment/production/ca_cert.pem"
client_key = "C:/D/certFor_CGP_payment/production/clientws1.pem"
client_cer = "C:/D/certFor_CGP_payment/production/clientws1.cer"
url = "https://ws1.ktb.co.th/CGPAppWeb/"


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

def paymentCGP_PD(ref1,total,ref2,payRef): #payRef gen from term_seq gen ใหม่ทุกครั้งที่ทำรายการ
     cursor = mysql.connection.cursor()
     sql = "SELECT accountNumber FROM account_number_ktb WHERE identity_card = %s AND accountStatus = %s"
     val = (ref1,"Active")
     cursor.execute(sql, val)
     result = cursor.fetchone()
     ac_ref = result[0]
     amount = total

     x = datetime.datetime.today()
     now = x.time()
     format = '%H:%M:%S' # The format
     time_cutoff = '23:00:00' #uat
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
     params = {"ac_ref": ac_ref, "amount": amount, "cust_id": ref1, "db_ac_curr_code": "THB", "db_bank_code": "006", "isp_id": "98427", "pay_ref": payRef,"pay_service": "EPAYNET","ref1": ref1,"ref_date":today ,"resend_flag": resend_flag,"tran_sub_type": "M","tran_type": "01","vendor_id": "98427","ref2":ref2 }
     cert = (client_cer,client_key)
     response = requests.get(url, params=params,cert=cert,verify=bundle)
     encoded = (response.text).encode("utf8")
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
           
     update_status(code,ref2,x)
     if code == "IC000":
          return "Payment is Executed Successfully"
     else:
          return code




