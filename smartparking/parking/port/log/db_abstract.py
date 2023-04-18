from abc import abstractmethod,ABC

class LogAbstract(ABC):
    
    @abstractmethod
    def from_id(self):
        pass 
    
    @abstractmethod
    def from_license_plate_and_parking_code(self):
        pass 
    
    @abstractmethod
    def from_qrcode(self):
        pass 
    
    @abstractmethod
    def create_new_log(self):
        pass 
    
    @abstractmethod
    def update_from_object(self):
        pass 
    
    @abstractmethod
    def delete_from_id(self):
        pass 
    
    #out of concept
    @abstractmethod
    def get_member_status(self):
        pass
    
    @abstractmethod
    def verify_qrcode_reserve(self):
        pass 
    
    @abstractmethod
    def update_reserve_checkout(self):
        pass 
    
    @abstractmethod
    def get_period_time_and_price_from_parking_code(self):
        pass 
    
    @abstractmethod
    def get_period_time_and_price_from_estamp(self):
        pass 
    
    @abstractmethod
    def get_over_night_period_range(self):
        pass 
    
    @abstractmethod
    def insert_message_box_member(self):
        pass 
    
    @abstractmethod
    def insert_message_box_visitor(self):
        pass 
    
    @abstractmethod
    def get_member_status_from_identity_card(self):
        pass 
    
    @abstractmethod
    def from_myqrcode(self):
        pass 
    
    @abstractmethod
    def healthcheck(self):
        pass 
    
    @abstractmethod
    def get_invoice(self):
        pass