from app import Parking_log,Parking_member,Parking_manage
from sqlalchemy import or_
from pydantic import BaseModel
from typing import Optional
from datetime import date,datetime
import requests
import os
import traceback

class MemberData(BaseModel):
    Id: Optional[int]
    local_id: Optional[int]
    card_id: Optional[str]
    cus_id: Optional[str]
    parking_code: Optional[str]
    vcard_type: Optional[str]
    first_name_th: Optional[str]
    last_name_th: Optional[str]
    first_name_en: Optional[str]
    middle_name_en: Optional[str]
    last_name_en: Optional[str]
    identity_card: Optional[str]
    passport_id: Optional[str]
    issue_date: Optional[date]
    expiry_date: Optional[date]
    phone: Optional[str]
    brand_name1: Optional[str]
    color1: Optional[str]
    license_plate1: Optional[str]
    province_car1: Optional[str]
    brand_name2: Optional[str]
    color2: Optional[str]
    license_plate2: Optional[str]
    province_car2: Optional[str]
    ownership1: Optional[str]
    occupy1: Optional[str]
    ownership2: Optional[str]
    occupy2: Optional[str]
    copy_id_card: Optional[str]
    passport: Optional[str]
    copy_doc_car1: Optional[str]
    copy_doc_car2: Optional[str]
    card_member_copy: Optional[str]
    address_no: Optional[str]
    unit_home: Optional[str]
    village: Optional[str]
    alley: Optional[str]
    street: Optional[str]
    sub_district: Optional[str]
    district: Optional[str]
    province: Optional[str]
    postal_code: Optional[str]
    company_name: Optional[str]
    company_no: Optional[str]
    company_unit: Optional[str]
    identity_com: Optional[str]
    company_village: Optional[str]
    company_alley: Optional[str]
    company_street: Optional[str]
    company_sub_district: Optional[str]
    company_district: Optional[str]
    company_province: Optional[str]
    company_postal_code: Optional[str]
    birth_date: Optional[date]
    parking_register_date: Optional[datetime]
    card_last_read_date: Optional[datetime]
    card_expire_date: Optional[date]
    card_status: Optional[str]
    deposit_amount: Optional[float]
    deposit_status: Optional[int]
    return_card: Optional[str]
    user_create_date: Optional[datetime]
    user_edit_date: Optional[datetime]
    user_create: Optional[str]
    user_edit: Optional[str]
    before7: Optional[int]
    after7: Optional[int]
    diffdate: Optional[str]
    deposit_return: Optional[str]
    comment: Optional[str]
    vehicle_type1: Optional[str]
    vehicle_type2: Optional[str]
    token_id: Optional[str]
    api_member_status: Optional[str]
    
    class Config:
        orm_mode = True 
    

def send_data_to_publish_service_with_ordernumber(ordernumber:str) -> None :
    try:
        log = Parking_log.query.filter_by(orderNumber=ordernumber).first()
        station = Parking_manage.query.filter_by(parking_code=log.parking_code).first()
        if station.line_name == 'สายสีน้ำเงิน':
            member_data = Parking_member.query.filter_by(card_id=log.card_id).filter(Parking_member.parking_code == log.parking_code)\
                .filter(or_(Parking_member.card_status == '1',Parking_member.card_status == None)).order_by(Parking_member.Id.desc()).first()
            member_model = MemberData.from_orm(member_data)
            command = dict()
            if log.transaction_type == '1':
                command['command'] = 'insert'
            elif log.transaction_type == '2':
                command['command'] = 'update'
            else:
                return 
            command['table'] = 'parking_member'
            command['data'] = member_model.dict()
            url = os.environ.get('CLOUD_PUBLISH_URL','https://test.mrta.cloud-publish-service.ittiponk.com/api/v1/add-command-to-income-queue')
            response = requests.post(url=url,json=command)
            if response.status_code != 200:
                print(f"can not send ordernumber : {ordernumber}")
    except Exception as e:
        print(traceback.format_exc())
        print(f"can not send ordernumber : {ordernumber}")
            
        
    
    
if __name__ == "__main__":
    send_data_to_publish_service_with_ordernumber('NMBBL1500020123345')
    