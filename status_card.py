def status_card(verify_status):
    if verify_status == '1':
        return 'ผ่านการตรวจสอบ'
    elif verify_status == '2':
        return 'ไม่ผ่านการตรวจสอบ'
    elif verify_status == '3':
        return 'รอจองคิว'
    elif verify_status == '4':
        return 'จองคิว'
    elif verify_status == '5':
        return 'ยกเลิก'
    elif verify_status == '6':
        return 'รอให้คิว'
    else:
        return 'กำลังตรวจสอบข้อมูล'

def status_card_en(verify_status):
    if verify_status == '1':
        return 'Passed inspection'
    elif verify_status == '2':
        return 'Not passed'
    elif verify_status == '3':
        return 'waiting for reservation'
    elif verify_status == '4':
        return 'Reservation'
    elif verify_status == '5':
        return 'Cancel'
    else:
        return 'Checking information'