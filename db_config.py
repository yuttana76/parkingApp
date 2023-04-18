from app import app
from flask_mysqldb import MySQL

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "mrta2021"
app.config["MYSQL_DB"] = "mrtaparking"
app.config['MYSQL_DATABASE_CHARSET'] = 'utf-8'

mysql = MySQL(app)
