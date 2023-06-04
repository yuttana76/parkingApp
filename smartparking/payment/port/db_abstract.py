from abc import ABC, abstractmethod 
from smartparking.payment.domain.base.aggregate import AggregateBase

class PaymentLogAbstrct(ABC):
    
    @abstractmethod
    def create_new_transaction(self):
        pass 
    
    @abstractmethod
    def from_owner(self) -> AggregateBase:
        pass 
    
    @abstractmethod
    def get_owner_latest_transaction_status(self):
        pass 
    
    @abstractmethod
    def get_number_of_transaction_today(self):
        pass 
    
    @abstractmethod
    def update_from_object(self):
        pass
    
    @abstractmethod 
    def get_all_amount_and_fine_is_paid_and_paid_round_from_owner(self):
        pass
    
    @abstractmethod
    def get_number_of_success_transaction_in_this_day(self,parking_code) -> str:
        pass
    
    @abstractmethod
    def from_ordernumber(self,ordernumber:str) -> AggregateBase:
        pass 
    
    
    