from smartparking.parking.domain.base.aggregate import AggregateBase 
import secrets 
from smartparking.parking.domain.registry import Registry
from datetime import datetime,timedelta
from time import strftime,gmtime


class Car(AggregateBase):
    
    #seperateauthority
    def seperateauthority(self):
        member_status,message = Registry().log.get_member_status(
            license_plate = self.license_plate,
            parking_code = self.parking_code
        )
        if member_status:
            self.member_status = '1'
            return True,message 
        self.member_status = '0'
        return False ,message
    
    def create_new_log(self):
        logId = Registry().log.create_new_log(self)
        return logId
    
    def update_time_in(self):
        self.time_in = datetime.today()

    #getqrcodeidentify
    def from_id(self,id) :
        log = Registry().log.from_id(id)
        if log:
            return log
        return None
        
    def get_qrcode(self):
        if not self.qrcode:
            qrcode = secrets.token_urlsafe(50)
            self.qrcode = qrcode 
            
    def update_to_database(self):
        Registry().log.update_from_object(self)
        
    #updateopengateinstatus
    def update_opengatein_status(self):
        self.opengatein_status = '1'
        
    def push_notification(self):
        if self.member_status == '1':
            Registry().log.insert_message_box_member(self)
        else:
            Registry().log.insert_message_box_visitor(self)
    
        
    #verify_qrcode_reserve
    def verify_qrcode_reserve(self,qrcode,parking_code):
        reserve_status,message = Registry().log.verify_qrcode_reserve(qrcode,parking_code)
        return reserve_status,message
    
    #reserve_checkout
    def reserve_checkout(self,qrcode,parking_code):
        checkout_status,message = Registry().log.update_reserve_checkout(qrcode,parking_code)
        return checkout_status,message
    
    #estamp
    def get_estamp(self,estamp):
        self.estamp = estamp 
        
    def from_qrcode(self,qrcode):
        car = Registry().log.from_qrcode(qrcode)
        return car
    
    def update_location_stamp(self,location_stamp):
        self.location_stamp = location_stamp
    
    #calculate service charge
    def get_service_charge(self):
        over_night_start_list,over_night_stop_list,fine = Registry().log.get_over_night_period_range(self.parking_code)
        
        # estamp change period time ,price and minute plus
        if self.estamp:
            period_time,price,minutes_plus = Registry().log.get_period_time_and_price_from_estamp(self.parking_code,self.type)
        else:
            period_time,price,minutes_plus = Registry().log.get_period_time_and_price_from_parking_code(self.parking_code,self.type)
        
        all_amount_is_paid,all_fine_is_paid,paid_round = Registry().paymentlog.get_all_amount_and_fine_is_paid_and_paid_round_from_owner(self.id)
        minutes_plus = minutes_plus * paid_round
        
        now = datetime.today() 
        
        # has paid + minute_plus
        now -= timedelta(minutes=minutes_plus)
        
        time_in = self.time_in
        service_charge = 0.0
        fine_amount = 0.0
        
        over_night_start = time_in.replace(hour=over_night_start_list[0],minute=over_night_start_list[1],second=over_night_start_list[2])
        over_night_stop = time_in.replace(hour=over_night_stop_list[0],minute=over_night_stop_list[1],second=over_night_stop_list[2])
        minus_time = (now - time_in)
        total_seconds = minus_time.total_seconds()
        hours_format = strftime("%H:%M:%S", gmtime(total_seconds))
        while time_in < now:            
            
            if self.is_between_overnight_start_and_stop(start=over_night_start,time=time_in,stop=over_night_stop):
                fine_amount += fine 
                time_in = over_night_stop
            else:
                time_in += timedelta(minutes=period_time)
                over_night_start = time_in.replace(hour=over_night_start_list[0],minute=over_night_start_list[1],second=over_night_start_list[2])
                over_night_stop = time_in.replace(hour=over_night_stop_list[0],minute=over_night_stop_list[1],second=over_night_stop_list[2])
                if self.is_between_overnight_start_and_stop(start=over_night_start,time=time_in,stop=over_night_stop):
                    fine_amount += fine 
                    time_in = over_night_stop
                else:
                    service_charge += price 
                    
        

        service_charge -= all_amount_is_paid if service_charge > 0 else 0
        fine_amount -= all_fine_is_paid if fine_amount > 0 else 0
        if self.member_status == '1':
            vat = 0.0
            service_charge = 0.0
            total = fine_amount
        else:
            vat = service_charge * 0.07       
            service_charge -= vat 
            total = service_charge + vat + fine_amount
        
        return total,round(service_charge,2),round(vat,2),fine_amount,hours_format,now
    
    @staticmethod
    def is_between_overnight_start_and_stop(start,time,stop):
        if start <= time < stop:
            return True 
        return False
    
    #check out service
    def check_out_service(self,ip_out,img_out,location_out,time_out_sender):
        self.time_out = datetime.today()
        total_time = self.time_out - self.time_in
        total_time = round(total_time.total_seconds() / 60,2)
        self.total_time = total_time
        self.ip_out = ip_out 
        self.img_out = img_out 
        self.location_out = location_out
        self.time_out_sender = time_out_sender 

    def from_license_plate_and_parking_code(self,license_plate,parking_code):
        return Registry().log.from_license_plate_and_parking_code(license_plate,parking_code)
    
    def have_amount(self):
        total,service_charge,vat,fine,hours,time_out = self.get_service_charge()
        if total > 0:
            return True 
        return False
    
    #end service
    def update_opengateout_status(self):
        self.opengateout_status = '1'
        
    #subdomain myqrcode 
    def verify_authority_from_identity_card_and_parking_code(self):
        member_status,message = Registry().log.get_member_status_from_identity_card(
            identity_card = self.identity_card,
            parking_code = self.parking_code,
            license_plate = self.license_plate
            )
        if member_status:
            self.member_status = '1'
            return True,message 
        self.member_status = '0'
        return False,message 
    
    def update_car_detail_from_requests_body(self,license_plate,parking_code,ip_in,img_in,type,time_in_sender,location_in):
        self.license_plate = license_plate
        self.parking_code = parking_code
        self.ip_in = ip_in
        self.img_in = img_in
        self.type = type
        self.time_in_sender = time_in_sender
        self.location_in = location_in
        
    def set_deactivate_status(self):
        self.deactivate = '1'
        
    def from_myqrcode(self,myqrcode):
        car = Registry().log.from_myqrcode(myqrcode)
        return car
    
    def car_type(self) -> str:
        if self.type == '1':
            return 'รถยนต์'
        elif self.type == '2':
            return 'รถมอเตอร์ไซค์'
        else:
            return 'unknow'
    
    def client_type(self) -> str:
        if self.estamp:
            return 'ผู้ใช้บริการรถไฟฟ้า'
        else:
            return 'ผู้ไม่ใช้บริการรถไฟฟ้า'
        
    def get_invoice(self) -> str:
        invoice_no = Registry().log.get_invoice(self.id)
        return invoice_no
    
    def is_member(self) -> bool:
        if self.member_status == '1':
            return True 
        return False