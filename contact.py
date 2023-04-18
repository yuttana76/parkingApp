import re
from app import app
from flask import Flask, render_template,request,redirect,url_for,session

from datetime import datetime


from db_config import mysql  # import sql


@app.route('/', methods=['GET', 'POST'])
def contact():
    if request.method=="POST":
        first_name=request.form['first_name']
        last_name=request.form['last_name']
        phone=request.form['phone']
        email=request.form['email']
        type=request.form['type']
        description=request.form['description']

        with mysql.connection.cursor() as cursor:
            sql="""Insert into `contact` (`first_name`,`last_name`,`phone`,`email`,
            `type`,`description`)
            values(%s,%s,%s,%s,%s,%s)"""
            cursor.execute(sql,(first_name, last_name, phone, email, type, description))
            mysql.connection.commit()
            
        return redirect(url_for('contact'))