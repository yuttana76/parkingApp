from smartparking.parking.domain.registry import Registry
from smartparking.parking.adapter.log.sqlalchemy import LogInSqlAlchemy
from smartparking.payment.adapter.sqlalchemy import PaymentLogInSQLalchemy

def inject():
    Registry().log = LogInSqlAlchemy()
    Registry().paymentlog = PaymentLogInSQLalchemy()