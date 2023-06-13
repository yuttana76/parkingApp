from app import app
from smartparking.payment.domain.base.aggregate import AggregateBase 
from smartparking.payment.domain.model.payment import Transaction
from flask import request,jsonify
from smartparking.payment.domain.base.exception import InvalidOrdernumber

@app.route('/api/v1/blue-line/payment/getpromptpayqrcode',methods=['POST'])
def blueline_getpromptpayqrcode():
    transaction = Transaction(**request.get_json())
    if transaction.if_latest_transaction_from_owner_not_success():
        latest_transaction:AggregateBase = transaction.get_owner_latest_transaction()
        latest_transaction.update_service_charge(transaction)
        latest_transaction.add_termseq_to_transaction()
        qrcode = latest_transaction.get_prompt_qrcode()
        latest_transaction.update()
        return jsonify({'promptpayqrcode':qrcode,'ordernumber':transaction.orderNumber})
    transaction.save_to_database()
    transaction.add_ordernumber_to_trasaction()
    transaction.add_termseq_to_transaction()
    qrcode = transaction.get_prompt_qrcode()
    transaction.update()
    return jsonify({'promptpayqrcode':qrcode,'ordernumber':transaction.orderNumber})

@app.route('/api/v1/blue-line/query-payment-status',methods=['POST'])
def blueline_query_payment_status():
    try:
        request_body = request.get_json()
        ordernumber = request_body.get('ordernumber')
        transaction:AggregateBase = Transaction().from_ordernumber(ordernumber)
        if transaction.payment_status == '1':
            return jsonify({'status':True})
        return jsonify({'status':False})
    except InvalidOrdernumber:
        return jsonify({'message':'invalid ordernumber'}),422
    
@app.route('/api/v1/blue-line/update/payment-status',methods=['POST'])
def blueline_update_payment_status():
    try:
        request_body = request.get_json()
        ordernumber = request_body.get('ordernumber')
        payment_status = request_body.get('payment_status')
        transaction:AggregateBase = Transaction().from_ordernumber(ordernumber)
        if payment_status:
            transaction.payment_status = '1'
        else:
            transaction.payment_status = '0'
        transaction.update()
        return jsonify({'message':'success'}),200
    except InvalidOrdernumber:
        return jsonify({'message':'invalid ordernumber'}),422
            
        