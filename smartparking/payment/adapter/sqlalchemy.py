from smartparking.payment.port.db_abstract import PaymentLogAbstrct
from app import Parking_log,db
from smartparking.payment.domain.base.aggregate import AggregateBase
from smartparking.payment.domain.model.payment import Transaction
from sqlalchemy import func,cast,Float
from datetime import date

class PaymentLogInSQLalchemy(PaymentLogAbstrct):
    def __init__(self):
        self.log:Parking_log = Parking_log
        self.db = db 
        
    def create_new_transaction(self,transaction:AggregateBase):
        new_transaction = self.log(**transaction.dict())
        self.db.session.add(new_transaction)
        self.db.session.commit()
        transaction.Id = new_transaction.Id
        
    def get_owner_latest_transaction_status(self,owner):
        latest_transaction = self.log.query.filter_by(owner=owner)\
            .order_by(self.log.Id.desc()).first()
        if latest_transaction and latest_transaction.payment_status != '1':
            return True 
        return False 
    
    def from_owner(self,owner) -> AggregateBase:
        latest_transaction = self.log.query.filter_by(owner=owner)\
            .order_by(self.log.Id.desc()).first()
        transaction = Transaction.from_orm(latest_transaction)
        return transaction
    
    def get_number_of_transaction_today(self,today):
        number_of_transaction = self.log.query.filter(
            self.log.parking_register_date == today
        ).count()
        return number_of_transaction
    
    def update_from_object(self,transaction:AggregateBase):
        log = self.log.query.filter_by(Id = transaction.Id).first()
        if log :
            for key,value in transaction.dict().items():
                if value:
                    if getattr(log,key) != value:
                        setattr(log,key,value)
                    pass 
                pass 
            self.db.session.commit()
            return True 
        return False
    
    def get_all_amount_and_fine_is_paid_and_paid_round_from_owner(self,owner):
        sum_transaction = self.log.query.with_entities(
            
            cast(func.sum(self.log.fine),Float).label('sumfine'),
            cast(func.sum(self.log.amount),Float).label('sumamount'),
            func.count(self.log.Id).label('countrow')
            
            )\
            .filter_by(owner=owner)\
            .filter(self.log.payment_status == '1').first()
            
        all_fine_is_paid = sum_transaction.sumfine
        all_amount_is_paid = sum_transaction.sumamount
        paid_round = sum_transaction.countrow
  
        if all_amount_is_paid:
            all_amount_is_paid = round(all_amount_is_paid / 0.93,2)
            return all_amount_is_paid,all_fine_is_paid,paid_round
        return 0.0,0.0,paid_round
    
    def get_number_of_success_transaction_in_this_day(self,parking_code):
        number_of_success_transaction = self.log.query.filter_by(transaction_type = '5')\
            .filter(self.log.parking_code == parking_code).filter(self.log.payment_status == '1')\
            .filter(self.log.payment_date >= date.today()).count()
        running = f'{number_of_success_transaction + 1}'.zfill(6)
        return running
            
        