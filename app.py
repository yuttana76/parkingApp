from flask import Flask
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
from flask_login import UserMixin,LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from flask_bcrypt import Bcrypt
from flask_cors import CORS

def reset_invoice_number():
    dt = datetime.datetime.today()
    if dt.strftime('%m/%d') == '10/01':
        today = str(int(dt.strftime('%Y')) + 543 +1)[-2:]
        stations = Parking_manage.query.all()
        for station in stations:
            station.start_inv_no = today+'/' + station.parking_branch+'/' + '0000'
        db.session.commit()
        print('success')
        return 'SUCCESS'



app = Flask(__name__, template_folder='templates', static_folder='static')
cors = CORS(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app,session_options={"autoflush": False})
app.config['SQLALCHEMY_DATABASE_URI']="mysql://root:mrta2021@localhost/mrtaparking"
app.config['SQLALCHEMY_POOL_RECYCLE'] = 60
db.Model.metadata.reflect(db.engine)
app.secret_key = "NdesKWazqD-TDocYq4u7qw"
bcrypt = Bcrypt(app)
app.config.from_pyfile('config.cfg')
sched = BackgroundScheduler(daemon=True)
sched.add_job(reset_invoice_number,'cron',hour='0',minute='1')
sched.add_job(reset_invoice_number,'cron',hour='0',minute='10')
sched.start()
mail = Mail(app)
s= URLSafeTimedSerializer('Thisisasecret!')

#file
UPLOAD_FOLDER =r'C:\D\project_mrta_parkingApp\mrta-app\static\image-manage\document'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 20


#login
login_manager = LoginManager(app)
login_manager.login_view = 'index'
login_manager.login_message_category ='danger'
@login_manager.user_loader
def load_user(user_id):
    return Customer_register.query.get(int(user_id))
    

class Customer_register(db.Model,UserMixin):
    __table__ = db.Model.metadata.tables['customer_register']

    def get_id(self):
        return (self.Id)
    
    @property #create password hash
    def password_hash(self):
        return self.password_hash

    @password_hash.setter
    def password_hash(self,plain_text_password):
        self.password = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    def check_password_correction(self,attempted_password): #method check password hash
        return bcrypt.check_password_hash(self.password,attempted_password)

class User_manage(db.Model):
    __table__ = db.Model.metadata.tables['user_manage']


class Parking_member(db.Model):
    __table__ = db.Model.metadata.tables['parking_member']
    def to_json(query_list):
        cols = Parking_member.__table__.columns.keys()
        return [{col:getattr(row,col)for col in cols}for row in query_list]


class Parking_manage(db.Model):
    __table__ = db.Model.metadata.tables['parking_manage']


class Card_member(db.Model):
    __table__ = db.Model.metadata.tables['card_member']

class Carpacity_manage(db.Model):
    __table__ = db.Model.metadata.tables['capacity_manage']

class Parking_log(db.Model):
    __table__ = db.Model.metadata.tables['parking_log']

class Policy(db.Model):
    __table__ = db.Model.metadata.tables['policy']

class News_manage(db.Model):
    __table__ = db.Model.metadata.tables['news_manage']


class Brand(db.Model):
    __table__ = db.Model.metadata.tables['brand']

class Activity_manage(db.Model):
    __table__ = db.Model.metadata.tables['activity_manage']

class Message_box(db.Model):
    __table__ = db.Model.metadata.tables['message_box']

class Login_logout_log(db.Model):
    __table__ = db.Model.metadata.tables['login_logout_log']

#smartparking
class Parking_logvisitor(db.Model):
    __table__ = db.Model.metadata.tables['parking_logvisitor']

class Estamp(db.Model):
    __table__ = db.Model.metadata.tables['estamp']

