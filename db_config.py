from app import app
from flask_mysqldb import MySQL
import os

app.config["MYSQL_HOST"] = os.environ.get('DB_HOST','localhost')
app.config["MYSQL_USER"] = os.environ.get('DB_USER','owner')
app.config["MYSQL_PASSWORD"] = os.environ.get('DB_PASSWORD','jpark1234*')
app.config["MYSQL_DB"] = os.environ.get('DB_NAME','mrtaparking')
app.config['MYSQL_DATABASE_CHARSET'] = 'utf-8'

mysql = MySQL(app)
