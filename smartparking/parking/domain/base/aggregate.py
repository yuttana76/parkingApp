from pydantic import BaseModel
from abc import abstractmethod,ABC
from typing import Optional 
from datetime import datetime 

class AggregateBase(BaseModel,ABC):
    id: Optional[int] = None 
    parking_code: Optional[str] = None 
    member_status: Optional[str] = None 
    time_in: Optional[datetime] = None
    time_in_sender: Optional[datetime] = None
    location_in: Optional[str] = None
    license_plate: Optional[str] = None 
    ip_in: Optional[str] = None
    location_stay: Optional[str] = None
    opengatein_status: Optional[str] = None
    opengateout_status: Optional[str] = None
    img_in: Optional[str] = None 
    time_out: Optional[datetime] = None
    time_out_sender: Optional[datetime] = None
    location_out: Optional[str] = None
    ip_out: Optional[str] = None
    total_time: Optional[str] = None
    img_out: Optional[str] = None
    qrcode: Optional[str] = None 
    estamp: Optional[str] = None 
    location_stamp: Optional[str] = None
    identity_card: Optional[str] = None 
    deactivate: Optional[str] = None
    type: Optional[str] = None
    sender_transaction_id: Optional[str] = None
    
    
    
    
    class Config:
        orm_mode = True
    
    @abstractmethod 
    def get_qrcode(self):
        pass 
    
    @abstractmethod
    def seperateauthority(self):
        pass 
    
    @abstractmethod
    def create_new_log(self):
        pass 
    
    @abstractmethod
    def update_to_database(self):
        pass
    
    @abstractmethod
    def update_opengatein_status(self):
        pass 
   
    @abstractmethod
    def verify_qrcode_reserve(self):
        pass 
    
    @abstractmethod
    def reserve_checkout(self):
        pass 
    
    @abstractmethod
    def get_estamp(self):
        pass 
    
    @abstractmethod
    def from_qrcode(self):
        pass 
    
    @abstractmethod
    def get_service_charge(self):
        pass 
    
    @abstractmethod
    def update_time_in(self):
        pass 
    
    @abstractmethod
    def push_notification(self):
        pass 
    
    @abstractmethod
    def check_out_service(self):
        pass 
    
    @abstractmethod
    def from_license_plate_and_parking_code(self):
        pass 
    
    @abstractmethod
    def have_amount(self):
        pass 
    
    @abstractmethod
    def update_opengateout_status(self):
        pass 
    
    @abstractmethod
    def verify_authority_from_identity_card_and_parking_code(self):
        pass 
    
    @abstractmethod
    def update_car_detail_from_requests_body(self):
        pass 
    
    @abstractmethod
    def set_deactivate_status(self):
        pass 
    
    @abstractmethod
    def from_myqrcode(self):
        pass 
    
    @abstractmethod
    def update_location_stamp(self):
        pass 
    
    @abstractmethod
    def car_type(self) -> str:
        pass 
    @abstractmethod
    def client_type(self) -> str:
        pass 
    
    @abstractmethod
    def get_invoice(self) -> str:
        pass 
    
    @abstractmethod
    def is_member(self) -> bool:
        pass 
    
    
