from app import app
from smartparking.payment.domain.base.aggregate import AggregateBase 
from smartparking.payment.domain.model.payment import Transaction
from flask import request,jsonify
from smartparking.parking.authen import authenApikey

@app.route('/api/payment/getpromptpayqrcode',methods=['POST'])
@authenApikey
def getpromptpayqrcode():
    transaction = Transaction(**request.get_json())
    if transaction.if_latest_transaction_from_owner_not_success():
        latest_transaction:AggregateBase = transaction.get_owner_latest_transaction()
        latest_transaction.update_service_charge(transaction)
        latest_transaction.add_termseq_to_transaction()
        latest_transaction.update()
        qrcode = latest_transaction.get_prompt_qrcode()
        return jsonify({'promptpayqrcode':qrcode})
    transaction.save_to_database()
    transaction.add_ordernumber_to_trasaction()
    transaction.add_termseq_to_transaction()
    transaction.update()
    qrcode = transaction.get_prompt_qrcode()
    return jsonify({'promptpayqrcode':qrcode})

@app.route('/api/payment/updatecashpayment',methods=['POST'])
@authenApikey
def updatecashpayment():
    transaction = Transaction(**request.get_json())
    if transaction.if_latest_transaction_from_owner_not_success():
        latest_transaction:AggregateBase= transaction.get_owner_latest_transaction()
        latest_transaction.update_service_charge(transaction)
        latest_transaction.paid_with_cash()
        invoice_no = latest_transaction.get_invoice_no()
        latest_transaction.update()
        return jsonify({'status':True,'invoice_no':invoice_no,'payment_type':'cash'})
    transaction.save_to_database()
    transaction.add_ordernumber_to_trasaction()
    transaction.paid_with_cash()
    invoice_no = transaction.get_invoice_no()
    transaction.update()
    return jsonify({'status':True,'invoice_no':invoice_no,'payment_type':'cash'})

@app.route('/api/payment/updateedcpayment',methods=['POST'])
@authenApikey
def updateedcpayment():
    transaction = Transaction(**request.get_json())
    if transaction.if_latest_transaction_from_owner_not_success():
        latest_transaction:AggregateBase= transaction.get_owner_latest_transaction()
        latest_transaction.update_service_charge(transaction)
        latest_transaction.paid_with_edc()
        invoice_no = latest_transaction.get_invoice_no()
        latest_transaction.update()
        return jsonify({'status':True,'invoice_no':invoice_no,'payment_type':'credit/debit'})
    transaction.save_to_database()
    transaction.add_ordernumber_to_trasaction()
    transaction.paid_with_edc()
    invoice_no = transaction.get_invoice_no()
    transaction.update()
    return jsonify({'status':True,'invoice_no':invoice_no,'payment_type':'credit/debit'})
