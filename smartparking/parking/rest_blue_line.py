from app import app
from smartparking.parking.domain.model.car import Car
from flask import request,jsonify
from smartparking.parking.domain.base.aggregate import AggregateBase 

@app.route('/api/v1/blue-line/verify-myqrcode',methods=['POST'])
def blue_line_verify_myqrcode():
    request_body = request.get_json()
    qrcode = request_body.get('qrcode')
    parking_code = request_body.get('parking_code')
    license_plate = request_body.get('license_plate')
    car:AggregateBase = Car().from_myqrcode(qrcode)
    if car:
        car.parking_code = parking_code
        car.license_plate = license_plate
        member_status,message = car.verify_authority_from_identity_card_and_parking_code()
        return jsonify({'member_status':member_status,'message':message})
    return jsonify({'message':'invalid qrcode'}),422