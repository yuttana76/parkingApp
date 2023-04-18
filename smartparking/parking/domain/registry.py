from typing import Optional
from smartparking.parking.domain.base.singleton import Singleton


class Registry(metaclass=Singleton):
    def __init__(self):
        
        from smartparking.parking.port.log.db_abstract import LogAbstract
        self.log: Optional[LogAbstract] = None
        
        from smartparking.payment.port.db_abstract import PaymentLogAbstrct
        self.paymentlog: Optional[PaymentLogAbstrct] = None
        
        
