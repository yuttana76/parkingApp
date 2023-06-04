from pydantic import BaseModel
from abc import abstractmethod,ABC
from typing import Optional
from datetime import date,datetime

class AggregateBase(BaseModel,ABC):
    Id : Optional[int] = None 
    transaction_type = '5'
    parking_code : Optional[str] = None
    parking_register_date = date.today()
    owner : Optional[int] = None 
    term_seq : Optional[str] = None 
    orderNumber : Optional[str] = None
    amount : Optional[float] = None 
    vat : Optional[float] = None 
    fine : Optional[float] = None
    total : Optional[float] = None 
    payment_status : Optional[str] = None
    payment_name : Optional[str] = None
    payment_date : Optional[datetime] = None
    identity_card : Optional[str] = '0994000165706'
    invoice_no: Optional[str] = None
    
    class Config:
        orm_mode = True
        
    @abstractmethod
    def save_to_database(self):
        pass 
    
    @abstractmethod
    def if_latest_transaction_from_owner_not_success(self):
        pass
    
    @abstractmethod
    def get_owner_latest_transaction(self):
        pass 
    
    @abstractmethod
    def add_ordernumber_to_trasaction(self):
        pass 
    
    @abstractmethod
    def add_termseq_to_transaction(self):
        pass 
    
    @abstractmethod
    def update(self):
        pass 
    
    @abstractmethod
    def get_prompt_qrcode(self):
        pass 
    
    @abstractmethod
    def update_service_charge(self):
        pass 
    
    @abstractmethod
    def paid_with_cash(self):
        pass 
    
    @abstractmethod
    def paid_with_edc(self):
        pass 
    
    @abstractmethod
    def get_invoice_no(self):
        pass 
    
    @abstractmethod
    def from_ordernumber(self,ordernumber:str):
        pass