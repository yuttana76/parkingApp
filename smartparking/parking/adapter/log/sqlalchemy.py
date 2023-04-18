from app import Parking_logvisitor ,db ,Parking_member,Parking_log,Parking_manage,Estamp,Message_box,Customer_register
from smartparking.parking.port.log.db_abstract import LogAbstract
from smartparking.parking.domain.model.car import Car
from smartparking.parking.domain.base.aggregate import AggregateBase
from sqlalchemy import or_
from datetime import date,datetime

class LogInSqlAlchemy(LogAbstract):
    def __init__(self):
        self.db = db 
        self.log:Parking_logvisitor = Parking_logvisitor
    
    def from_id(self,id_) -> AggregateBase:
        log = self.log.query.filter_by(id = id_).first()
        if log:
            car = Car.from_orm(log)
            return car 
        return None
    
    def from_license_plate_and_parking_code(self,license_plate,parking_code) -> AggregateBase:
        log = self.log.query.filter_by(license_plate = license_plate) \
            .filter(self.log.parking_code == parking_code)\
            .filter(self.log.time_out == None)\
            .filter(self.log.deactivate != '1') \
                .order_by(self.log.id.desc()).first()
        if log :
            car = Car.from_orm(log)
            return car 
        return None
    
    def from_qrcode(self,qrcode):
        log = self.log.query.filter_by(qrcode = qrcode)\
            .filter(self.log.time_out == None) \
            .order_by(self.log.id.desc()).first()
        if log :
            car = Car.from_orm(log)
            return car 
        return None 
    
    def from_myqrcode(self,myqrcode):
        log = self.log.query.filter_by(qrcode = myqrcode)\
            .filter(self.log.time_in == None) \
            .filter(self.log.time_out == None) \
            .order_by(self.log.id.desc()).first()
        if log :
            car = Car.from_orm(log)
            return car 
        return None 
    
    def create_new_log(self,car:AggregateBase):
        newlog = self.log(**car.dict())
        self.db.session.add(newlog)
        self.db.session.commit()
        return newlog.id
        
    def update_from_object(self,car:AggregateBase):
        log = self.log.query.filter_by(id = car.id).first()
        if log :
            update_status = False
            for key,value in car.dict().items():
                if value:
                    if getattr(log,key) != value:
                        setattr(log,key,value)
                        update_status = True 
                    pass 
                pass 
            if update_status:
                self.db.session.commit()
            return True 
        return False 
    
    def delete_from_id(self,id_):
        log = self.log.query.filter_by(id = id_).first()
        if log :
            self.db.session.delete(log)
            self.db.session.commit()
            return True
        return False
    
    #out of concept
    def get_member_status(self,license_plate,parking_code):
        member = Parking_member.query.filter(
            or_(
                (Parking_member.license_plate1 == license_plate),
                (Parking_member.license_plate2 == license_plate)
            )
        ).filter(Parking_member.parking_code == parking_code).first()
        if member :
            if member.card_expire_date < date.today():
                return False,'member is expire'
            
            license_plate_list = [member.license_plate1,member.license_plate2]
            license_plate_list.remove(license_plate)
            for car in license_plate_list:
                if car:
                    another_car = Parking_logvisitor.query.filter(
                        (Parking_logvisitor.license_plate == car) &\
                        (Parking_logvisitor.parking_code == parking_code) &\
                        (Parking_logvisitor.member_status == '1') &\
                        (Parking_logvisitor.time_out == None) &\
                        (Parking_logvisitor.deactivate != '1')
                    ).first()
                    if another_car:
                        return False,'member have another car in this parking lot'
                else:
                    pass
            return True,'member is already'
        return False,'this car is not member'
    
    def verify_qrcode_reserve(self,qrcode,parking_code):
        reserve_log = Parking_log.query.filter_by(qr_code_reserve=qrcode)\
            .filter(Parking_log.parking_code == parking_code)\
            .filter(Parking_log.qr_code_gatein_status == None).first()
        if reserve_log:
            if reserve_log.qr_code_exprie >= datetime.today() and reserve_log.qr_code_gatein_status !='1':
                reserve_log.qr_code_gatein_status ='1'
                reserve_log.opengatein_date = datetime.today()
                self.db.session.commit()
                return True,'reserve qrcode is already'
            return False,'reserve qrcode is expire'
        return False,'can not map reserve qrcode'
    
    def update_reserve_checkout(self,qrcode,parking_code):
        reserve_log = Parking_log.query.filter_by(qr_code_reserve=qrcode)\
            .filter(Parking_log.parking_code == parking_code).first()
        if reserve_log and reserve_log.qr_code_gatein_status == '1':
            reserve_log.opengateout_date = datetime.today()
            reserve_log.qr_code_gateout_status = '1'
            self.db.session.commit()
            return True,'reserve checkout success'
        return False ,'can not map reserve qrcode'
    
    def get_period_time_and_price_from_parking_code(self,parking_code,type_):
        parkinglot = Parking_manage.query.filter_by(parking_code=parking_code).first()
        if parkinglot:
            if type_ == '1':
                return parkinglot.period_time,float(parkinglot.price),parkinglot.minute_plus
            elif type_ == '2':
                return parkinglot.period_time_motocycle,float(parkinglot.price_motocycle),parkinglot.minute_plus_motocycle
        return None,None,0
    
    def get_period_time_and_price_from_estamp(self,parking_code,type_):
        estamp = Estamp.query.filter_by(parking_code = parking_code).filter(Estamp.type == type_).first()
        if estamp:
            return estamp.period_time,float(estamp.price),estamp.minute_plus
        return None,None,0
    
    def get_over_night_period_range(self,parking_code):
        parkinglot = Parking_manage.query.filter_by(parking_code=parking_code).first()
        if parkinglot:
            over_night_start_str_list = [int(time) for time in parkinglot.over_night_start.split(':')]
            over_night_stop_str_list = [int(time) for time in parkinglot.over_night_stop.split(':')]
            return over_night_start_str_list,over_night_stop_str_list,float(parkinglot.over_night)
        return None,None,None
    
    def insert_message_box_member(self,car:AggregateBase):
        user = Parking_member.query.filter(
                or_(
                    (Parking_member.license_plate1 == car.license_plate),
                    (Parking_member.license_plate2 == car.license_plate)
                )
            ).filter(Parking_member.parking_code == car.parking_code)\
            .filter(Parking_member.card_expire_date >= date.today()).first()
        identity_card = user.identity_card
        description = f'ยินดีต้อนรับเข้าสู่ลานจอด ตรวจค่าบริการที่นี่'
        new_message = Message_box(
            identity_card = identity_card,
            des_noti = description,
            date = car.time_in.date(),
            read = '0'
        )
        self.db.session.add(new_message)
        self.db.session.commit()
        
    def insert_message_box_visitor(self,car:AggregateBase):
        user = Customer_register.query.filter_by(license_plate = car.license_plate)\
            .filter(Customer_register.register_status == '1').first() or  Parking_member.query.filter(
                or_(
                    (Parking_member.license_plate1 == car.license_plate),
                    (Parking_member.license_plate2 == car.license_plate)
                )
            ).filter(Parking_member.card_expire_date >= date.today()).first()
        if not user:
            user = Parking_member.query.filter(
                or_(
                    (Parking_member.license_plate1 == car.license_plate),
                    (Parking_member.license_plate2 == car.license_plate)
                )
            ).filter(Parking_member.parking_code == car.parking_code)\
            .filter(Parking_member.card_expire_date >= date.today()).first()
        if user:
            identity_card = user.identity_card 
            description = f'ยินดีต้อนรับเข้าสู่ลานจอด ตรวจค่าบริการที่นี่'
            new_message = Message_box(
                identity_card = identity_card,
                des_noti = description,
                date = car.time_in.date(),
                read = '0',
                link = '/billslist'
            )
            self.db.session.add(new_message)
            self.db.session.commit()
            
    def get_member_status_from_identity_card(self,identity_card,parking_code,license_plate):
        member = Parking_member.query\
            .filter(Parking_member.identity_card == identity_card)\
            .filter(Parking_member.parking_code == parking_code)\
            .filter(
                or_(
                    (Parking_member.license_plate1 == license_plate),
                    (Parking_member.license_plate2 == license_plate)
                )
            ).first()
        if member :
            if member.card_expire_date < date.today():
                return False,'member is expire'
            
            license_plate_list = [member.license_plate1,member.license_plate2]
            license_plate_list.remove(license_plate)
            for car in license_plate_list:
                if car:
                    another_car = Parking_logvisitor.query.filter(
                        (Parking_logvisitor.license_plate == car) &\
                        (Parking_logvisitor.parking_code == parking_code) &\
                        (Parking_logvisitor.time_out == None) &\
                        (Parking_logvisitor.deactivate != '1')
                    ).first()
                    if another_car:
                        return False,'member have another car in this parking lot'
                else:
                    pass
            return True,'member is already'
        return False,'this car is not member'
    
    def healthcheck(self):
        row = self.log.query.first()
        if row :
            return True 
        return False
    
    def get_invoice(self,id_):
        latest_log = Parking_log.query.filter_by(owner=id_).order_by(Parking_log.Id.desc()).first()
        return latest_log.invoice_no
        
        
        