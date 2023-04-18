from flask import request
from app import  (
    Parking_logvisitor as plv,
    Parking_log as pl,
    db,
    app
)
import secrets

@app.route('/api/reset/mockmyqrcode', methods=['POST'])
def mock_my_qrcode():
    req_data = request.get_json()
    member_status = req_data['member_status']
    if member_status:
        id = 3011
    else:
        id = 3207
    log = plv.query.filter_by(id=id).first()
    payment_log = pl.query.filter_by(owner=id).first()
    if payment_log:
        db.session.delete(payment_log)
    log.license_plate = None
    log.ip_in = None
    log.img_in = None
    log.parking_code = None
    log.type = None
    log.estamp = None
    log.ip_out = None
    log.img_out = None
    log.member_status = None
    log.time_in = None
    log.time_out = None
    log.total_time = None
    log.opengatein_status = None
    log.opengateout_status = None
    log.deactivate = '0'
    db.session.commit()
    return {'status':'Reset qrcode complete','qrcode':log.qrcode}