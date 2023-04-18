from ast import literal_eval
from datetime import datetime
import re
from sqlalchemy.sql.expression import label
from wtforms import validators
from app import Customer_register
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,DateField,SelectField,TextAreaField,FileField
from wtforms.validators import Length,EqualTo,Email,DataRequired,ValidationError,Optional,InputRequired
# from wtforms_validators import AlphaNumeric
from flask_login import current_user
from flask_wtf.file import FileRequired


class RegisterForm(FlaskForm):
    def validate_email_address(self,email_address_to_check):
        email_address = Customer_register.query.filter_by(email=email_address_to_check.data).first()
        if email_address:
            if email_address.register_status == '1':
                raise ValidationError('อีเมลนี้ได้ถูกใช้งานแล้ว กรุณากรอกใหม่อีกครั้ง')
    def validate_identity_card(self,identity_card_to_check):
        identity_card =  Customer_register.query.filter_by(identity_card=identity_card_to_check.data).first()
        if identity_card:
            if identity_card.register_status == '1':
                raise ValidationError('เลขบัตรประชาชนถูกใช้งานแล้ว กรุณากรอกใหม่')

    def validate_password(self,password_to_check):
        password= password_to_check.data
        if re.search('[0-9]',password) is None:
            raise ValidationError("รหัสผ่านต้องประกอบด้วยตัวอักษร a-z, A-Z และ 0-9")
        elif re.search('[A-Z|a-z]',password) is None:
            raise ValidationError("รหัสผ่านต้องประกอบด้วยตัวอักษร a-z, A-Z และ 0-9")


    name = StringField(label='ชื่อ',validators=[DataRequired()])
    last_name = StringField(label='นามสกุล',validators=[DataRequired()])
    identity_card = StringField(label='identity_card',validators=[DataRequired(),Length(min=13,max=13)])
    email_address = StringField(label='email',validators=[Email(),DataRequired()])
    password = PasswordField(label='Password',validators=[Length(min=8,message='รหัสผ่านต้องประกอบด้วยตัวอักษร a-z, A-Z และ 0-9 ความยาวขั้นต่ำ 8 ตัวอักษร'),DataRequired()])
    # password = PasswordField(label='Password',validators=[Length(min=8,message='รหัสผ่านต้องประกอบด้วยตัวอักษร a-z, A-Z และ 0-9 ความยาวขั้นต่ำ 8 ตัวอักษร'),DataRequired(),AlphaNumeric('ห้ามมีอักขระพิเศษ เช่น!@#$%^&*()_-+')])
    confirm_password = PasswordField(label='Confirm password',validators=[EqualTo('password','รหัสผ่านไม่ตรงกัน กรุณากรอกใหม่'),DataRequired()])
    submit = SubmitField(label='สร้างบัญชี')
    #,render_kw={"onclick": "alert('ขณะนี้ทางเราปิดรับสมัครสมาชิคชั่วคราวรบกวนกลับมาทำรายการใหม่ภายในวันที่ 14/12/2564 ขออภัยในความไม่สะดวกครับ/ค่ะ')"}


class RegisterForm_eng(FlaskForm):
    def validate_email_address(self,email_address_to_check):
        email_address = Customer_register.query.filter_by(email=email_address_to_check.data).first()
        if email_address:
            if email_address.register_status == '1':
                raise ValidationError('This email is already in use. Please enter again.')
    def validate_identity_card(self,identity_card_to_check):
        identity_card =  Customer_register.query.filter_by(identity_card=identity_card_to_check.data).first()
        if identity_card:
            if identity_card.register_status == '1':
                raise ValidationError('Your ID card number is already in use, please fill it out.')

    def validate_password(self,password_to_check):
        password= password_to_check.data
        if re.search('[0-9]',password) is None:
            raise ValidationError("Password must contain letters a-z, A-Z and 0-9.")
        elif re.search('[A-Z|a-z]',password) is None:
            raise ValidationError("Password must contain letters a-z, A-Z and 0-9.")

    name = StringField(label='Name',validators=[DataRequired()])
    last_name = StringField(label='Lastname',validators=[DataRequired()])
    identity_card = StringField(label='identity_card',validators=[DataRequired(),Length(min=13,max=13)])
    email_address = StringField(label='email',validators=[Email(),DataRequired()])
    password = PasswordField(label='Password',validators=[Length(min=8,message='Password must contain letters a-z, A-Z and 0-9, minimum length of 8 characters.'),DataRequired()])
    # password = PasswordField(label='Password',validators=[Length(min=8,message='รหัสผ่านต้องประกอบด้วยตัวอักษร a-z, A-Z และ 0-9 ความยาวขั้นต่ำ 8 ตัวอักษร'),DataRequired(),AlphaNumeric('ห้ามมีอักขระพิเศษ เช่น!@#$%^&*()_-+')])
    confirm_password = PasswordField(label='Confirm password',validators=[EqualTo('password','Passwords do not match Please enter again'),DataRequired()])
    submit1 = SubmitField(label='create account')


class ResetPassword(FlaskForm):

    def validate_email(self,email_to_check):
        email = Customer_register.query.filter_by(email=email_to_check.data).first()
        if not email:
            raise ValidationError('อีเมลไม่ถูกต้อง กรุณากรอกใหม่อีกครั้ง')
    
    def validate_password(self,password_to_check):
        password= password_to_check.data
        if re.search('[0-9]',password) is None:
            raise ValidationError("รหัสผ่านต้องประกอบด้วยตัวอักษร a-z, A-Z และ 0-9")
        elif re.search('[A-Z|a-z]',password) is None:
            raise ValidationError("รหัสผ่านต้องประกอบด้วยตัวอักษร a-z, A-Z และ 0-9")

    email = StringField(label='Email',validators=[Email(),DataRequired()])
    password = PasswordField(label='Password',validators=[Length(min=8,message='รหัสผ่านต้องประกอบด้วยตัวอักษร a-z, A-Z และ 0-9 ความยาวขั้นต่ำ 8 ตัวอักษร'),DataRequired()])
    # password = PasswordField(label='Password',validators=[Length(min=8,message='รหัสผ่านต้องประกอบด้วยตัวอักษร a-z, A-Z และ 0-9 ความยาวขั้นต่ำ 8 ตัวอักษร'),DataRequired(),AlphaNumeric('ห้ามมีอักขระพิเศษ เช่น!@#$%^&*()_-+')])
    confirm_password = PasswordField(label='Confirm Password',validators=[EqualTo('password','รหัสผ่านไม่ตรงกัน กรุณากรอกใหม่'),DataRequired()])


province = ['','กรุงเทพมหานคร', 'สมุทรปราการ', 'นนทบุรี', 'ปทุมธานี', 'พระนครศรีอยุธยา', 'อ่างทอง', 'ลพบุรี', 'สิงห์บุรี',
 'ชัยนาท', 'สระบุรี', 'ชลบุรี', 'ระยอง', 'จันทบุรี', 'ตราด', 'ฉะเชิงเทรา', 'ปราจีนบุรี', 'นครนายก', 'สระแก้ว', 'นครราชสีมา', 
 'บุรีรัมย์', 'สุรินทร์', 'ศรีสะเกษ', 'อุบลราชธานี', 'ยโสธร', 'ชัยภูมิ', 'อำนาจเจริญ', 'บึงกาฬ', 'หนองบัวลำภู', 'ขอนแก่น', 'อุดรธานี',
  'เลย', 'หนองคาย', 'มหาสารคาม', 'ร้อยเอ็ด', 'กาฬสินธุ์', 'สกลนคร', 'นครพนม', 'มุกดาหาร', 'เชียงใหม่', 'ลำพูน', 'ลำปาง',
   'อุตรดิตถ์', 'แพร่', 'น่าน', 'พะเยา', 'เชียงราย', 'แม่ฮ่องสอน', 'นครสวรรค์', 'อุทัยธานี', 'กำแพงเพชร', 'ตาก', 'สุโขทัย', 'พิษณุโลก',
    'พิจิตร', 'เพชรบูรณ์', 'ราชบุรี', 'กาญจนบุรี', 'สุพรรณบุรี', 'นครปฐม', 'สมุทรสาคร', 'สมุทรสงคราม', 'เพชรบุรี', 'ประจวบคีรีขันธ์',
     'นครศรีธรรมราช', 'กระบี่', 'พังงา', 'ภูเก็ต', 'สุราษฎร์ธานี', 'ระนอง', 'ชุมพร', 'สงขลา', 'สตูล', 'ตรัง', 'พัทลุง', 'ปัตตานี', 'ยะลา', 'นราธิวาส']

class Step3(FlaskForm):

    def validate_identity_card(self,identity_card_to_check):
        if identity_card_to_check != current_user.identity_card:
            raise ValidationError('Please check identity card in profile.')

    card_id = StringField(label='Card Id')
    identity_card = StringField(label='Identity Card',validators=[DataRequired()])
    first_name_th = StringField(label='name th',validators=[DataRequired()])
    last_name_th = StringField(label='lastname th',validators=[DataRequired()])
    first_name_en = StringField(label='name_en',validators=[DataRequired()])
    last_name_en = StringField(label='lastname_en',validators=[DataRequired()])
    birth_date = DateField(label='date',format='%Y-%m-%d',validators=[DataRequired()])
    phone = StringField(label='Phone number',validators=[DataRequired(),Length(max=10)])

    #car registration 1

    license_plate1 = StringField(label='license_plate1',validators=[DataRequired()])
    province_car1 = SelectField(label='province car1',validators=[DataRequired()])
    brand_name1 = SelectField(label='brand name1',validators=[DataRequired()])
    color1 = StringField(label='color1',validators=[DataRequired()])

    #car registration 2

    license_plate2 = StringField(label='license_plate2')
    province_car2 = SelectField(label='province car2')
    brand_name2 = SelectField(label='brand name2')
    color2 = StringField(label='color2')

    #tax invoice home
    unit_home = StringField(label='unit')
    address_home = StringField(label='address home',validators=[DataRequired()])
    village_home = StringField(label='village home',validators=[])
    alley_home = StringField(label='alley home',validators=[])
    road_home = StringField(label='road home',validators=[])
    province_home = SelectField(label='province',validators=[DataRequired()])
    district_home = SelectField(label='district',validators=[DataRequired()])
    sub_district_home = SelectField(label='subdistrict',validators=[DataRequired()])
    postal_code_home = SelectField(label='postalcode',validators=[DataRequired()])
    

    #tax invoice company
    unit_company = StringField(label='unit company')
    identity_com = StringField(label='tax')
    company_name = StringField(label='company name')
    address_company = StringField(label='address company')
    village_company = StringField(label='village company')
    alley_company = StringField(label='alley company')
    road_company = StringField(label='road company')
    province_company = SelectField(label='province company')
    district_company = SelectField(label='district company')
    sub_district_company = SelectField(label='sub district company')
    postal_code_company = SelectField(label='postal code company')

    #file
    copy_id_card = FileField(label='copy idcard',validators=[DataRequired()])
    copy_doc_car1 =FileField(label='copy car1',validators=[DataRequired()])
    copy_doc_car2 = FileField(label='copy car2',validators=[])
    card_member_copy = FileField(label='card member copy',validators=[])
    submit = SubmitField(label='ถัดไป')
    submit_en = SubmitField(label='Next')

class Reserve_step3(FlaskForm):

    def validate_identity_card(self,identity_card_to_check):
        if identity_card_to_check != current_user.identity_card:
            raise ValidationError('Please check identity card in profile.')

    submit = SubmitField(label='ยืนยันการจอง')

    #tax invoice home
    unit_home = StringField(label='unit')
    address_home = StringField(label='address home',validators=[DataRequired()])
    village_home = StringField(label='village home',validators=[])
    alley_home = StringField(label='alley home',validators=[])
    road_home = StringField(label='road home',validators=[])
    province_home = SelectField(label='province',validators=[DataRequired()])
    district_home = SelectField(label='district',validators=[DataRequired()])
    sub_district_home = SelectField(label='subdistrict',validators=[DataRequired()])
    postal_code_home = SelectField(label='postalcode',validators=[DataRequired()])

    #tax invoice company
    unit_company = StringField(label='unit company')
    identity_com = StringField(label='tax')
    company_name = StringField(label='company name')
    address_company = StringField(label='address company')
    village_company = StringField(label='village company')
    alley_company = StringField(label='alley company')
    road_company = StringField(label='road company')
    province_company = SelectField(label='province company')
    district_company = SelectField(label='district company')
    sub_district_company = SelectField(label='sub district company')
    postal_code_company = SelectField(label='postal code company')

class Change_username(FlaskForm):
    name = StringField(label='name')
    last_name = StringField(label='last name')
    submit = SubmitField(label='Save changes')

class Change_identity(FlaskForm):
    identity = StringField(label='identity',validators=[Length(min=13,max=13)])
    submit = SubmitField(label='Save changes')

class Change_phone(FlaskForm):
    phone = StringField(label='phone number')
    submit = SubmitField(label='Save changes')

class Home_form(FlaskForm):
    unit_home1 = StringField(label='unit1')
    address_no = StringField(label='บ้านเลขที่')
    village = StringField(label='หมู่บ้าน')
    district = SelectField(label='อำเภอ')
    province = SelectField(label='จังหวัด')
    sub_district = SelectField('ตำบล')
    postal_code = SelectField(label='รหัสไปรษณี')
    submit = SubmitField(label='Save changes')

class Company_form(FlaskForm):
    unit_company1 = StringField(label='unit company1')
    identity_com1 = StringField(label='tax')
    company_no = StringField(label='เลขที่อยู่บริษัท')
    company_village = StringField(label='หมู่บ้าน')
    company_district = SelectField(label='อำเภอ')
    company_province = SelectField(label='จังหวัด')
    company_sub_district = SelectField(label='ตำบล')
    company_postal_code = SelectField(label='รหัสไปรษณี')
    submit = SubmitField(label='Save changes')

class Home_form2(FlaskForm):
    unit_home2 = StringField(label='unit2')
    address_no_card2 = StringField(label='บ้านเลขที่')
    village_card2 = StringField(label='หมู่บ้าน')
    district_card2 = SelectField(label='อำเภอ')
    province_card2 = SelectField(label='จังหวัด')
    sub_district_card2 = SelectField('ตำบล')
    postal_code_card2 = SelectField(label='รหัสไปรษณี')
    submit = SubmitField(label='Save changes')

class Company_form2(FlaskForm):
    unit_company2 = StringField(label='unit company2')
    identity_com2 = StringField(label='tax')
    company_no_card2 = StringField(label='เลขที่อยู่บริษัท')
    company_village_card2 = StringField(label='หมู่บ้าน')
    company_district_card2 = SelectField(label='อำเภอ')
    company_province_card2 = SelectField(label='จังหวัด')
    company_sub_district_card2 = SelectField(label='ตำบล')
    company_postal_code_card2 = SelectField(label='รหัสไปรษณี')
    submit = SubmitField(label='Save changes')

class Car_form(FlaskForm):
    brand_name1 = SelectField(label='brand name')
    color1 = StringField(label='color')
    license_plate1 = StringField(label='license plate')
    province_car1 = SelectField(label='province')
    submit = SubmitField(label='Save changes')

class Car_form2(FlaskForm):
    brand_name2 = SelectField(label='brand name')
    color2 = StringField(label='color')
    license_plate2 = StringField(label='license plate')
    province_car2 = SelectField(label='province')
    submit_car2 = SubmitField(label='Save changes')

class Car_form3(FlaskForm):
    brand_name1_card2 = SelectField(label='brand name')
    color1_card2 = StringField(label='color')
    license_plate1_card2 = StringField(label='license plate')
    province_car1_card2 = SelectField(label='province')
    submit = SubmitField(label='Save changes')

class Car_form4(FlaskForm):
    brand_name2_card2 = SelectField(label='brand name')
    color2_card2 = StringField(label='color')
    license_plate2_card2 = StringField(label='license plate')
    province_car2_card2 = SelectField(label='province')
    submit = SubmitField(label='Save changes')

class Dashboard(FlaskForm):
    service_type = SelectField(label='ประเภทบริการ',choices=[
        ('--ประเภทบริการ--',''),('สมัครใหม่','สมัครใหม่'),
        ('ต่ออายุ','ต่ออายุ'),('ยกเลิก','ยกเลิก')],validators=[DataRequired()])
    parking_name = SelectField(label='ลานจอด',validators=[DataRequired()]) #for parking_log
    cus_id = StringField(label='รหัสลูกค้า',validators=[DataRequired()])
    card_id = StringField(label='รหัสบัตร',validators=[DataRequired()])
    parking_register_date = DateField(label='วันที่สมัคร',format='%Y-%m-%d',validators=[DataRequired()])
    first_name = StringField(label='ชือ่ลูกค้า',validators=[DataRequired()])
    last_name = StringField(label='นามสกุลลูกค้า',validators=[DataRequired()])
    phone = StringField(label='เบอร์โทรติดต่อ',validators=[DataRequired()])
    vcard_type = SelectField(label='ประเภทบัตร',choices=[
        ('--ประเภทบัตร--',''),('AFC','AFC'),
        ('TAFF','TAFF'),('CIT','CIT'),('JOWIT','JOWIT')],validators=[DataRequired()])
    month = StringField(label='จำนวนเดือน',validators=[DataRequired()])
    start_date = StringField(label='วันที่เริ่มต้น',validators=[DataRequired()])
    deposit = StringField(label='ค่ามัดจำบัตร',validators=[DataRequired()])
    service_price = StringField(label='ค่าบริการ',validators=[DataRequired()])
    vat = StringField(label='vat',validators=[DataRequired()])
    total = StringField(label='ค่าบริการรวม',validators=[DataRequired()])
    copy_id_card = FileField(label='เอกสารสำเนาบัตรประชาชน',validators=[DataRequired()])
    copy_doc_car = FileField(label='เอกสารสำเนารถ',validators=[DataRequired()])
    verify_status = SelectField(label='สถานะการตรวจสอบ',choices=[
        ('--สถานะการตรวจสอบ--',''),('ผ่านการตรวจสอบ',1),('ไม่ผ่านการตรวจสอบ',2),('รอจองคิว',3),
        ('จองคิว',4),('ยกเลิก',5)],validators=[DataRequired()]) #for parking_log
    notificate = StringField(label='แจ้งเตือน',validators=[DataRequired()])
    payment_name = SelectField(label='ช่องทางการชำระเงิน',choices=[
        ('เงินสด',1),('บัตรเครดิต',2),('ทรูมันนี่',5),('QR Code',3),('ผูกบัญชี',4)
        ],validators=[DataRequired()])
    payment_status = SelectField(label='สถานะการชำระเงิน',choices=[('--สถานะการชำระเงิน--',''),('ชำระเงิน',1),('ไม่ชำระเงิน',0)],validators=[DataRequired()])
    cancel = SelectField(label='ยกเลิก',choices=[('--ยกเลิก--',''),('ค่ามัดจำบัตร','ค่ามัดจำบัตร'),('สถานะคินบัตร','สถานะคินบัตร'),('หมายเหตุ','หมายเหตุ')],validators=[DataRequired()])
    payment_date = DateField(label='วันที่ชำระเงิน',validators=[DataRequired()])
    card_last_read_date = DateField(label='วันที่อ่านบัตรล่าสุด',validators=[DataRequired()])
    return_card_status = StringField(label='สถานะคืนบัตร',validators=[DataRequired()])
    note = StringField(label='หมายเหตุ')

class Profilepassword(FlaskForm):
    
    def validate_password(self,password_to_check):
        password= password_to_check.data
        if re.search('[0-9]',password) is None:
            raise ValidationError("รหัสผ่านต้องประกอบด้วยตัวอักษร a-z, A-Z และ 0-9")
        elif re.search('[A-Z|a-z]',password) is None:
            raise ValidationError("รหัสผ่านต้องประกอบด้วยตัวอักษร a-z, A-Z และ 0-9")

    password = PasswordField(label='Password',validators=[Length(min=8,message='รหัสผ่านต้องประกอบด้วยตัวอักษร a-z, A-Z และ 0-9 ความยาวขั้นต่ำ 8 ตัวอักษร'),DataRequired()])
    confirm_password = PasswordField(label='Confirm Password',validators=[EqualTo('password','รหัสผ่านไม่ตรงกัน กรุณากรอกใหม่'),DataRequired()])
    submit = SubmitField(label='Save changes')
