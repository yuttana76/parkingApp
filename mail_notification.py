from app import db,Parking_log,Customer_register,Message_box,mail
from flask_mail import Message
from datetime import datetime,date

def change_verify_status_notification(verify_status:str,id:int) -> None:
    try:
        log = Parking_log.query.filter_by(Id=id).first()
        customer = Customer_register.query.filter_by(identity_card = log.identity_card).first()
        if customer:
            msg = Message('Notification Email',sender='parkandride@mrta.co.th',recipients=[customer.email])
            body = ''
            if verify_status == 'ผ่านการตรวจสอบ':
                body = f'เรียนคุณ {customer.first_name} {customer.last_name} \n'
                body += f'\t\t รหัสบัตร {log.card_id} ได้รับสถานะ "ผ่านการตรวจสอบ" รบกวนคุณ {customer.first_name} ชำระค่าบริการที่เมนู "ข้อมูลสมาชิกรายเดือน" และกดปุ่ม "ชำระเงิน" ด้วยค่ะ\n'
            elif verify_status == 'ไม่ผ่านการตรวจสอบ':
                body = f'เรียนคุณ {customer.first_name} {customer.last_name} \n'
                body += f'\t\t รหัสบัตร {log.card_id} ได้รับสถานะ "ไม่ผ่านการตรวจสอบ" รบกวนตรวจสอบข้อมูลที่เมนู "ข้อมูลผู้ใช้งาน" เพื่อ update แก้ไขข้อมูลส่วนตัวให้ถูกต้อง ด้วยค่ะ\n'
            elif verify_status == 'รอจองคิว':
                body = f'เรียนคุณ {customer.first_name} {customer.last_name} \n'
                body += f'\t\t รหัสบัตร {log.card_id} ได้รับสถานะ "รอจองคิว" รบกวนคุณ {customer.first_name} กดปุ่มจองคิวที่เมนู "ข้อมูลสมาชิกรายเดือน" และ กดปุ่ม "จองคิว" ด้วยค่ะ\n'   
            elif verify_status == 'ยกเลิก':
                body = f'เรียนคุณ {customer.first_name} {customer.last_name} \n'
                body += f'\t\t รหัสบัตร {log.card_id} ได้รับสถานะ "ยกเลิก" ค่ะ\n'   
            if body != '':
                notification = Message_box(identity_card=log.identity_card,card_id=log.card_id,des_noti=body,date=date.today())
                db.session.add(notification)
                db.session.commit()
                msg.body = body
                mail.send(msg)
    except Exception as e:
        print('send main notification fail')
        print(e.with_traceback())
        pass 