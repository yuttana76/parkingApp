from app import app
from smartparking.parking.domain.base.aggregate import AggregateBase 
from smartparking.parking.domain.model.car import Car
from flask import request ,jsonify
from smartparking.parking.authen import authenApikey,authenticateSV
from smartparking.parking.domain.registry import Registry

@app.route('/api/lprin/seperateauthority',methods=['POST'])
@authenApikey
def seperateauthorityfromlprin():
    car = Car(**request.get_json())
    member_status,message = car.seperateauthority()
    car.update_time_in()
    logId = car.create_new_log()
    return jsonify({'member_status':member_status,'id':logId,'message':message}),200

@app.route('/api/kioskin/getqrcodeidentify',methods=['POST'])
@authenApikey
def getqrcodeidentify():
    body = request.get_json()
    id = body.get('id')
    car:AggregateBase= Car().from_id(id)
    if car:
        car.get_qrcode()
        car.update_to_database()
        return jsonify({'qrcode':car.qrcode}),200
    return jsonify({'message':'invalid id'}),404

@app.route('/api/kiosk/updateopengateinstatus',methods=['POST'])
@authenApikey
def updateopengateinstatus():
    body = request.get_json()
    id = body.get('id')
    car:AggregateBase = Car().from_id(id)
    if car:
        car.update_opengatein_status()
        car.push_notification()
        car.update_time_in()
        car.update_to_database()
        return jsonify({'status':True}),200
    return jsonify({'message':'invalid id'}),404

@app.route('/api/kioskreserve/verifyqrcodereserve',methods=['POST'])
@authenApikey
def verifyqrcodereserve():
    body = request.get_json()
    qrcode = body.get('qrcode_reserve')
    parking_code = body.get('parking_code')
    reserve_status,message = Car().verify_qrcode_reserve(qrcode,parking_code)
    return jsonify({'status':reserve_status,'message':message})

@app.route('/api/kioskreserve/reservecheckout',methods=['POST'])
@authenApikey
def checkoutreserve():
    body = request.get_json()
    qrcode = body.get('qrcode_reserve')
    parking_code = body.get('parking_code')
    checkoutreserve,message = Car().reserve_checkout(qrcode,parking_code)
    return jsonify({'status':checkoutreserve,'message':message})

@app.route('/api/kioskestamp/useestamp',methods=['POST'])
@authenApikey
def useestamp():
    body = request.get_json()
    qrcode = body.get('qrcode')
    estamp = body.get('estamp')
    location_stamp = body.get('location_stamp')
    car:AggregateBase = Car().from_qrcode(qrcode)
    if car:
        if not car.is_member():
            car.get_estamp(estamp)
            car.update_location_stamp(location_stamp)
            car.update_to_database()
            return jsonify({'status':True,'time_in':car.time_in.strftime('%Y-%m-%d %H:%M:%S'),'license_plate':car.license_plate}),200
        return jsonify({'status':False,'message':'member can not use estamp'})
    return jsonify({'message':'invalid qrcode'}),404    

@app.route('/api/kioskpayment/getservicecharge',methods=['POST'])
@authenApikey
def getservicecharge():
    body = request.get_json()
    qrcode = body.get('qrcode')
    car:AggregateBase = Car().from_qrcode(qrcode)
    if car :
        total,service_charge,vat,fine,hours,time_out = car.get_service_charge()
        return jsonify({
            'total':total,
            'amount':service_charge,
            'vat':vat,
            'fine':fine,
            'owner':car.id,
            'license_plate':car.license_plate,
            'time_in':car.time_in.strftime('%Y/%m/%d %H:%M:%S'),
            'hours':hours,
            'time_out':time_out.strftime('%Y/%m/%d %H:%M:%S'),
            'client_type':car.client_type(),
            'car_type':car.car_type()
            })
    return jsonify({'message':'invalid qrcode'})

@app.route('/api/lprout/checkoutservice',methods=['POST'])
@authenApikey
def lprcheckoutservice():
    #create check point
    body = request.get_json()
    license_plate = body.get('license_plate')
    ip_out = body.get('ip_out')
    img_out = body.get('img_out')
    parking_code = body.get('parking_code')
    location_out = body.get('location_out')
    time_out_sender = body.get('time_out_sender')
    
    car:AggregateBase = Car().from_license_plate_and_parking_code(license_plate,parking_code)
    if car:
        if car.have_amount():
            return jsonify({'status':False,'message':'have amount is not paid.'})
        else:
            if car.is_member():
                car.check_out_service(ip_out,img_out,location_out,time_out_sender)
                car.update_to_database()
                return jsonify({'status':True,'id':car.id,'message':"this car is member"})
            return jsonify({'status':False,'id':car.id,'message':'this visitor already paid'})
    return jsonify({'status':False,'message':"can not map this license plate"})
    
@app.route('/api/kioskout/checkoutservice',methods=['POST'])
@authenApikey
def kioskcheckoutservice():
    body = request.get_json()
    qrcode = body.get('qrcode')
    ip_out = body.get('ip_out')
    img_out = body.get('img_out')
    location_out = body.get('location_out')
    time_out_sender = body.get('time_out_sender')
    
    car:AggregateBase = Car().from_qrcode(qrcode)  
    if car:
        if car.have_amount():
            return jsonify({'status':False,'message':'Have amount is not paid.'})
        else:
            car.check_out_service(ip_out,img_out,location_out,time_out_sender)
            car.update_to_database()
            return jsonify({'status':True,'id':car.id})
    return jsonify({'status':False,'message':"Can not map this qrcode"})  
    
@app.route('/api/barrierout/endservice',methods=['POST'])
@authenApikey
def endservice():
    body =  request.get_json()
    id = body.get('id')
    
    car:AggregateBase = Car().from_id(id)
    if car:
        car.update_opengateout_status()
        car.update_to_database()
        return jsonify({'status':True})
    return jsonify({'status':False,'message':'Can not map this id'})
    
#subdomain
@app.route('/api/kioskmyqrcode/myqrcodecheckin',methods=['POST'])
@authenApikey
def myqrcodecheckin():
    body =  request.get_json()
    license_plate = body.get('license_plate')
    parking_code = body.get('parking_code')
    ip_in = body.get('ip_in')
    img_in = body.get('img_in')
    myqrcode = body.get('qrcode')
    type = body.get('type')
    time_in_sender = body.get('time_in_sender')
    location_in = body.get('location_in')
    
    #update log myqrcode and verify member status
    car:AggregateBase = Car().from_myqrcode(myqrcode)
    if car:
        car.update_car_detail_from_requests_body(
            license_plate = license_plate,
            parking_code = parking_code,
            ip_in = ip_in,
            img_in = img_in,
            type = type,
            time_in_sender = time_in_sender,
            location_in = location_in
        )
        member_status,message = car.verify_authority_from_identity_card_and_parking_code()
        car.update_time_in()
        car.update_to_database()
        
        #deactivate log this car is check in with lpr
        target_car:AggregateBase = Car().from_license_plate_and_parking_code(license_plate,parking_code)
        if target_car:
            target_car.set_deactivate_status()
            target_car.update_to_database()
            
        return jsonify({'member_status':member_status,'id':car.id,'message':message,'status':True})
    return jsonify({'message':'can not map myqrcode','status':False}),400
    
@app.route('/api/kioskpayment/checkpaymentstatus',methods=['POST'])
@authenApikey
def checkpaymentstatus():
    body = request.get_json()
    qrcode = body.get('qrcode')
    car:AggregateBase = Car().from_qrcode(qrcode)
    if car : 
        if car.have_amount():
            return jsonify({'status':False})
        return jsonify({'status':True,'invoice_no':car.get_invoice()})
    return jsonify({'message':'invalid qrcode'})

@app.route('/api/healthcheck',methods=['GET'])
# @authenApikey
def healthcheck():
    status = Registry().log.healthcheck()
    return jsonify({'status':status})

@app.route('/api/v1/verify/qrcode',methods=['POST'])
def verify_qrcode():
    body = request.get_json() 
    qrcode = body.get('qrcode')
    car:AggregateBase = Car().from_qrcode(qrcode)
    if car:
        return jsonify({'status':True,'license_plate':car.license_plate})
    return jsonify({'status':False,'license_plate':None})