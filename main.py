from smartparking.parking.inject import inject
import smartparking.payment.rest
import smartparking.parking.rest
import smartparking.parking.rest_blue_line
import smartparking.payment.rest_blue_line
from pickle import NONE
from posixpath import join
# from flask.typing import AppOrBlueprintKey
from sqlalchemy.sql.base import NO_ARG
from form import Car_form, Car_form2, Car_form3, Car_form4, Change_identity, Change_phone, Change_username, Company_form, Company_form2, Home_form, Home_form2, Profilepassword, RegisterForm, ResetPassword, Step3, Reserve_step3
from app import *
from flask import render_template, request, url_for, redirect, flash, json, jsonify
from province import get_district, get_postcode, get_province, get_subdistrict
from directlink import getDirectlink
from directlinkPD import getDirectlink_pd
from apiGetParkRT import get_api_parking, get_blueline, get_greenline, get_purpleline, find_availability
from flask.globals import session
import datetime
from flask_mail import Message
from itsdangerous import SignatureExpired
from getparking import get_parking_json, get_parking_json2
import main_manage
import main_en
from db_config import mysql  # import sql
from ref2 import genRef2
from get_cus_id import generate_cus_id
from file_customize import custom_file
from flask_login import login_user, current_user, logout_user, login_required
from create_newlist import create_allnews_list, create_home_news, create_api_list
from ktb_Qrcode import text_qr
import hashlib
from status_card import status_card
from payment_card import payment, payment_exp, check_status_card
from user_owned_card import create_company_address, owned_card, create_home_address, randomAlpha_cid, checkCardNotRandom, checkCardNotReMem
import re
from sqlalchemy import or_, and_
import os
from werkzeug.utils import secure_filename
from find_log import find_last_log, reserve, card_reserve
from cgpPayment import paymentCGP
from encrypt import encrypt
from renewTAFF import renew_card_TAFF_orAll, get_numofMonth
from cgpPaymentPD import paymentCGP_PD
from datetime import timedelta
from updatecapacity import capacity_count
# Home Public
#from pushbullet import Pushbullet
#API_KEY = "o.iYJuE1znz07O4LBtOJo2l1SnlqtVHJU0"
#pb = Pushbullet(API_KEY)
import reserveParking
import multiprocessing as mp
from getReserveParking import qr_opengate_timeout
from apiMember import ApiMember
from threading import Thread
from encryptuat import encryptuat
from senddatatolocal import send_data_to_publish_service_with_ordernumber
import random 
import string


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # all station
        data = get_api_parking()
        data_list = create_api_list(data)
        last_data_list = data_list.pop()

        # blueline
        blue = get_blueline()
        blue_count = len(blue)
        blue_line = create_allnews_list(blue)
        last_blue_line = blue_line.pop()

        # purpleline
        purple_line = get_purpleline()
        purple_count = len(purple_line)

        # greenline
        green_line = get_greenline()
        green_count = len(green_line)
        
        total = blue_count + purple_count + green_count

        today = datetime.datetime.today().strftime('%Y-%m-%d')
        # news
        news_activity = Activity_manage.query.filter(
            Activity_manage.activity_type == 1).filter(Activity_manage.activity_status == 'active')\
            .filter(and_(Activity_manage.activity_date <= today, Activity_manage.end_activity >= today)).order_by(Activity_manage.activity_date.desc()).all()
        news_advertise = News_manage.query.filter(
            News_manage.news_type == 1).filter(News_manage.news_status == 'active')\
            .filter(and_(News_manage.news_date <= today, News_manage.end_date >= today)).order_by(News_manage.news_date.desc()).all()
        news_activity = create_home_news(news_activity)
        news_advertise = create_home_news(news_advertise)
        if news_activity != []:
            news_activity_last = news_activity.pop()
        else:
            news_activity_last = []
        if news_advertise != []:
            news_advertise_last = news_advertise.pop()
        else:
            news_advertise_last = []

        return render_template(
            # api
            'home.html', data_list=data_list, last_data_list=last_data_list,
            blue_line=blue_line, last_blue_line=last_blue_line, purple_line=purple_line,
            green_line=green_line, total=total, blue_count=blue_count, purple_count=purple_count, green_count=green_count,
            # new and activity
            news_activity=news_activity, news_activity_last=news_activity_last,
            news_advertise=news_advertise, news_advertise_last=news_advertise_last)

    # ittipon
    if request.method == "POST" and request.form.get('email') != None:
        email = request.form['email']
        password = request.form['repassword']
        account = Customer_register.query.filter_by(
            email=email).order_by(Customer_register.Id.desc()).first()
        # check Customer_register in server
        if account and account.register_status == '1' and account.check_password_correction(attempted_password=password):
            if account.delete_date:
                remaining = datetime.date.today() - account.delete_date
                if remaining.days > 30:
                    db.session.delete(account)
                    db.session.commit()
                    flash('บัญชีนี้ถูกลบเรียบร้อยแล้วกรุณาสมัครบัญชีใหม่',
                          category='danger')
                    return redirect('/')
                else:
                    user_log = Login_logout_log(
                        user=email, login_type='home', ip_address=request.remote_addr, login_datetime=datetime.datetime.today())
                    db.session.add(user_log)
                    db.session.commit()
                    login_user(account)
                    return redirect(url_for('home_2'))
            else:
                user_log = Login_logout_log(
                    user=email, login_type='home', ip_address=request.remote_addr, login_datetime=datetime.datetime.today())
                db.session.add(user_log)
                db.session.commit()
                login_user(account)
                return redirect(url_for('home_2'))
        # check when wrong password
        elif account and account.register_status != '1':
            flash('Please click confirm link in email box.', category='danger')
            return redirect('/')
        # elif Customer_register.query.filter_by(password=password).first():  # check when wrong Customer_register and password
        #     flash('Your email is not correct.',category='danger')
        #     return redirect('/')
        elif Customer_register.query.filter_by(email=email).first():
            flash('Your password is not correct.', category='danger')
            return redirect('/')
        else:
            flash('Please register before login', category='danger')
            return redirect('/')

    if request.method == 'POST' and request.form.get('news_id') != None:
        session['new_id'] = request.form.get('news_id')
        return redirect(url_for('parking_news'))

    if request.method == 'POST' and request.form.get('activity_id') != None:
        session['activity_id'] = request.form.get('activity_id')
        return redirect(url_for('parking_activities'))

    if request.method == 'POST' and request.form.get('station') != None:
        session['station'] = request.form.get('station')
        return redirect(url_for('parking_info'))


@app.route('/home', methods=['GET', 'POST'])  # ittipon
def home_2():
    if request.method == 'GET':
        # all station
        data = get_api_parking()
        data_list = create_api_list(data)
        last_data_list = data_list.pop()

        # blueline
        blue = get_blueline()
        blue_count = len(blue)
        blue_line = create_allnews_list(blue)
        last_blue_line = blue_line.pop()

        # purpleline
        purple_line = get_purpleline()
        purple_count = len(purple_line)

        # greenline
        green_line = get_greenline()
        green_count = len(green_line)

        total = blue_count + purple_count + green_count

        # news
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        news_activity = Activity_manage.query.filter(Activity_manage.activity_status == 'active')\
            .filter(and_(Activity_manage.activity_date <= today, Activity_manage.end_activity >= today))\
            .order_by(Activity_manage.activity_date.desc()).all()
        news_advertise = News_manage.query.filter_by(news_status='active')\
            .filter(and_(News_manage.news_date <= today, News_manage.end_date >= today))\
            .order_by(News_manage.news_date.desc()).all()
        news_activity = create_home_news(news_activity)
        news_advertise = create_home_news(news_advertise)
        if news_activity != []:
            news_activity_last = news_activity.pop()
        else:
            news_activity_last = []
        if news_advertise != []:
            news_advertise_last = news_advertise.pop()
        else:
            news_advertise_last = []

        return render_template(
            # api
            'home2.html', data_list=data_list, last_data_list=last_data_list,
            blue_line=blue_line, last_blue_line=last_blue_line, purple_line=purple_line,
            green_line=green_line, total=total, blue_count=blue_count, purple_count=purple_count, green_count=green_count,
            # new and activity
            news_activity=news_activity, news_activity_last=news_activity_last,
            news_advertise=news_advertise, news_advertise_last=news_advertise_last)
    if request.method == 'POST' and request.form.get('news_id') != None:
        session['new_id'] = request.form.get('news_id')
        return redirect(url_for('parking_news2'))

    if request.method == 'POST' and request.form.get('activity_id') != None:
        session['activity_id'] = request.form.get('activity_id')
        return redirect(url_for('parking_activities2'))

    if request.method == 'POST' and request.form.get('station') != None:
        session['station'] = request.form.get('station')
        return redirect(url_for('parking_info2'))

# confirm register


@app.route('/confirm_email/<token>/<idt>')  # ittipon
def confirm_email(token, idt):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return '<h1> The token is expired!</h1>'

    register_date = datetime.datetime.today()

    update_cus = Customer_register.query.filter_by(
        identity_card=idt).order_by(Customer_register.Id.desc()).first()
    update_cus.register_date = register_date
    update_cus.register_status = '1'
    db.session.commit()

    flash('Register success, Please login.', category='success')
    return redirect('/')

# รายละเอียดข่าวประชาสัมพันธ์


@app.route('/parking-news', methods=['GET', 'POST'])  # ittipon
def parking_news():
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    if request.method == 'GET' and current_user.is_authenticated == False:
        new_id = session.get('new_id')
        new = News_manage.query.filter_by(Id=new_id).first()
        news = News_manage.query.filter_by(
            news_type=1).filter(News_manage.news_status == 'active').filter(and_(News_manage.news_date <= today, News_manage.end_date >= today)).order_by(News_manage.news_date.desc()).all()
        return render_template('parking-news.html', new=new, news=news)

    if request.method == 'GET' and current_user.is_authenticated:
        new_id = session.get('new_id')
        new = News_manage.query.filter_by(Id=new_id).first()
        news = News_manage.query.filter_by(news_status='active').filter(and_(
            News_manage.news_date <= today, News_manage.end_date >= today)).order_by(News_manage.news_date.desc()).all()
        return render_template('parking-news.html', new=new, news=news)

    if request.method == 'POST':
        new_id = request.form.get('new_id')
        session['new_id'] = new_id
        return redirect(url_for('parking_news'))

# รายละเอียดข่าวประชาสัมพันธ์ 2 private


@app.route('/parking-news2', methods=['GET', 'POST'])  # jirapas
def parking_news2():
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    if request.method == 'GET' and current_user.is_authenticated == False:
        new_id = session.get('new_id')
        new = News_manage.query.filter_by(Id=new_id).first()
        news = News_manage.query.filter_by(
            news_type=1).filter(News_manage.news_status == 'active').filter(and_(News_manage.news_date <= today, News_manage.end_date >= today)).order_by(News_manage.news_date.desc()).all()
        return render_template('parking-news2.html', new=new, news=news)

    if request.method == 'GET' and current_user.is_authenticated:
        new_id = session.get('new_id')
        new = News_manage.query.filter_by(Id=new_id).first()
        news = News_manage.query.filter_by(news_status='active').filter(and_(
            News_manage.news_date <= today, News_manage.end_date >= today)).order_by(News_manage.news_date.desc()).all()
        return render_template('parking-news2.html', new=new, news=news)

    if request.method == 'POST':
        new_id = request.form.get('new_id')
        session['new_id'] = new_id
        return redirect(url_for('parking_news2'))

# ข่าวประชาสัมพันธ์ทั้งหมด


@app.route('/parking-all-news', methods=['GET', 'POST'])  # ittipon
def parking_all_news():
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    if request.method == 'GET' and current_user.is_authenticated == False:
        news_list = News_manage.query.filter(
            News_manage.news_type == '1').filter(News_manage.news_status == 'active')\
            .filter(and_(News_manage.news_date <= today, News_manage.end_date >= today))\
            .order_by(News_manage.news_date.desc()).all()
        if news_list == []:
            news_list = News_manage.query.filter(
                News_manage.news_type == '1').filter(News_manage.news_status == 'active')\
                .order_by(News_manage.news_date.desc()).all()
        all_news = create_allnews_list(news_list)
        if all_news != []:
            last_row_news = all_news.pop()
        else:
            last_row_news = []
        return render_template('parking-all-news.html', all_news=all_news, last_row_news=last_row_news)

    elif request.method == 'GET' and current_user.is_authenticated:
        news_list = News_manage.query.filter_by(news_status='active')\
            .filter(and_(News_manage.news_date <= today, News_manage.end_date >= today))\
            .order_by(News_manage.news_date.desc()).all()
        all_news = create_allnews_list(news_list)
        if all_news != []:
            last_row_news = all_news.pop()
        else:
            last_row_news = []
        return render_template('parking-all-news.html', all_news=all_news, last_row_news=last_row_news)

    if request.method == 'POST':
        new_id = request.form.get('news_id')
        session['new_id'] = new_id
        return redirect(url_for('parking_news'))


# ข่าวประชาสัมพันธ์ทั้งหมด 2  private


@app.route('/parking-all-news2', methods=['GET', 'POST'])  # jirapas
def parking_all_news2():
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    if request.method == 'GET' and current_user.is_authenticated == False:
        news_list = News_manage.query.filter(
            News_manage.news_type == '1').filter(News_manage.news_status == 'active')\
            .filter(and_(News_manage.news_date <= today, News_manage.end_date >= today))\
            .order_by(News_manage.news_date.desc()).all()
        if news_list == []:
            news_list = News_manage.query.filter(
                News_manage.news_type == '1').filter(News_manage.news_status == 'active')\
                .order_by(News_manage.news_date.desc()).all()
        all_news = create_allnews_list(news_list)
        if all_news != []:
            last_row_news = all_news.pop()
        else:
            last_row_news = []
        return render_template('parking-all-news2.html', all_news=all_news, last_row_news=last_row_news)

    elif request.method == 'GET' and current_user.is_authenticated:
        news_list = News_manage.query.filter_by(news_status='active')\
            .filter(and_(News_manage.news_date <= today, News_manage.end_date >= today))\
            .order_by(News_manage.news_date.desc()).all()
        all_news = create_allnews_list(news_list)
        if all_news != []:
            last_row_news = all_news.pop()
        else:
            last_row_news = []
        return render_template('parking-all-news2.html', all_news=all_news, last_row_news=last_row_news)

    if request.method == 'POST':
        new_id = request.form.get('news_id')
        session['new_id'] = new_id
        return redirect(url_for('parking_news2'))


# รายละเอียดกิจกรรม


@app.route('/parking-activities', methods=['GET', 'POST'])  # ittipon
def parking_activities():
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    if request.method == 'GET' and current_user.is_authenticated == False:
        activity_id = session.get('activity_id')
        activity = Activity_manage.query.filter_by(Id=activity_id).first()
        activities = Activity_manage.query.filter_by(
            activity_type=1).filter(Activity_manage.activity_status == 'active')\
            .filter(and_(Activity_manage.activity_date <= today, Activity_manage.end_activity >= today))\
            .order_by(Activity_manage.activity_date.desc()).all()
        # if activities == []:
        #     activities = Activity_manage.query.filter_by(activity_type = '1').filter(Activity_manage.activity_status =='active')\
        #         .order_by(Activity_manage.activity_date.desc()).all()
        return render_template('parking-activities.html', activity=activity, activities=activities)

    elif request.method == 'GET' and current_user.is_authenticated:
        activity_id = session.get('activity_id')
        activity = Activity_manage.query.filter_by(Id=activity_id).first()
        activities = Activity_manage.query.filter(Activity_manage.activity_status == 'active')\
            .filter(and_(Activity_manage.activity_date <= today, Activity_manage.end_activity >= today))\
            .order_by(Activity_manage.activity_date.desc()).all()
        # if activities == []:
        #     activities = Activity_manage.query.filte_by(activity_status = 'active')\
        #         .order_by(Activity_manage.activity_date.desc()).all()
        return render_template('parking-activities.html', activity=activity, activities=activities)

    if request.method == 'POST':
        activity_id = request.form.get('activity_id')
        session['activity_id'] = activity_id
        return redirect(url_for('parking_activities'))
    return render_template('parking-activities.html')


# รายละเอียดกิจกรรม 2 private


@app.route('/parking-activities2', methods=['GET', 'POST'])  # ittipon
def parking_activities2():
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    if request.method == 'GET' and current_user.is_authenticated == False:
        activity_id = session.get('activity_id')
        activity = Activity_manage.query.filter_by(Id=activity_id).first()
        activities = Activity_manage.query.filter_by(
            activity_type=1).filter(Activity_manage.activity_status == 'active')\
            .filter(and_(Activity_manage.activity_date <= today, Activity_manage.end_activity >= today))\
            .order_by(Activity_manage.activity_date.desc()).all()
        # if activities == []:
        #     activities = Activity_manage.query.filter_by(activity_type = '1').filter(Activity_manage.activity_status =='active')\
        #         .order_by(Activity_manage.activity_date.desc()).all()
        return render_template('parking-activities2.html', activity=activity, activities=activities)

    elif request.method == 'GET' and current_user.is_authenticated:
        activity_id = session.get('activity_id')
        activity = Activity_manage.query.filter_by(Id=activity_id).first()
        activities = Activity_manage.query.filter(Activity_manage.activity_status == 'active')\
            .filter(and_(Activity_manage.activity_date <= today, Activity_manage.end_activity >= today))\
            .order_by(Activity_manage.activity_date.desc()).all()
        # if activities == []:
        #     activities = Activity_manage.query.filte_by(activity_status = 'active')\
        #         .order_by(Activity_manage.activity_date.desc()).all()
        return render_template('parking-activities2.html', activity=activity, activities=activities)

    if request.method == 'POST':
        activity_id = request.form.get('activity_id')
        session['activity_id'] = activity_id
        return redirect(url_for('parking_activities2'))
    return render_template('parking-activities2.html')


# กิจกรรมทั้งหมด


@app.route('/parking-all-activities', methods=['GET', 'POST'])  # ittipon
def parking_all_activities():
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    if request.method == 'GET' and current_user.is_authenticated == False:
        activity_list = Activity_manage.query.filter(
            Activity_manage.activity_type == '1').filter(Activity_manage.activity_status == 'active')\
            .filter(and_(Activity_manage.activity_date <= today, Activity_manage.end_activity >= today))\
            .order_by(Activity_manage.activity_date.desc()).all()
        activities = create_allnews_list(activity_list)
        if activities != []:
            last_row_activities = activities.pop()
        else:
            last_row_activities = []
        return render_template('parking-all-activities.html', activities=activities, last_row_activities=last_row_activities)

    elif request.method == 'GET' and current_user.is_authenticated:
        activity_list = Activity_manage.query.filter(Activity_manage.activity_status == 'active')\
            .filter(and_(Activity_manage.activity_date <= today, Activity_manage.end_activity >= today))\
            .order_by(Activity_manage.activity_date.desc()).all()
        activities = create_allnews_list(activity_list)
        if activities != []:
            last_row_activities = activities.pop()
        else:
            last_row_activities = []
        return render_template('parking-all-activities.html', activities=activities, last_row_activities=last_row_activities)

    if request.method == 'POST':
        activity_id = request.form.get('activity_id')
        session['activity_id'] = activity_id
        return redirect(url_for('parking_activities'))


# กิจกรรมทั้งหมด 2 private


@app.route('/parking-all-activities2', methods=['GET', 'POST'])  # jirapas
def parking_all_activities2():
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    if request.method == 'GET' and current_user.is_authenticated == False:
        activity_list = Activity_manage.query.filter(
            Activity_manage.activity_type == 1).filter(Activity_manage.activity_status == 'active')\
            .filter(and_(Activity_manage.activity_date <= today, Activity_manage.end_activity >= today))\
            .order_by(Activity_manage.activity_date.desc()).all()
        activities = create_allnews_list(activity_list)
        if activities != []:
            last_row_activities = activities.pop()
        else:
            last_row_activities = []
        return render_template('parking-all-activities2.html', activities=activities, last_row_activities=last_row_activities)

    elif request.method == 'GET' and current_user.is_authenticated:
        activity_list = Activity_manage.query.filter(Activity_manage.activity_status == 'active')\
            .filter(and_(Activity_manage.activity_date <= today, Activity_manage.end_activity >= today))\
            .order_by(Activity_manage.activity_date.desc()).all()
        activities = create_allnews_list(activity_list)
        if activities != []:
            last_row_activities = activities.pop()
        else:
            last_row_activities = []
        return render_template('parking-all-activities2.html', activities=activities, last_row_activities=last_row_activities)

    if request.method == 'POST':
        activity_id = request.form.get('activity_id')
        session['activity_id'] = activity_id
        return redirect(url_for('parking_activities2'))


# Home Private
@app.route('/home-private', methods=['GET', 'POST'])  # ittipon
@login_required
def home_private():
    if request.method == 'GET':
        card = owned_card(current_user.identity_card)
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        user_owned_card = len(card)
        # query private news
        news = News_manage.query.filter_by(
            news_type=2).filter(News_manage.news_status == 'active')\
            .filter(and_(News_manage.news_date <= today, News_manage.end_date >= today))\
            .order_by(News_manage.news_date.desc()).all()
        # not owned card
        if user_owned_card == 0:
            return render_template('home-private.html', user_owned_card=user_owned_card, news=news)

        # not owned 1card
        if user_owned_card == 1:
            card1 = card[0]
            station_name = Parking_manage.query.filter_by(
                parking_code=card1.parking_code).first().parking_name
            card_id = card1.card_id
            card_name = card1.first_name_th
            card_last_name = card1.last_name_th
            exp = card1.card_expire_date
            print(card1.card_id)
            print(card1.parking_code)
            print(card1.identity_card)
            log1 = Parking_log.query.filter(Parking_log.card_id == card1.card_id)\
                .filter(Parking_log.parking_code == card1.parking_code).filter(Parking_log.identity_card == card1.identity_card).order_by(Parking_log.Id.desc()).first()
            status = status_card(log1.verify_status)
            vcard_type = card1.vcard_type
            if status == 'ผ่านการตรวจสอบ' and log1.payment_status == '1':
                status = 'พร้อมใช้งาน'
            elif status == 'ผ่านการตรวจสอบ' and log1.payment_status != '1':
                status = 'ยังไม่ได้ชำระเงิน'
            if card_id.isalpha():
                if vcard_type == "TAFF":
                    card_id = "ติดต่อรับบัตรที่ห้องทำบัตรรายเดือนสถานีศูนย์วัฒฯ"
                elif vcard_type == "CIT":
                    card_id = "ติดต่อรับบัตรที่ห้องทำบัตรรายเดือน"
                elif vcard_type == "JOWIT":
                    card_id = "ติดต่อรับบัตรที่ห้องทำบัตรรายเดือนสถานีเคหะฯ"
            check_status = check_status_card(card1.card_expire_date)
            ######################################################
            if vcard_type == 'TAFF':
                if log1.payment_status == '1':
                    month = log1.month
                    day_remaining = exp - datetime.date.today()
                    seven_date = (card1.card_expire_date +
                                  datetime.timedelta(7)).strftime('%d/%m/%Y')
                    start = log1.service_start_date.strftime('%d/%m/%Y')
                    exp = exp.strftime('%d/%m/%Y')

                    if day_remaining.days < 0:
                        remaining = 0
                        day_remaining = f'บัตรหมดอายุ'
                    elif day_remaining.days >= 0:
                        remaining = day_remaining.days + 1
                        day_remaining = f'จำนวนวันคงเหลือ {remaining} วัน'
                elif log1.payment_status == None:

                    month = 1
                    exp = ''
                    day_remaining = 'จำนวนวันคงเหลือ: '
                    remaining = 0
                    seven_date = log1.lastdate_pay.strftime('%d/%m/%Y')
                    start = f'กรุณาชำระเงินก่อนวันที่ {seven_date}'
                else:
                    if exp:
                        month = log1.month
                        day_remaining = exp - datetime.date.today()
                        seven_date = (card1.card_expire_date +
                                      datetime.timedelta(7)).strftime('%d/%m/%Y')
                        start = log1.service_start_date.strftime('%d/%m/%Y')
                        exp = exp.strftime('%d/%m/%Y')
                        if day_remaining.days < 0:
                            remaining = 0
                            day_remaining = f'บัตรหมดอายุ'
                        elif day_remaining.days >= 0:
                            remaining = day_remaining.days + 1
                            day_remaining = f'จำนวนวันคงเหลือ {remaining} วัน'
                    else:
                        month = 1
                        exp = ''
                        day_remaining = 'จำนวนวันคงเหลือ:'
                        remaining = 0
                        seven_date = log1.lastdate_pay.strftime('%d/%m/%Y')
                        start = f'กรุณาชำระเงินก่อนวันที่ {seven_date}'

            else:
                month = 1
                if log1.payment_status == '1':
                    if card1.card_last_read_date:
                        if card1.card_last_read_date.date() >= log1.payment_date.date():
                            day_remaining = exp - datetime.date.today()
                            seven_date = (
                                card1.card_expire_date + datetime.timedelta(7)).strftime('%d/%m/%Y')
                            start = log1.service_start_date.strftime(
                                '%d/%m/%Y')
                            exp = exp.strftime('%d/%m/%Y')
                            if day_remaining.days < 0:
                                remaining = 0
                                day_remaining = f'บัตรหมดอายุ'
                            elif day_remaining.days >= 0:
                                remaining = day_remaining.days + 1
                                day_remaining = f'จำนวนวันคงเหลือ {remaining} วัน'
                        else:
                            exp = log1.service_start_date + datetime.timedelta(get_numofMonth(
                                log1.service_start_date.year, log1.service_start_date.month))
                            day_remaining = exp - \
                                datetime.datetime.combine(
                                    datetime.datetime.today(), datetime.datetime.min.time())
                            # (exp + datetime.timedelta(7)).strftime('%d/%m/%Y')
                            seven_date = ''
                            start = log1.service_start_date.strftime(
                                '%d/%m/%Y')
                            exp = exp.strftime('%d/%m/%Y')
                            status = 'กรุณานำบัตรมาบันทึก'
                            if day_remaining.days < 0:
                                remaining = 0
                                day_remaining = f'บัตรหมดอายุ'
                            elif day_remaining.days >= 0:
                                remaining = day_remaining.days + 1
                                day_remaining = f'จำนวนวันคงเหลือ {remaining} วัน'
                    else:
                        exp = log1.service_start_date + datetime.timedelta(get_numofMonth(
                            log1.service_start_date.year, log1.service_start_date.month))
                        if log1.service_start_date > datetime.datetime.today():
                            day_remaining = exp - log1.service_start_date
                        else:
                            day_remaining = exp - \
                                datetime.datetime.combine(
                                    datetime.datetime.today(), datetime.datetime.min.time())
                        # (exp + datetime.timedelta(7)).strftime('%d/%m/%Y')
                        seven_date = ''
                        start = log1.service_start_date.strftime('%d/%m/%Y')
                        exp = exp.strftime('%d/%m/%Y')
                        status = 'กรุณานำบัตรมาบันทึก'
                        if day_remaining.days < 0:
                            remaining = 0
                            day_remaining = f'บัตรหมดอายุ'
                        elif day_remaining.days >= 0:
                            remaining = day_remaining.days + 1
                            day_remaining = f'จำนวนวันคงเหลือ {remaining} วัน'

                elif log1.payment_status == None:
                    exp = ''
                    day_remaining = 'จำนวนวันคงเหลือ: '
                    remaining = 0
                    seven_date = log1.lastdate_pay.strftime('%d/%m/%Y')
                    start = f'กรุณาชำระเงินก่อนวันที่ {seven_date}'

                else:
                    if exp:
                        day_remaining = exp - datetime.date.today()
                        seven_date = (card1.card_expire_date +
                                      datetime.timedelta(7)).strftime('%d/%m/%Y')
                        start = log1.service_start_date.strftime('%d/%m/%Y')
                        exp = exp.strftime('%d/%m/%Y')
                        if day_remaining.days < 0:
                            remaining = 0
                            day_remaining = f'บัตรหมดอายุ'
                        elif day_remaining.days >= 0:
                            remaining = day_remaining.days + 1
                            day_remaining = f'จำนวนวันคงเหลือ {remaining} วัน'
                    else:
                        exp = ''
                        day_remaining = 'จำนวนวันคงเหลือ:'
                        remaining = 0
                        seven_date = log1.lastdate_pay.strftime('%d/%m/%Y')
                        start = f'กรุณาชำระเงินก่อนวันที่ {seven_date}'
            #######################################################
            if log1.verify_status == '6':
                seven_date = 'xx/xx/xx'
                start = 'xx/xx/xx'
            elif log1.verify_status == '3':
                seven_date = '-'
                start = '-'
            fullname = f'{card1.first_name_th} {card1.last_name_th}'
            register_date = card1.parking_register_date.strftime('%d/%m/%Y')

            return render_template('home-private.html', news=news, register_date=register_date, start=start, check_status=check_status,
                                   user_owned_card=user_owned_card, station_name=station_name, fullname=fullname, month=month,
                                   card_name=card_name, card_last_name=card_last_name, exp=exp, card_id=card_id, vcard_type=vcard_type,
                                   day_remaining=day_remaining, remaining=remaining, status=status, seven_date=seven_date)

        # owned 2 card
        if user_owned_card == 2:
            card1 = card[0]
            card2 = card[1]
            # first_card
            station_name = Parking_manage.query.filter_by(
                parking_code=card1.parking_code).first().parking_name
            card_id = card1.card_id
            card_name = card1.first_name_th
            card_last_name = card1.last_name_th
            exp = card1.card_expire_date
            vcard_type1 = card1.vcard_type
            log1 = Parking_log.query.filter(Parking_log.card_id == card1.card_id)\
                .filter(Parking_log.parking_code == card1.parking_code).filter(Parking_log.identity_card == card1.identity_card).order_by(Parking_log.Id.desc()).first()
            status = status_card(log1.verify_status)
            if status == 'ผ่านการตรวจสอบ' and log1.payment_status == '1':
                status = 'พร้อมใช้งาน'
            elif status == 'ผ่านการตรวจสอบ' and log1.payment_status != '1':
                status = 'ยังไม่ได้ชำระเงิน'
            check_status = check_status_card(card1.card_expire_date)
            if card_id.isalpha():
                if vcard_type1 == "TAFF":
                    card_id = "ติดต่อรับบัตรที่ห้องทำบัตรรายเดือนสถานีศูนย์วัฒฯ"
                elif vcard_type1 == "CIT":
                    card_id = "ติดต่อรับบัตรที่ห้องทำบัตรรายเดือน"
                elif vcard_type1 == "JOWIT":
                    card_id = "ติดต่อรับบัตรที่ห้องทำบัตรรายเดือนสถานีเคหะฯ"
            ##########################################################################
            if vcard_type1 == 'TAFF':
                if log1.payment_status == '1':
                    month = log1.month
                    day_remaining = exp - datetime.date.today()
                    seven_date = (card1.card_expire_date +
                                  datetime.timedelta(7)).strftime('%d/%m/%Y')
                    start = log1.service_start_date.strftime('%d/%m/%Y')
                    exp = exp.strftime('%d/%m/%Y')

                    if day_remaining.days < 0:
                        remaining = 0
                        day_remaining = f'บัตรหมดอายุ'
                    elif day_remaining.days >= 0:
                        remaining = day_remaining.days + 1
                        day_remaining = f'จำนวนวันคงเหลือ {remaining} วัน'
                elif log1.payment_status == None:
                    month = 1
                    exp = ''
                    day_remaining = 'จำนวนวันคงเหลือ: '
                    remaining = 0
                    seven_date = log1.lastdate_pay.strftime('%d/%m/%Y')
                    start = f'กรุณาชำระเงินก่อนวันที่ {seven_date}'
                else:
                    if exp:
                        month = log1.month
                        day_remaining = exp - datetime.date.today()
                        seven_date = (card1.card_expire_date +
                                      datetime.timedelta(7)).strftime('%d/%m/%Y')
                        start = log1.service_start_date.strftime('%d/%m/%Y')
                        exp = exp.strftime('%d/%m/%Y')
                        if day_remaining.days < 0:
                            remaining = 0
                            day_remaining = f'บัตรหมดอายุ'
                        elif day_remaining.days >= 0:
                            remaining = day_remaining.days + 1
                            day_remaining = f'จำนวนวันคงเหลือ {remaining} วัน'
                    else:
                        month = 1
                        exp = ''
                        day_remaining = 'จำนวนวันคงเหลือ:'
                        remaining = 0
                        seven_date = log1.lastdate_pay.strftime('%d/%m/%Y')
                        start = f'กรุณาชำระเงินก่อนวันที่ {seven_date}'

            else:
                month = 1
                if log1.payment_status == '1':
                    if card1.card_last_read_date:
                        if card1.card_last_read_date.date() >= log1.payment_date.date():
                            day_remaining = exp - datetime.date.today()
                            seven_date = (
                                card1.card_expire_date + datetime.timedelta(7)).strftime('%d/%m/%Y')
                            start = log1.service_start_date.strftime(
                                '%d/%m/%Y')
                            exp = exp.strftime('%d/%m/%Y')
                            if day_remaining.days < 0:
                                remaining = 0
                                day_remaining = f'บัตรหมดอายุ'
                            elif day_remaining.days >= 0:
                                remaining = day_remaining.days + 1
                                day_remaining = f'จำนวนวันคงเหลือ {remaining} วัน'
                        else:
                            exp = log1.service_start_date + datetime.timedelta(get_numofMonth(
                                log1.service_start_date.year, log1.service_start_date.month))
                            day_remaining = exp - \
                                datetime.datetime.combine(
                                    datetime.datetime.today(), datetime.datetime.min.time())
                            # (exp + datetime.timedelta(7)).strftime('%d/%m/%Y')
                            seven_date = ''
                            start = log1.service_start_date.strftime(
                                '%d/%m/%Y')
                            exp = exp.strftime('%d/%m/%Y')
                            status = 'กรุณานำบัตรมาบันทึก'
                            if day_remaining.days < 0:
                                remaining = 0
                                day_remaining = f'บัตรหมดอายุ'
                            elif day_remaining.days >= 0:
                                remaining = day_remaining.days + 1
                                day_remaining = f'จำนวนวันคงเหลือ {remaining} วัน'
                    else:
                        exp = log1.service_start_date + datetime.timedelta(get_numofMonth(
                            log1.service_start_date.year, log1.service_start_date.month))
                        if log1.service_start_date > datetime.datetime.today():
                            day_remaining = exp - log1.service_start_date
                        else:
                            day_remaining = exp - \
                                datetime.datetime.combine(
                                    datetime.datetime.today(), datetime.datetime.min.time())
                        # (exp + datetime.timedelta(7)).strftime('%d/%m/%Y')
                        seven_date = ''
                        start = log1.service_start_date.strftime('%d/%m/%Y')
                        exp = exp.strftime('%d/%m/%Y')
                        status = 'กรุณานำบัตรมาบันทึก'
                        if day_remaining.days < 0:
                            remaining = 0
                            day_remaining = f'บัตรหมดอายุ'
                        elif day_remaining.days >= 0:
                            remaining = day_remaining.days + 1
                            day_remaining = f'จำนวนวันคงเหลือ {remaining} วัน'

                elif log1.payment_status == None:
                    exp = ''
                    day_remaining = 'จำนวนวันคงเหลือ: '
                    remaining = 0
                    seven_date = log1.lastdate_pay.strftime('%d/%m/%Y')
                    start = f'กรุณาชำระเงินก่อนวันที่ {seven_date}'

                else:
                    if exp:
                        day_remaining = exp - datetime.date.today()
                        seven_date = (card1.card_expire_date +
                                      datetime.timedelta(7)).strftime('%d/%m/%Y')
                        start = log1.service_start_date.strftime('%d/%m/%Y')
                        exp = exp.strftime('%d/%m/%Y')
                        if day_remaining.days < 0:
                            remaining = 0
                            day_remaining = f'บัตรหมดอายุ'
                        elif day_remaining.days >= 0:
                            remaining = day_remaining.days + 1
                            day_remaining = f'จำนวนวันคงเหลือ {remaining} วัน'
                    else:
                        exp = ''
                        day_remaining = 'จำนวนวันคงเหลือ:'
                        remaining = 0
                        seven_date = log1.lastdate_pay.strftime('%d/%m/%Y')
                        start = f'กรุณาชำระเงินก่อนวันที่ {seven_date}'
            #########################################################################
            fullname = f'{card1.first_name_th} {card1.last_name_th}'
            register_date = card1.parking_register_date.strftime('%d/%m/%Y')
            if log1.verify_status == '6':
                seven_date = 'xx/xx/xx'
                start = 'xx/xx/xx'
            elif log1.verify_status == '3':
                seven_date = '-'
                start = '-'
            # second_card
            vcard_type2 = card2.vcard_type
            station_name2 = Parking_manage.query.filter_by(
                parking_code=card2.parking_code).first().parking_name
            card_id2 = card2.card_id
            card_name2 = card2.first_name_th
            card_last_name2 = card2.last_name_th
            exp2 = card2.card_expire_date
            check_status2 = check_status_card(card2.card_expire_date)
            log2 = Parking_log.query.filter(Parking_log.card_id == card2.card_id)\
                .filter(Parking_log.parking_code == card2.parking_code).filter(Parking_log.identity_card == card1.identity_card).order_by(Parking_log.Id.desc()).first()
            status2 = status_card(log2.verify_status)
            if status2 == 'ผ่านการตรวจสอบ' and log2.payment_status == '1':
                status2 = 'พร้อมใช้งาน'
            elif status2 == 'ผ่านการตรวจสอบ' and log2.payment_status != '1':
                status2 = 'ยังไม่ได้ชำระเงิน'
            if card_id2.isalpha():
                if vcard_type2 == "TAFF":
                    card_id2 = "ติดต่อรับบัตรที่ห้องทำบัตรรายเดือนสถานีศูนย์วัฒฯ"
                elif vcard_type2 == "CIT":
                    card_id2 = "ติดต่อรับบัตรที่ห้องทำบัตรรายเดือน"
                elif vcard_type2 == "JOWIT":
                    card_id2 = "ติดต่อรับบัตรที่ห้องทำบัตรรายเดือนสถานีเคหะฯ"
            ######################################################################
            if vcard_type2 == 'TAFF':
                if log2.payment_status == '1':
                    month2 = log2.month
                    day_remaining2 = exp2 - datetime.date.today()
                    seven_date2 = (card2.card_expire_date +
                                   datetime.timedelta(7)).strftime('%d/%m/%Y')
                    start2 = log2.service_start_date.strftime('%d/%m/%Y')
                    exp2 = exp2.strftime('%d/%m/%Y')

                    if day_remaining2.days < 0:
                        remaining2 = 0
                        day_remaining2 = f'บัตรหมดอายุ'
                    elif day_remaining2.days >= 0:
                        remaining2 = day_remaining2.days + 1
                        day_remaining2 = f'จำนวนวันคงเหลือ {remaining2} วัน'
                elif log2.payment_status == None:
                    month2 = 1
                    exp2 = ''
                    day_remaining2 = 'จำนวนวันคงเหลือ: '
                    remaining2 = 0
                    seven_date2 = log2.lastdate_pay.strftime('%d/%m/%Y')
                    start2 = f'กรุณาชำระเงินก่อนวันที่ {seven_date2}'
                else:
                    if exp2:
                        month2 = log2.month
                        day_remaining2 = exp2 - datetime.date.today()
                        seven_date2 = (card2.card_expire_date +
                                       datetime.timedelta(7)).strftime('%d/%m/%Y')
                        start2 = log2.service_start_date.strftime('%d/%m/%Y')
                        exp2 = exp2.strftime('%d/%m/%Y')
                        if day_remaining2.days < 0:
                            remaining2 = 0
                            day_remaining2 = f'บัตรหมดอายุ'
                        elif day_remaining2.days >= 0:
                            remaining2 = day_remaining2.days + 1
                            day_remaining2 = f'จำนวนวันคงเหลือ {remaining2} วัน'
                    else:
                        month2 = 1
                        exp2 = ''
                        day_remaining2 = 'จำนวนวันคงเหลือ:'
                        remaining2 = 0
                        seven_date2 = log2.lastdate_pay.strftime('%d/%m/%Y')
                        start2 = f'กรุณาชำระเงินก่อนวันที่ {seven_date2}'

            else:
                month2 = 1
                if log2.payment_status == '1':
                    if card2.card_last_read_date:
                        if card2.card_last_read_date.date() >= log2.payment_date.date():
                            day_remaining2 = exp2 - datetime.date.today()
                            seven_date2 = (
                                card2.card_expire_date + datetime.timedelta(7)).strftime('%d/%m/%Y')
                            start2 = log2.service_start_date.strftime(
                                '%d/%m/%Y')
                            exp2 = exp2.strftime('%d/%m/%Y')
                            if day_remaining2.days < 0:
                                remaining2 = 0
                                day_remaining2 = f'บัตรหมดอายุ'
                            elif day_remaining2.days >= 0:
                                remaining2 = day_remaining2.days + 1
                                day_remaining2 = f'จำนวนวันคงเหลือ {remaining2} วัน'
                        else:
                            exp2 = log2.service_start_date + datetime.timedelta(get_numofMonth(
                                log2.service_start_date.year, log2.service_start_date.month))
                            day_remaining2 = exp - \
                                datetime.datetime.combine(
                                    datetime.datetime.today(), datetime.datetime.min.time())
                            # (exp2 + datetime.timedelta(7)).strftime('%d/%m/%Y')
                            seven_date2 = ''
                            start2 = log2.service_start_date.strftime(
                                '%d/%m/%Y')
                            exp2 = exp2.strftime('%d/%m/%Y')
                            status2 = 'กรุณานำบัตรมาบันทึก'
                            if day_remaining2.days < 0:
                                remaining2 = 0
                                day_remaining2 = f'บัตรหมดอายุ'
                            elif day_remaining2.days >= 0:
                                remaining2 = day_remaining2.days + 1
                                day_remaining2 = f'จำนวนวันคงเหลือ {remaining2} วัน'
                    else:
                        exp2 = log2.service_start_date + datetime.timedelta(get_numofMonth(
                            log2.service_start_date.year, log2.service_start_date.month))
                        if log2.service_start_date > datetime.datetime.today():
                            day_remaining2 = exp2 - log2.service_start_date
                        else:
                            day_remaining2 = exp2 - \
                                datetime.datetime.combine(
                                    datetime.datetime.today(), datetime.datetime.min.time())
                        # (exp2 + datetime.timedelta(7)).strftime('%d/%m/%Y')
                        seven_date2 = ''
                        start2 = log2.service_start_date.strftime('%d/%m/%Y')
                        exp2 = exp2.strftime('%d/%m/%Y')
                        status2 = 'กรุณานำบัตรมาบันทึก'
                        if day_remaining2.days < 0:
                            remaining2 = 0
                            day_remaining2 = f'บัตรหมดอายุ'
                        elif day_remaining2.days >= 0:
                            remaining2 = day_remaining2.days + 1
                            day_remaining2 = f'จำนวนวันคงเหลือ {remaining2} วัน'

                elif log2.payment_status == None:
                    exp2 = ''
                    day_remaining2 = 'จำนวนวันคงเหลือ: '
                    remaining2 = 0
                    seven_date2 = log2.lastdate_pay.strftime('%d/%m/%Y')
                    start2 = f'กรุณาชำระเงินก่อนวันที่ {seven_date2}'
                else:
                    if exp2:
                        day_remaining2 = exp2 - datetime.date.today()
                        seven_date2 = (card2.card_expire_date +
                                       datetime.timedelta(7)).strftime('%d/%m/%Y')
                        start2 = log2.service_start_date.strftime('%d/%m/%Y')
                        exp2 = exp2.strftime('%d/%m/%Y')
                        if day_remaining2.days < 0:
                            remaining2 = 0
                            day_remaining2 = f'บัตรหมดอายุ'
                        elif day_remaining2.days >= 0:
                            remaining2 = day_remaining2.days + 1
                            day_remaining2 = f'จำนวนวันคงเหลือ {remaining2} วัน'
                    else:
                        exp2 = ''
                        day_remaining2 = 'จำนวนวันคงเหลือ:'
                        remaining2 = 0
                        seven_date2 = log2.lastdate_pay.strftime('%d/%m/%Y')
                        start2 = f'กรุณาชำระเงินก่อนวันที่ {seven_date2}'
            ######################################################################
            if log2.verify_status == '6':
                seven_date2 = 'xx/xx/xx'
                start2 = 'xx/xx/xx'
            elif log2.verify_status == '3':
                seven_date2 = '-'
                start2 = '-'
            fullname2 = f'{card2.first_name_th} {card2.last_name_th}'
            register_date2 = card2.parking_register_date.strftime('%d/%m/%Y')

            return render_template('home-private.html', news=news, fullname=fullname, fullname2=fullname2, check_status=check_status, start=start, check_status2=check_status2, start2=start2,
                                   user_owned_card=user_owned_card, station_name=station_name, register_date=register_date, register_date2=register_date2, month=month, month2=month2,
                                   card_name=card_name, card_last_name=card_last_name, exp=exp, card_id=card_id, vcard_type1=vcard_type1, day_remaining=day_remaining, remaining=remaining,
                                   station_name2=station_name2, card_name2=card_name2, card_last_name2=card_last_name2, exp2=exp2, vcard_type2=vcard_type2, card_id2=card_id2,
                                   day_remaining2=day_remaining2, remaining2=remaining2, status=status, status2=status2, seven_date=seven_date, seven_date2=seven_date2)

    if request.method == 'POST':
        new_id = request.form.get('newid')
        session['new_id'] = new_id
        return redirect(url_for('parking_news'))


# ข้อมูลอาคารและลานจอดรถ
@app.route('/parking-detail', methods=['GET', 'POST'])  # ittipon
def parking_detail():
    if request.method == 'GET':
        data = get_parking_json2()
        return render_template("parking-detail.html", parkings=data)
    if request.method == 'POST':
        session['station'] = request.form.get('station')
        return redirect(url_for('parking_info'))


@app.route('/parking-detail2', methods=['GET', 'POST'])
def parking_detail2():
    if request.method == 'GET':
        data = get_parking_json2()
        return render_template("parking-detail2.html", parkings=data)
    if request.method == 'POST':
        session['station'] = request.form.get('station')
        return redirect(url_for('parking_info2'))


# ข้อมูลอาคารและลานจอดรถ (รายละเอียดข้อมูล)


@app.route('/parking-info', methods=['GET', 'POST'])  # ittipon
def parking_info():
    if request.method == 'GET':
        station = session.get('station')
        capacity = remaining = Carpacity_manage.query.filter_by(
            parking_name=station).first()
        remaining = capacity.member_remaining
        parking_all = capacity.parking_all
        availability = find_availability(station)
        station_data = Parking_manage.query.filter_by(
            parking_name=station).first()
        map_ = station_data.parking_map
        over_night = f'{station_data.over_night:,}'.split('.')[0]
        use_mrta = str(station_data.use_mrta)
        visitor_price = str(station_data.visitor_price)
        parking_price = f'{station_data.parking_price:,}'.split('.')[0]
        card_lost = str(station_data.card_lost)
        parking_image = station_data.parking_image
        close_date = station_data.office_time
        des_date = station_data.office_time_des
        des_date2 = station_data.office_time_des2
        des_date_eng = station_data.office_time_des_eng
        des_date_eng2 = station_data.office_time_des_eng2
        novisitor = str(station_data.no_visitor_price)
        vcard_type = station_data.vcard_type
        return render_template(
            'parking-info.html', parking_all=parking_all, remaining=remaining, availability=availability, novisitor=novisitor,
            map_=map_, station=station, over_night=over_night, use_mrta=use_mrta,
            visitor_price=visitor_price, parking_price=parking_price, card_lost=card_lost,
            parking_image=parking_image, close_date=close_date, des_date=des_date, des_date2=des_date2, des_date_eng=des_date_eng, des_date_eng2=des_date_eng2,
            vcard_type=vcard_type)


@app.route('/parking-info2', methods=['GET', 'POST'])
def parking_info2():
    if request.method == 'GET':
        station = session.get('station')
        capacity = remaining = Carpacity_manage.query.filter_by(
            parking_name=station).first()
        remaining = capacity.member_remaining
        parking_all = capacity.parking_all
        availability = find_availability(station)
        station_data = Parking_manage.query.filter_by(
            parking_name=station).first()
        map_ = station_data.parking_map
        over_night = f'{station_data.over_night:,}'.split('.')[0]
        use_mrta = str(station_data.use_mrta)
        visitor_price = str(station_data.visitor_price)
        parking_price = f'{station_data.parking_price:,}'.split('.')[0]
        card_lost = str(station_data.card_lost)
        parking_image = station_data.parking_image
        close_date = station_data.office_time
        des_date = station_data.office_time_des
        des_date2 = station_data.office_time_des2
        des_date_eng = station_data.office_time_des_eng
        des_date_eng2 = station_data.office_time_des_eng2
        novisitor = str(station_data.no_visitor_price)
        vcard_type = station_data.vcard_type
        return render_template(
            'parking-info2.html', parking_all=parking_all, remaining=remaining, availability=availability, novisitor=novisitor,
            map_=map_, station=station, over_night=over_night, use_mrta=use_mrta,
            visitor_price=visitor_price, parking_price=parking_price, card_lost=card_lost,
            parking_image=parking_image, close_date=close_date, des_date=des_date, des_date2=des_date2, des_date_eng=des_date_eng, des_date_eng2=des_date_eng2,
            vcard_type=vcard_type)

# สมัครสมาชิก


@app.route('/register', methods=['GET', 'POST'])
def user_register():  # ittipon
    registerform = RegisterForm()
    if registerform.validate_on_submit():
        identity_card = registerform.identity_card.data
        firstname = registerform.name.data
        lastname = registerform.last_name.data
        email = registerform.email_address.data
        password = registerform.password.data
        old_user = Customer_register.query.filter(
            Customer_register.email == email).first()
        if old_user:
            if old_user.register_status == '0':
                token = s.dumps(email, salt='email-confirm')
                msg = Message('Confirm Email',
                              sender='parkandride@mrta.co.th', recipients=[email])
                link = url_for('confirm_email', token=token,
                               idt=identity_card, _external=True)
                msg.body = f'Please click the confirmation link : {link}'
                mail.send(msg)
        # send email
        else:
            newcustomer = Customer_register(identity_card=identity_card, first_name=firstname,
                                            last_name=lastname, email=email, password_hash=password, ip_address=request.remote_addr,
                                            register_status='0', datetime=datetime.datetime.today())
            token = s.dumps(email, salt='email-confirm')
            msg = Message('Confirm Email',
                          sender='parkandride@mrta.co.th', recipients=[email])
            link = url_for('confirm_email', token=token,
                           idt=identity_card, _external=True)
            msg.body = f'Please click the confirmation link : {link}'
            mail.send(msg)
            db.session.add(newcustomer)
            db.session.commit()
        return redirect(url_for('waiting_confirm'))
    if registerform.errors != {}:
        for err_from, err_msg in zip(registerform.errors, registerform.errors.values()):
            flash(f'{re.sub("_"," ",err_from.upper())} : {err_msg}',
                  category='danger')
    return render_template('register.html', registerform=registerform)

# ลืมรหัสผ่าน


@app.route('/reset-password', methods=['GET', 'POST'])  # ittipon
def reset_password():
    form = ResetPassword()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        token = s.dumps(email, salt='password-confirm')
        link = url_for('confirm_password', token=token,
                       email=email, password=password, _external=True)
        msg = Message('Reset Password',
                      sender='parkandride@mrta.co.th', recipients=[email])
        msg.body = f'Please click this link for reset password : {link}'
        mail.send(msg)

        session['reset_password_email'] = email
        session['reset_password_password'] = password
        flash('Please check new password in email', category='info')
        return redirect('/')
    if form.errors != {}:
        for err_from, err_msg in zip(form.errors, form.errors.values()):
            flash(f'{err_from.upper()} : {err_msg}',
                  category='danger')
    return render_template('reset-password.html', form=form)

# confirm reset password


@app.route('/confirm_password/<token>/<email>/<password>')  # ittipon
def confirm_password(token, email, password):
    try:
        emails = s.loads(token, salt='password-confirm', max_age=3600)
    except SignatureExpired:
        return '<h1>Your link is expire, Please try again</h1>'
    # add to database
    cus = Customer_register.query.filter_by(
        email=email).order_by(Customer_register.Id.desc()).first()
    cus.password = bcrypt.generate_password_hash(password).decode('utf-8')
    db.session.commit()
    flash('New password already use.', category='success')

    return redirect('/')

# เงื่อนไขการสมาชิก


@app.route('/agreement')
def agreement():
    return render_template('agreement.html')

# การสมัคร step 1


@app.route('/member-register-step1', methods=['GET', 'POST'])  # ittipon
@login_required
def member_register_step1():
    if request.method == 'GET':
        data = get_parking_json()
        return render_template("member-register-step1.html", parkings=data)

    if request.method == 'POST':
        station = request.form.get('station')
        session['station'] = station
        return redirect('/member-register-step2')

# การสมัคร step 2


@app.route('/member-register-step2')  # ittipon
@login_required
def member_register_step2():
    station = session.get('station')
    rule = Parking_manage.query.filter_by(parking_name=station).first()
    policy = Policy.query.filter_by(policy_name=station).first()
    policy = policy.policy_des.split('\n')
    return render_template('member-register-step2.html', over_night=f'{rule.over_night:,}'.split('.')[0], parking_price=f'{rule.parking_price:,}'.split('.')[0], policy=policy)

# การสมัคร step 3 ittipon!


@app.route('/member-register-step3', methods=['GET', 'POST'])  # ittipon
@login_required
def member_register_step3():
    form = Step3()
    province = get_province()
    form.province_home.choices = [(i, i) for i in province]
    form.province_company.choices = [(i, i) for i in province]
    form.province_car1.choices = [(i, i) for i in province]
    form.province_car2.choices = [(i, i) for i in province]
    form.brand_name1.choices = [(i.brand_name, i.brand_name)
                                for i in Brand.query.all()]
    form.brand_name2.choices = [(i.brand_name, i.brand_name)
                                for i in Brand.query.all()]
    station = session.get('station')
    station = Parking_manage.query.filter_by(parking_name=station).first()
    station_name = station.parking_name
    station_image = station.parking_image
    location = station.location
    price = f'{station.parking_price:,}'.split('.')[0]
    parking_type = station.parking_type_name
    print(parking_type)
    parking_code = station.parking_code

    # check new and old user
    check_user = Parking_member.query.filter_by(
        identity_card=current_user.identity_card).first()
    if check_user:
        check_user = 1
    elif not check_user:
        check_user = 0

    if request.method == 'POST':
        if check_user == 0:
            card_id = form.card_id.data
            if card_id == '' or card_id == None:
                card_id = randomAlpha_cid(8)
            if Parking_member.query.filter_by(identity_card=current_user.identity_card).first():
                cus_id = Parking_member.query.filter_by(
                    card_id=card_id).first().cus_id
            else:
                cus_id = None
            identity_card = form.identity_card.data
            first_name_th = form.first_name_th.data
            last_name_th = form.last_name_th.data
            first_name_en = form.first_name_en.data
            last_name_en = form.last_name_en.data
            birth_date = form.birth_date.data.strftime('%d/%m/%Y')
            phone = form.phone.data
            # car registration 1

            license_plate1 = form.license_plate1.data
            province_car1 = form.province_car1.data
            brand_name1 = form.brand_name1.data
            color1 = form.color1.data

            # car registration 2

            license_plate2 = form.license_plate2.data
            province_car2 = form.province_car2.data
            brand_name2 = form.brand_name2.data
            color2 = form.color2.data

            # tax invoice home
            unit_home = form.unit_home.data
            address_home = form.address_home.data
            village_home = form.village_home.data
            alley_home = form.alley_home.data
            road_home = form.road_home.data
            district_home = form.district_home.data
            sub_district_home = form.sub_district_home.data
            postal_code_home = form.postal_code_home.data
            province_home = form.province_home.data

            # tax invoice company
            unit_company = form.unit_company.data
            identity_com = form.identity_com.data
            company_name = form.company_name.data
            address_company = form.address_company.data
            village_company = form.village_company.data
            alley_company = form.alley_company.data
            road_company = form.road_company.data
            province_company = form.province_company.data
            district_company = form.district_company.data
            sub_district_company = form.sub_district_company.data
            postal_code_company = form.postal_code_company.data

            # file
            copy_id_card = form.copy_id_card.data
            copy_doc_car1 = form.copy_doc_car1.data
            copy_doc_car2 = form.copy_doc_car2.data
            card_member_copy = form.card_member_copy.data

            # custom file

            copy_id_card = custom_file(
                file=copy_id_card, card_id=identity_card, filename='id_card')
            copy_doc_car1 = custom_file(
                file=copy_doc_car1, card_id=identity_card, filename='car1')
            copy_doc_car2 = custom_file(
                file=copy_doc_car2, card_id=identity_card, filename='car2')
            card_member_copy = custom_file(
                file=card_member_copy, card_id=identity_card, filename='membercard')

            # save to sesion
            session_dict = {
                'card_id': card_id, 'identity_card': identity_card, 'first_name_th': first_name_th,
                'last_name_th': last_name_th, 'first_name_en': first_name_en, 'last_name_en': last_name_en,
                'birth_date': birth_date, 'phone': phone, 'cus_id': cus_id,

                'license_plate1': license_plate1, 'province_car1': province_car1,
                'brand_name1': brand_name1, 'color1': color1,

                'license_plate2': license_plate2, 'province_car2': province_car2,
                'brand_name2': brand_name2, 'color2': color2,

                'address_home': address_home, 'village_home': village_home, 'alley_home': alley_home,
                'district_home': district_home, 'sub_district_home': sub_district_home, 'postal_code_home': postal_code_home,
                'road_home': road_home, 'province_home': province_home, 'unit_home': unit_home,

                'company_name': company_name, 'address_company': address_company, 'village_company': village_company, 'alley_company': alley_company,
                'road_company': road_company, 'province_company': province_company, 'district_company': district_company, 'unit_company': unit_company,
                'sub_district_company': sub_district_company, 'postal_code_company': postal_code_company, 'identity_com': identity_com,

                'copy_id_card': copy_id_card, 'copy_doc_car1': copy_doc_car1,
                'copy_doc_car2': copy_doc_car2, 'card_member_copy': card_member_copy
            }
            for i in session_dict.keys():
                session[i] = session_dict[i]

            return redirect(url_for('member_register_step4'))

        if check_user == 1:
            card_id = form.card_id.data
            if card_id == '' or card_id == None:
                card_id = randomAlpha_cid(8)
            identity_card = form.identity_card.data

            # car registration 1
            license_plate1 = form.license_plate1.data
            province_car1 = form.province_car1.data
            brand_name1 = form.brand_name1.data
            color1 = form.color1.data

            # car registration 2

            license_plate2 = form.license_plate2.data
            province_car2 = form.province_car2.data
            brand_name2 = form.brand_name2.data
            color2 = form.color2.data

            # file
            copy_id_card = form.copy_id_card.data
            copy_doc_car1 = form.copy_doc_car1.data
            copy_doc_car2 = form.copy_doc_car2.data
            card_member_copy = form.card_member_copy.data

            # custom file
            copy_id_card = custom_file(
                file=copy_id_card, card_id=identity_card, filename='id_card')
            copy_doc_car1 = custom_file(
                file=copy_doc_car1, card_id=identity_card, filename='car1')
            copy_doc_car2 = custom_file(
                file=copy_doc_car2, card_id=identity_card, filename='car2')
            card_member_copy = custom_file(
                file=card_member_copy, card_id=identity_card, filename='membercard')

            session['card_id'] = card_id
            session['identity_card'] = identity_card
            session['license_plate1'] = license_plate1
            session['province_car1'] = province_car1
            session['brand_name1'] = brand_name1
            session['color1'] = color1
            session['license_plate2'] = license_plate2
            session['province_car2'] = province_car2
            session['brand_name2'] = brand_name2
            session['color2'] = color2
            session['copy_id_card'] = copy_id_card
            session['copy_doc_car1'] = copy_doc_car1
            session['copy_doc_car2'] = copy_doc_car2
            session['card_member_copy'] = card_member_copy

            return redirect(url_for('member_register_step4'))

        if form.errors != {}:
            for err_from, err_msg in zip(form.errors, form.errors.values()):
                flash(
                    f'{err_msg[0]}', category='danger')
                print('*'*50)

    return render_template('member-register-step3.html', form=form, station_name=station_name, location=location, price=price, parking_type=parking_type, check_user=check_user, image=station_image)


# การสมัคร step 4
@app.route('/member-register-step4', methods=['GET', 'POST'])  # ittipon
@login_required
def member_register_step4():
    if request.method == 'POST':

        check_user = Parking_member.query.filter_by(
            identity_card=current_user.identity_card).first()
        if check_user:
            check_user = 1
        elif not check_user:
            check_user = 0
        approve_date = datetime.datetime.today()
        lastdate_pay = approve_date + datetime.timedelta(7)
        # new user logic
        if check_user == 0:
            station = session.get('station')
            station = Parking_manage.query.filter_by(
                parking_name=station).first()
            station_name = station.parking_name
            station_name_en = station.parking_name_eng
            vcard_type = station.vcard_type
            price = int(station.parking_price)
            parking_code = station.parking_code
            id_ = Parking_log.query.filter(Parking_log.Id >= 0).order_by(
                Parking_log.Id.desc()).first().Id + 1
            cus_id = None

            new_log = Parking_log(
                Id=id_,
                cus_id=cus_id,
                card_id=session.get('card_id'),
                input_type=1,
                transaction_type=1,
                identity_card=session.get('identity_card'),
                last_name=session.get('last_name_th'),
                first_name=session.get('first_name_th'),
                phone=session.get('phone'),
                parking_code=parking_code,
                parking_name=station_name,
                parking_type_name=vcard_type,
                amount=price,
                orderNumber=genRef2(a=check_user, id_=id_,
                                    station=parking_code),
                parking_register_date=datetime.datetime.today(),
                approve_date=approve_date,
                lastdate_pay=lastdate_pay
            )

# **************************************************************************************************

            newmember = Parking_member(
                Id=Parking_member.query.order_by(
                    Parking_member.Id.desc()).first().Id + 1,
                cus_id=cus_id,
                card_id=session.get('card_id'),
                identity_card=session.get('identity_card'),
                first_name_th=session.get('first_name_th'),
                last_name_th=session.get('last_name_th'),
                first_name_en=session.get('first_name_en'),
                last_name_en=session.get('last_name_en'),
                birth_date=datetime.datetime.strptime(
                    session.get('birth_date'), '%d/%m/%Y'),
                phone=session.get('phone'),
                parking_code=parking_code,
                parking_register_date=datetime.datetime.today(),
                vcard_type=vcard_type,


                # car registration 1

                license_plate1=session.get('license_plate1'),
                province_car1=session.get('province_car1'),
                brand_name1=session.get('brand_name1'),
                color1=session.get('color1'),

                # car registration 2

                license_plate2=session.get('license_plate2'),
                province_car2=session.get('province_car2'),
                brand_name2=session.get('brand_name2'),
                color2=session.get('color2'),

                # tax invoice home

                unit_home=session.get('unit_home'),
                address_no=session.get('address_home'),
                province=session.get('province_home') if session.get(
                    'province_home') != '' else None,
                district=session.get('district_home') if session.get(
                    'district_home') != '' else None,
                sub_district=session.get('sub_district_home' if session.get(
                    'sub_district_home') != '' else None),
                postal_code=session.get('postal_code_home') if session.get(
                    'postal_code_home') != '' else None,
                village=session.get('village_home'),
                alley=session.get('alley_home'),
                street=session.get('road_home'),

                # tax invoice company
                company_unit=session.get('unit_company'),
                identity_com=session.get('identity_com'),
                company_name=session.get('company_name'),
                company_no=session.get('address_company'),
                company_village=session.get('village_company'),
                company_alley=session.get('alley_company'),
                company_street=session.get('road_company'),
                company_sub_district=session.get('sub_district_company') if session.get(
                    'sub_district_company') != '' else None,
                company_district=session.get('district_company') if session.get(
                    'district_company') != '' else None,
                company_province=session.get('province_company') if session.get(
                    'province_company') != '' else None,
                company_postal_code=session.get('postal_code_company') if session.get(
                    'postal_code_company') != '' else None,

                # file
                copy_id_card=session.get('copy_id_card'),
                copy_doc_car1=session.get('copy_doc_car1'),
                copy_doc_car2=session.get('copy_doc_car2'),
                card_member_copy=session.get('card_member_copy'),

            )
            db.session.add(newmember)
            # old user logic
        elif check_user == 1:
            identity_card = current_user.identity_card
            card_id = session.get('card_id')
            parking_user = Parking_member.query.filter_by(
                identity_card=identity_card).first()
            station = Parking_manage.query.filter_by(
                parking_name=session.get('station')).first()
            station_name = station.parking_name
            station_name_en = station.parking_name_eng
            vcard_type = station.vcard_type
            price = int(station.parking_price)
            parking_code = station.parking_code
            id_ = Parking_log.query.filter(Parking_log.Id >= 0).order_by(
                Parking_log.Id.desc()).first().Id + 1
            cus_id = parking_user.cus_id

            new_log = Parking_log(
                Id=id_,
                cus_id=cus_id,
                card_id=card_id,
                input_type=1,
                transaction_type=1,
                identity_card=identity_card,
                first_name=parking_user.first_name_th,
                last_name=parking_user.last_name_th,
                phone=parking_user.phone,
                parking_code=parking_code,
                parking_name=station_name,
                parking_type_name=vcard_type,
                amount=price,
                orderNumber=genRef2(a=check_user, id_=id_,
                                    station=parking_code),
                parking_register_date=datetime.datetime.today(),
                lastdate_pay=lastdate_pay,
                approve_date=approve_date

            )

# *****************************************************************************
            old_card = Parking_member.query.filter_by(identity_card=identity_card)\
                .filter(Parking_member.parking_code == parking_code).first()
            if not old_card:
                newmember = Parking_member(
                    Id=Parking_member.query.order_by(
                        Parking_member.Id.desc()).first().Id + 1,
                    cus_id=cus_id,
                    card_id=card_id,
                    identity_card=identity_card,
                    first_name_th=parking_user.first_name_th,
                    last_name_th=parking_user.last_name_th,
                    first_name_en=parking_user.first_name_en,
                    last_name_en=parking_user.last_name_en,
                    birth_date=parking_user.birth_date,
                    phone=parking_user.phone,
                    parking_code=parking_code,
                    parking_register_date=datetime.datetime.today(),
                    vcard_type=vcard_type,



                    # car registration 1

                    license_plate1=session.get('license_plate1'),
                    province_car1=session.get('province_car1'),
                    brand_name1=session.get('brand_name1'),
                    color1=session.get('color1'),

                    # car registration 2

                    license_plate2=session.get('license_plate2'),
                    province_car2=session.get('province_car2'),
                    brand_name2=session.get('brand_name2'),
                    color2=session.get('color2'),

                    # tax invoice
                    unit_home=parking_user.unit_home,
                    address_no=parking_user.address_no,
                    province=parking_user.province if parking_user.province != '' else None,
                    district=parking_user.district,
                    sub_district=parking_user.sub_district,
                    postal_code=parking_user.postal_code,
                    village=parking_user.village,
                    alley=parking_user.alley,
                    street=parking_user.street,

                    # tax invoice company
                    company_unit=parking_user.company_unit,
                    identity_com=parking_user.identity_com,
                    company_name=parking_user.company_name,
                    company_no=parking_user.company_no,
                    company_village=parking_user.company_village,
                    company_alley=parking_user.company_alley,
                    company_street=parking_user.company_street,
                    company_sub_district=parking_user.company_sub_district,
                    company_district=parking_user.company_district,
                    company_province=parking_user.company_province if parking_user.company_province != '' else None,
                    company_postal_code=parking_user.company_postal_code,

                    # file
                    copy_id_card=session.get('copy_id_card'),
                    copy_doc_car1=session.get('copy_doc_car1'),
                    copy_doc_car2=session.get('copy_doc_car2'),
                    card_member_copy=session.get('card_member_copy')
                )
                db.session.add(newmember)
            else:
                for key, value in session.items():
                    if key in Parking_member.__table__.columns.keys():
                        if getattr(old_card, key) != value:
                            if key == 'birth_date':
                                setattr(old_card, key, datetime.datetime.strptime(
                                    value, '%d/%m/%Y'))
                            else:
                                setattr(old_card, key,
                                        value if value != '' else None)
                setattr(old_card, 'card_status', None)
                setattr(old_card, 'parking_register_date',
                        datetime.datetime.today())
                setattr(old_card, 'card_expire_date', None)
                setattr(old_card, 'card_last_read_date', None)

        db.session.add(new_log)
        db.session.commit()
        return redirect(url_for('home_private'))

    if request.method == 'GET':
        check_user = Parking_member.query.filter_by(
            identity_card=current_user.identity_card).first()
        if check_user:
            check_user = 1
        elif not check_user:
            check_user = 0
        if check_user == 0:
            station = session.get('station')
            station = Parking_manage.query.filter_by(
                parking_name=station).first()
            parking_code = station.parking_code
            station_name = station.parking_name
            station_name_en = station.parking_name_eng
            station_image = station.parking_image
            vcard_type = station.vcard_type
            price = f'{station.parking_price:,}'.split('.')[0]
            location = station.location
            card_id = session.get('card_id')
            # if card_id:
            #     exp = Parking_member.query.filter_by(card_id=card_id).first()
            #     if exp:
            #         exp = exp.card_expire_date.strftime('%d/%m/%Y')
            #     else:
            #         exp = 'รอการอนุมัติ'
            # else:
            #     exp = 'รอการอนุมัติ'
            exp = 'รออนุมัติ'

            return render_template(
                'member-register-step4.html',

                cus_id=session.get('cus_id'),
                identity_card=session.get('identity_card'),
                first_name_th=session.get('first_name_th'),
                last_name_th=session.get('last_name_th'),
                first_name_en=session.get('first_name_en'),
                last_name_en=session.get('last_name_en'),
                birth_date=session.get('birth_date'),
                phone=session.get('phone'),
                parking_code=parking_code,

                # car registration 1

                license_plate1=session.get('license_plate1'),
                province_car1=session.get('province_car1'),
                brand_name1=session.get('brand_name1'),
                color1=session.get('color1'),

                # car registration 2

                license_plate2=session.get('license_plate2'),
                province_car2=session.get('province_car2'),
                brand_name2=session.get('brand_name2'),
                color2=session.get('color2'),

                # tax invoice home
                unit_home=session.get('unit_home'),
                address_no=session.get('address_home'),
                village_home=session.get('village_home'),
                alley_home=session.get('alley_home'),
                road_home=session.get('road_home'),
                province_home=session.get('province_home'),
                district_home=session.get('district_home'),
                sub_district_home=session.get('sub_district_home'),
                postal_code_home=session.get('postal_code_home'),

                # tax invoice company
                company_unit=session.get('unit_company'),
                identity_com=session.get('identity_com'),
                company_name=session.get('company_name'),
                company_no=session.get('address_company'),
                company_village=session.get('village_company'),
                company_alley=session.get('alley_company'),
                company_street=session.get('road_company'),
                company_province=session.get('province_company'),
                company_district=session.get('district_company'),
                company_sub_district=session.get('sub_district_company'),
                company_postal_code=session.get('postal_code_company'),

                # file
                copy_id_card='../static/image-manage/document/' + \
                session.get('copy_id_card'),
                copy_doc_car1='../static/image-manage/document/' + \
                session.get('copy_doc_car1'),
                copy_doc_car2='../static/image-manage/document/' + \
                session.get('copy_doc_car2'),
                card_member_copy='../static/image-manage/document/' + \
                session.get('card_member_copy'),

                # card
                vcard_type=vcard_type,
                card_id=session.get('card_id'),
                card_name=session.get('first_name_th'),
                exp=exp, card_last_name=session.get('last_name_th'),

                # below page
                station_name_en=station_name_en,
                station_name=station_name,
                location=location,
                price=price,
                station_image=station_image
            )
        elif check_user == 1:
            identity_card = current_user.identity_card
            card_id = session.get('card_id')
            # if card_id:
            #     exp = Parking_member.query.filter_by(card_id=card_id).first()
            #     if exp:
            #         exp = exp.card_expire_date.strftime('%d/%m/%Y')
            #     else:
            #         exp = 'รอการอนุมัติ'
            # else:
            #     exp = 'รอการอนุมัติ'
            exp = 'รออนุมัติ'
            parking_user = Parking_member.query.filter_by(
                identity_card=identity_card).first()
            station = Parking_manage.query.filter_by(
                parking_name=session.get('station')).first()

            return render_template(
                'member-register-step4.html',
                # below page
                station_name=station.parking_name,
                station_name_en=station.parking_name_eng,
                price=f'{station.parking_price:,}'.split('.')[0],
                location=station.location,
                station_image=station.parking_image,

                # card
                card_id=card_id,
                vcard_type=station.vcard_type,
                card_name=parking_user.first_name_th,
                exp=exp, card_last_name=parking_user.last_name_th,

                # personal
                cus_id=session.get('cus_id'),
                identity_card=identity_card,
                first_name_th=parking_user.first_name_th,
                last_name_th=parking_user.last_name_th,
                first_name_en=parking_user.first_name_en,
                last_name_en=parking_user.last_name_en,
                birth_date=parking_user.birth_date.strftime(
                    '%d/%m/%Y') if parking_user.birth_date else '',
                phone=parking_user.phone,

                # car registration 1

                license_plate1=session.get('license_plate1'),
                province_car1=session.get('province_car1'),
                brand_name1=session.get('brand_name1'),
                color1=session.get('color1'),

                # car registration 2

                license_plate2=session.get('license_plate2'),
                province_car2=session.get('province_car2'),
                brand_name2=session.get('brand_name2'),
                color2=session.get('color2'),

                # tax invoice home
                unit_home=parking_user.unit_home,
                address_no=parking_user.address_no,
                province_home=parking_user.province,
                district_home=parking_user.district,
                sub_district_home=parking_user.sub_district,
                postal_code_home=parking_user.postal_code,
                village_home=parking_user.village,
                alley_home=parking_user.alley,
                road_home=parking_user.street,

                # tax invoice company
                company_unit=parking_user.company_unit,
                identity_com=parking_user.identity_com,
                company_name=parking_user.company_name,
                company_no=parking_user.company_no,
                company_village=parking_user.company_village,
                company_alley=parking_user.company_alley,
                company_street=parking_user.company_street,
                company_sub_district=parking_user.company_sub_district,
                company_district=parking_user.company_district,
                company_province=parking_user.company_province,
                company_postal_code=parking_user.company_postal_code,

                # file
                copy_id_card='../static/image-manage/document/' + \
                session.get('copy_id_card'),
                copy_doc_car1='../static/image-manage/document/' + \
                session.get('copy_doc_car1'),
                copy_doc_car2='../static/image-manage/document/' + \
                session.get('copy_doc_car2'),
                card_member_copy='../static/image-manage/document/' + \
                session.get('card_member_copy')
            )


# ยืนยันการชำระค่าบริการ
@app.route('/parking-payment', methods=['GET', 'POST'])  # ittipon
def parking_payment():
    cards = payment(current_user.identity_card)
    cards_count = len(cards)
    cards_exp = payment_exp(current_user.identity_card)
    approve_date = datetime.datetime.today()
    lastdate_pay = approve_date + datetime.timedelta(7)
    if request.method == 'GET':
        if cards_count == 1:
            date = datetime.date.today()
            max_date = date + datetime.timedelta(7)
            min_date = date.strftime('%Y-%m-%d')
            date2 = date.strftime('%d/%m/%Y')
            date = date.strftime("%Y-%m-%d")
            card = cards[0]
            return render_template('parking-payment.html', card=card, date=date, max_date=max_date, min_date=min_date, cards_count=cards_count, cards_exp=cards_exp, date2=date2)
        elif cards_count == 2:
            date = datetime.date.today()
            max_date = date + datetime.timedelta(7)
            min_date = date.strftime('%Y-%m-%d')
            date2 = date.strftime('%d/%m/%Y')
            date = date.strftime("%Y-%m-%d")
            return render_template('parking-payment.html', card=cards[0], card2=cards[1], date=date, max_date=max_date, min_date=min_date, cards_count=cards_count, cards_exp=cards_exp, date2=date2)
        else:
            return render_template('parking-payment.html')

    if request.method == 'POST' and cards_count == 1:
        if request.form.get('status') == 'บัตรใหม่':
            total = request.form.get('total2')
            deposit = request.form.get('deposit')
            address_type = request.form.get('address')
            station = request.form.get('station')
            # month = request.form.get('myNumber')
            # price = Parking_manage.query.filter_by(parking_name=station).first().parking_price
            # price = round(((float(total) - float(deposit)) * (100/107)), 2)
            # vat = round(((float(total) - float(deposit)) - price), 2)
            # month = (int(total) - float(deposit)) / int(price)
            card_id = request.form.get('card_id')
            service_start = request.form.get('datefield')
            # card1
            parking_detail = Parking_manage.query.filter_by(parking_name = station).first()
            price = round(float(parking_detail.parking_price) * (100/107),2)
            vat = round(((float(total) - float(deposit)) - price), 2)
            month = (int(total) - float(deposit)) / int(parking_detail.parking_price)

            log_update = Parking_log.query.filter_by(card_id=card_id).filter(Parking_log.parking_name == station)\
                .filter(Parking_log.transaction_type != 3).order_by(Parking_log.Id.desc()).first()
            log_update.amount = price
            log_update.total = total
            log_update.month = month
            log_update.service_start_date = datetime.datetime.strptime(
                service_start, '%Y-%m-%d')
            log_update.payment_status = '0'
            log_update.address_type = address_type
            log_update.deposit_amount = deposit
            log_update.vat = vat
        elif request.form.get('status') != 'บัตรใหม่':
            total = request.form.get('total2')
            deposit = request.form.get('deposit')
            station = request.form.get('station')
            # month = request.form.get('myNumber')
            # price = Parking_manage.query.filter_by(parking_name=station).first().parking_price
            # price = round(((float(total) - float(deposit)) * (100/107)), 2)
            # vat = round(((float(total) - float(deposit)) - price), 2)
            # month = (int(total) - float(deposit)) / int(price)
            parking_detail = Parking_manage.query.filter_by(parking_name = station).first()
            price = round(float(parking_detail.parking_price) * (100/107),2)
            vat = round(((float(total) - float(deposit)) - price), 2)
            month = (int(total) - float(deposit)) / int(parking_detail.parking_price)

            card_id = request.form.get('card_id')
            service_start = request.form.get('datefield')
            address_type = request.form.get('address')
            print('-'*30)
            print(station)
            print(station == 'สถานีศูนย์วัฒนธรรม (ลาน1)')
            print('-'*30)
            old_log = Parking_log.query.filter_by(card_id=card_id).filter(Parking_log.parking_name == station)\
                .order_by(Parking_log.Id.desc()).first()
            member = Parking_member.query.filter_by(card_id=card_id).filter(Parking_member.parking_code == Parking_manage.query.filter_by(parking_name=station).first().parking_code)\
                .filter(or_(Parking_member.card_status == '1', Parking_member.card_status == None)).first()
            if old_log.payment_status == '0':
                old_log.amount = price
                old_log.total = total
                old_log.month = month
                old_log.service_start_date = datetime.datetime.strptime(
                    service_start, '%Y-%m-%d')
                old_log.address_type = address_type
                old_log.deposit_amount = deposit
                old_log.vat = vat
            elif old_log.payment_status != '0':
                new_log = Parking_log(verify_status=1,
                                      card_id=card_id,
                                      input_type=1, transaction_type=2,
                                      identity_card=member.identity_card,
                                      last_name=member.last_name_th,
                                      first_name=member.first_name_th,
                                      phone=member.phone,
                                      parking_code=member.parking_code,
                                      parking_name=old_log.parking_name,
                                      parking_type_name=old_log.parking_type_name,
                                      amount=price,# orderNumber=genRef2(a=1, id_=Parking_log.query.order_by(Parking_log.Id.desc()).first().Id + 1,station=member.parking_code),
                                      parking_register_date=member.parking_register_date,
                                      approve_date=approve_date, lastdate_pay=lastdate_pay,
                                      payment_status='0', service_start_date=datetime.datetime.strptime(service_start, '%Y-%m-%d'),
                                      total=total, deposit_amount=deposit,
                                      month=month, address_type=address_type, vat=vat
                                      )
                db.session.add(new_log)
                db.session.flush()
                new_log.orderNumber = genRef2(a=1, id_=new_log.Id,station=old_log.parking_code)
        db.session.commit()
        return redirect(url_for('payment_methods'))

    if request.method == 'POST' and cards_count == 2:
        total = request.form.get('total2')
        if total != '0':
            deposit = request.form.get('deposit')
            price = request.form.get('pricedummy')
            # month = (int(total) - float(deposit)) / int(price)
            # month = int(request.form.get('myNumber'))
            station = request.form.get('station')
            card_id = request.form.get('card_id')
            date = request.form.get('datefield')
            status = request.form.get('status')
            station = request.form.get('station')
            service_start = request.form.get('datefield')
            address_type = request.form.get('address')
            # price = round(((float(total) - float(deposit)) * (100/107)), 2)
            # vat = round(((float(total) - float(deposit)) - price), 2)
            parking_detail = Parking_manage.query.filter_by(parking_name = station).first()
            price = round(float(parking_detail.parking_price) * (100/107),2)
            vat = round(((float(total) - float(deposit)) - price), 2)
            month = (int(total) - float(deposit)) / int(parking_detail.parking_price)
            # card1
        else:
            total = request.form.get('total3')
            deposit = request.form.get('deposit2')
            price = request.form.get('pricedummy2')
            # month = (int(total) - float(deposit)) / int(price)
            # month = int(request.form.get('myNumber2'))
            card_id = request.form.get('card_id2')
            station = request.form.get('station2')
            date = request.form.get('datefield2')
            status = request.form.get('status1')
            station = request.form.get('station2')
            service_start = request.form.get('datefield2')
            address_type = request.form.get('address')

            parking_detail = Parking_manage.query.filter_by(parking_name = station).first()
            price = round(float(parking_detail.parking_price) * (100/107),2)
            vat = round(((float(total) - float(deposit)) - price), 2)
            month = (int(total) - float(deposit)) / int(parking_detail.parking_price)
            # price = round(((float(total) - float(deposit)) * (100/107)), 2)
            # vat = round(((float(total) - float(deposit)) - price), 2)
        if status == 'บัตรใหม่':
            log_update = Parking_log.query.filter_by(card_id=card_id)\
                .filter(Parking_log.parking_name == station).order_by(Parking_log.Id.desc()).first()
            log_update.month = month
            log_update.amount = price
            log_update.total = total
            log_update.service_start_date = datetime.datetime.strptime(
                service_start, '%Y-%m-%d')
            log_update.payment_status = '0'
            log_update.address_type = address_type
            log_update.deposit_amount = deposit
            log_update.vat = vat
        elif status != 'บัตรใหม่':
            old_log = Parking_log.query.filter_by(card_id=card_id).filter(Parking_log.parking_name == station)\
                .order_by(Parking_log.Id.desc()).first()
            member = Parking_member.query.filter_by(card_id=card_id).filter(Parking_member.parking_code == Parking_manage.query.filter_by(parking_name=station).first().parking_code)\
                .filter(or_(Parking_member.card_status == '1', Parking_member.card_status == None)).first()
            if old_log.payment_status == '0':
                old_log.amount = price
                old_log.total = total
                old_log.month = month
                old_log.service_start_date = datetime.datetime.strptime(
                    service_start, '%Y-%m-%d')
                old_log.address_type = address_type
                old_log.deposit_amount = deposit
                old_log.vat = vat
            elif old_log.payment_status != '0':
                new_log = Parking_log(
                    verify_status=1,
                    card_id=card_id,
                    input_type=1, transaction_type=2,
                    identity_card=member.identity_card,
                    last_name=member.last_name_th,
                    first_name=member.first_name_th,
                    phone=member.phone,
                    parking_code=member.parking_code,
                    parking_name=old_log.parking_name,
                    parking_type_name=old_log.parking_type_name,
                    amount=price,# orderNumber=genRef2(a=1, id_=Parking_log.query.order_by(Parking_log.Id.desc()).first().Id + 1,station=member.parking_code),
                    parking_register_date=member.parking_register_date,
                    approve_date=approve_date, lastdate_pay=lastdate_pay,
                    payment_status='0', service_start_date=datetime.datetime.strptime(service_start, '%Y-%m-%d'),
                    total=total, deposit_amount=deposit,
                    month=month, address_type=address_type, vat=vat
                )
                db.session.add(new_log)
                db.session.flush()
                new_log.orderNumber = genRef2(a=1, id_=new_log.Id,station=old_log.parking_code)
            # card2
        print('-'*30)
        print(address_type)
        db.session.commit()
        return redirect(url_for('payment_methods'))


# เพิ่มบัตรเครดิต

@app.route('/parking-creditcard')
def parking_creditcard():
    return render_template('parking-creditcard.html')

# เพิ่มผูกบัญชี


@app.route('/parking-account')
def parking_account():
    return render_template('parking-account.html')


def gen_securityKey_pd(ref2, total):  # passachon
    cur = mysql.connection.cursor()
    cur.execute('select secure_hash_secret_pd from key_info')
    res = cur.fetchone()
    merchantId = '900000303'
    orderRef = ref2
    currcode = '764'
    amount = str(total)
    payType = 'N'
    SecureHashKey = res[0]
    print("*******", SecureHashKey)
    securityKey = merchantId+'|'+orderRef+'|' + \
        currcode+'|'+amount+'|'+payType+'|'+SecureHashKey
    securityKey = securityKey.encode('utf-8')
    h = hashlib.sha512(securityKey)
    return h.hexdigest()


def gen_securityKey_uat(ref2, total):  # passachon
    #Merchant ID : 900000303
    # SecureHashSecret: kuxSqqDo26xGgBr6PCmHEa5I9TyMXLUG
    # https://uatktbfastpay.ktb.co.th/SIT/eng/merchant/index.jsp
    # password:uatFastpay2021
    cur = mysql.connection.cursor()
    cur.execute('select secure_hash_secret_uat from key_info')
    res = cur.fetchone()
    merchantId = '900000303'  # ธนาคารกำหนดให้
    orderRef = ref2
    currcode = '764'  # ค่าบาทไทย
    amount = str(total)
    payType = 'N'  # การชำระแบบปกติ
    # 'kuxSqqDo26xGgBr6PCmHEa5I9TyMXLUG'  # จะมีการ update ทุกๆ 2 ปี
    SecureHashKey = res[0]
    print("*******", SecureHashKey)
    securityKey = merchantId+'|'+orderRef+'|' + \
        currcode+'|'+amount+'|'+payType+'|'+SecureHashKey
    securityKey = securityKey.encode('utf-8')
    h = hashlib.sha512(securityKey)
    print('this', h.hexdigest())
    return h.hexdigest()

# gen_securityKey_uat('REVN10130000007160',20)


def generate_term_seq():  # passachon #ขาpayment=pay_ref
    x = datetime.datetime.now()
    date = x.date()
    date = date.strftime('%Y-%m-%d')
    today = x.strftime('%Y''%m''%d''%H''%M')
    cursor = mysql.connection.cursor()
    query = "select COUNT(id) from parking_log where parking_register_date = %s"
    val = (date,)
    cursor.execute(query, val)
    result = cursor.fetchone()
    count_id = int(result[0])+1
    term_seq = today+str(count_id)
    return term_seq


@app.route('/uat/payment-methods/')
def payment_methods_uat():
    ref1 = current_user.identity_card
    session['identity_card'] = ref1
    encrypt_ref1 = encryptuat(ref1)
    
    latest_log = find_last_log(ref1)[0]
    ref2 = latest_log.orderNumber
    
    termS = generate_term_seq()
    term_seq = encryptuat(termS)
    session['payRef'] = termS
    
    total = latest_log.total
    session['transaction_type'] = latest_log.transaction_type
    
    securityKey = gen_securityKey_uat(ref2, total)
    deposit_amount = latest_log.deposit_amount
    
    if deposit_amount is None:
        amount = total
        deposit_amount = 0
    else:
        amount = total - deposit_amount
        deposit_amount = int(deposit_amount)
    
    month = latest_log.month
    address_type = latest_log.address_type
    id_ = latest_log.Id
    
    session['total'] = str(total)
    session['ref2'] = ref2
    
    park = latest_log.parking_name
    cardid = latest_log.card_id

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE parking_log SET term_seq = %s WHERE orderNumber = %s", (termS, ref2))
    mysql.connection.commit()

    cur = mysql.connection.cursor()
    cur.execute("SELECT accountNumber FROM account_number_ktb WHERE identity_card = %s AND accountStatus = 'Active'", (ref1,))
    result = cur.fetchone()
    
    parking_code = latest_log.parking_code
    line = Parking_manage.query.filter_by(parking_code=parking_code).first().line_name
    ktb_detail = Ktb_detail.query.filter_by(line=line).first()
    
    transaction_type = latest_log.transaction_type
    merchant_id_dict = {
        '1': (ktb_detail.mid_register,ktb_detail.tid_register),
        '2': (ktb_detail.mid_renew,ktb_detail.tid_register),
        '4': (ktb_detail.mid_reserve,ktb_detail.tid_reserve),
        '5': (ktb_detail.mid_daily,ktb_detail.tid_daily)
    }
    merchant_id,terminal_id = merchant_id_dict.get(transaction_type)
    if not merchant_id or not terminal_id:
        raise Exception('Invalid transaction type')
    
    if result:
        ktb_ac = result[0]
        ktb_ac = f"XXXX-X-XX{ktb_ac[7:11]}"
        return render_template('payment-methods-2.html',
                               securityKey=securityKey, total=total, total3=total, ref2=ref2, ref1=ref1, 
                               ktb_ac=ktb_ac, service_start_date=latest_log.service_start_date.strftime('%d/%m/%Y'), 
                               amount=amount, month=month, parkname=park, card_id=cardid, term_seq=term_seq, 
                               address_type=address_type, id_=id_, total2=f"{total-deposit_amount:,}", 
                               deposit_amount=f"{deposit_amount:,}",merchant_id=merchant_id,terminal_id=terminal_id)
    else:
        return render_template('payment-methodsuat.html',
                               securityKey=securityKey, total=total, total3=total, ref2=ref2, ref1=ref1, 
                               service_start_date=latest_log.service_start_date.strftime('%d/%m/%Y'), amount=amount, 
                               month=month, parkname=park, card_id=cardid, term_seq=term_seq, encrypt_ref1=encrypt_ref1, 
                               address_type=address_type, id_=id_, total2=f"{total-deposit_amount:,}", 
                               deposit_amount=f"{deposit_amount:,}",merchant_id=merchant_id,terminal_id=terminal_id)


# ยืนยันการชำระค่าบริการ


@app.route('/payment-methods')  # passachon
def payment_methods():
    ref1 = current_user.identity_card
    session['identity_card'] = ref1
    encrypt_ref1 = encrypt(ref1)
    find = find_last_log(ref1)
    ref2 = find[0].orderNumber
    address_type = find[0].address_type
    id_ = find[0].Id
    termS = generate_term_seq()
    term_seq = encrypt(termS)
    session['payRef'] = termS
    total = find[0].total
    session['transaction_type'] = find[0].transaction_type
    securityKey = gen_securityKey_pd(ref2, total)
    deposit_amount = find[0].deposit_amount
    total2 = f'{int(find[0].total)-int(deposit_amount):,}'
    total3 = f'{int(find[0].total):,}'
    service_start_date = find[0].service_start_date.strftime('%d/%m/%Y')
    if deposit_amount is None:
        amount = total
        deposit_amount = f'0'
    else:
     amount = total - deposit_amount
     deposit_amount = f"{int(deposit_amount):,}"
    month = find[0].month
    address_type = find[0].address_type
    id_ = find[0].Id
    session['total'] = str(total)
    session['ref2'] = ref2
    park = find[0].parking_name
    cardid = find[0].card_id

    cursor = mysql.connection.cursor()
    sql = "UPDATE parking_log SET term_seq= %s WHERE orderNumber = %s"
    val = (termS, ref2)
    cursor.execute(sql, val)
    mysql.connection.commit()

    cur = mysql.connection.cursor()
    cur.execute(
        'select accountNumber from account_number_ktb where identity_card =%s AND accountStatus = "Active" ', (ref1,))
    result = cur.fetchone()
    if result:  # กรณีผูกบัญชีแล้ว สามารถกดชำระเงินได้เลยเพื่อตัดผ่านบัญชี
        ktb_ac = result[0]
        ktb_ac = "XXXX-X-XX"+ktb_ac[7:11]
        return render_template('payment-methods-2.html', securityKey=securityKey, total=total, ref2=ref2, ref1=ref1, ktb_ac=ktb_ac, service_start_date=service_start_date, amount=amount, month=month, parkname=park, card_id=cardid, term_seq=term_seq, address_type=address_type, id_=id_, total2=total2, deposit_amount=deposit_amount, total3=total3)
    else:
        return render_template('payment-methods.html', securityKey=securityKey, total=total, ref2=ref2, ref1=ref1, service_start_date=service_start_date, amount=amount, month=month, parkname=park, card_id=cardid, term_seq=term_seq, encrypt_ref1=encrypt_ref1, address_type=address_type, id_=id_, total2=total2, deposit_amount=deposit_amount, total3=total3)


def checkCustomer_cash():
    if session.get('transaction_type') == '1':
        return "newCus"
    else:
        return "oldCus"


@app.route('/methodCash')
def checkcard_type():
    typeCus = checkCustomer_cash()
    ref1 = current_user.identity_card
    find = find_last_log(ref1)
    cid = find[0].card_id
    card_type = find[0].parking_type_name
    parking_name = 'ที่ห้องทำบัตรรายเดือนหรือตู้ขาเข้าบริเวณอาคาจอดแล้วจร' + \
        find[0].parking_name
    if typeCus == "newCus":
     limit_date = find[0].parking_register_date
     limit_date = (limit_date+timedelta(days=7)).strftime('%d/%m/%Y')
     limit_date = 'ภายในวันที่ '+limit_date
    else:
     cursor = mysql.connection.cursor()
     cursor.execute(
         'select card_expire_date from parking_member where card_id=%s and vcard_type=%s', (cid, card_type))
     result = cursor.fetchone()
     card_expire_date = result[0]
     limit_date = (card_expire_date+timedelta(days=7)).strftime('%d/%m/%Y')
     limit_date = 'ภายในวันที่ '+limit_date
    return render_template('all-payment.html', typeCus=typeCus, card_type=card_type, parking_name=parking_name, limit_date=limit_date)


@app.route('/update_paymentName_cash', methods=['POST'])
def update_paymentName_cash():
    cursor = mysql.connection.cursor()
    sql = "UPDATE parking_log SET payment_name = %s WHERE orderNumber = %s"
    val = ('1', session['ref2'])
    cursor.execute(sql, val)
    mysql.connection.commit()
    return "cash"


@app.route('/update_paymentName_cgp', methods=['POST'])
def update_paymentName_cgp():
    cursor = mysql.connection.cursor()
    sql = "UPDATE parking_log SET payment_name = %s WHERE orderNumber = %s"
    val = ('4', session['ref2'])
    cursor.execute(sql, val)
    mysql.connection.commit()
    return "CGP"


@app.route('/update_paymentName_debit', methods=['POST'])
def update_paymentName_debit():
    cursor = mysql.connection.cursor()
    sql = "UPDATE parking_log SET payment_name = %s WHERE orderNumber = %s"
    val = ('2', session['ref2'])
    cursor.execute(sql, val)
    mysql.connection.commit()
    return "success"


@app.route('/cgp-KTBPayment', methods=['POST'])  # passachon
def cgp_payment():
    ref1 = current_user.identity_card
    total = session['total']
    ref2 = session['ref2']
    payRef = session['payRef']
    find = find_last_log(ref1)
    cid = find[0].card_id
    parking_code = find[0].parking_code
    count_month = find[0].month
    card_type = find[0].parking_type_name
    id_ = find[0].Id
    # paymentCGP(ref1,total,ref2,payRef)
    response = paymentCGP(ref1, total, ref2, payRef)
    print(response)
    cursor = mysql.connection.cursor()
    sql = "UPDATE parking_log SET payment_name = %s WHERE orderNumber = %s"
    val = ('4', ref2)
    cursor.execute(sql, val)
    mysql.connection.commit()
    if response == "Payment is Executed Successfully":
        capacity_count(parking_code, id_)
        renew_card_TAFF_orAll(cid, count_month, '0', ref1, parking_code)
        log_update = Parking_log.query.filter_by(orderNumber = ref2).first()
        if log_update.transaction_type in ["1","2"]:
            card_id = log_update.card_id
            mem = Parking_member.query.filter_by(card_id=card_id)\
                .filter(Parking_member.parking_code == log_update.parking_code).first()
            data = {
                    "parking_code": log_update.parking_code,    
                    "first_name": log_update.first_name,
                    "last_name": log_update.last_name,
                    "card_id": card_id,
                    "license_plate1": mem.license_plate1,
                    "license_plate2": mem.license_plate2,
                    "card_expire_date": mem.card_expire_date,
                    "service_start_date": log_update.service_start_date,
                }
            api = ApiMember(data)
            api.from_orm(mem)
            if log_update.transaction_type == "1":
                true_card_id = checkCardNotRandom(card_id)
                not_re_mem = checkCardNotReMem(log_update)
                print('true card id: ',true_card_id)
                if true_card_id:
                    if not_re_mem:
                        res = api.request_insert()[1]
                        if res == 404:
                            update_token_thread = Thread(target=api.try_to_request,args=('insert',))
                            update_token_thread.start()
                    else:
                        res = api.request_update()[1]
                        if res == 404:
                            update_token_thread = Thread(target=api.try_to_request,args=('update',))
                            update_token_thread.start()
            elif log_update.transaction_type == "2":
                res = api.request_update()[1]
                if res == 404:
                    update_token_thread = Thread(target=api.try_to_request,args=('update',))
                    update_token_thread.start()
        return redirect(url_for('success_payment'))
    else:
        print("------------not suc")
        if response == "EM053":
            return '/not-enough-payment'
        else:
            return '/payment/fail'

# เลือกชำระเงิน qr-code


@app.route('/qr-code')  
def qrcode():
    ref1 = current_user.identity_card
    latest_log = find_last_log(ref1)[0]
    
    parking_code = latest_log.parking_code
    line = Parking_manage.query.filter_by(parking_code=parking_code).first().line_name
    ktb_detail = Ktb_detail.query.filter_by(line=line).first()
    transaction_type = latest_log.transaction_type
    qrcode_detail = {
        '1': (ktb_detail.bid_register,ktb_detail.suffix_register),
        '2': (ktb_detail.bid_renew,ktb_detail.suffix_renew),
        '4': (ktb_detail.bid_reserve,ktb_detail.suffix_reserve),
        '5': (ktb_detail.bid_daily,ktb_detail.suffix_daily)
    }
    bid,suffix = qrcode_detail.get(transaction_type)
    
    
    ref2 = latest_log.orderNumber
    total = str(latest_log.total)
    identity_card = latest_log.identity_card
    qrcode = text_qr(total, identity_card, ref2, bid=bid, suffix=suffix)  # (money,ref1,ref2)
    latest_log.payment_name = '3'
    db.session.commit()
    return render_template('qr-code.html', qrcode=qrcode)

################fastpay#########################################


@app.route('/payment/success')  # Success Payment ถ้าชำระสำเร็จ
def success_payment():
    print("checkcus")
    check = checkCustomer_cash()
    if check == 'newCus':
     return render_template('success-payment-Newcustomer.html')
    else:
     return render_template('success-payment-Oldcustomer.html')


@app.route('/payment/fail')  # กรณีชำระไม่สำเร็จ
def fail_payment():
    return render_template('fail-payment.html')


@app.route('/payment/cancel')  # กรณีcancle
def cancel_payment():
    return render_template('cancel-payment.html')

#######################################################################
###############################cgp######################################


@app.route('/uat/payment-methods/success')  # Success Account ผูกบัญชีสำเร็จ
def success_account_():
    return render_template('success-account.html')


@app.route('/payment-methods/success')
def success_account():
    return render_template('success-account.html')
######################################################################

# กรณีเงินในบัญชีไม่พอ


@app.route('/not-enough-payment')
def not_enough_payment():
    return render_template('not-enough-payment.html')


@app.route('/uat/payment/ktb/1.0/execute', methods=['POST'])  # passachon
def directlinkAPI():
    response_ = getDirectlink()
    return response_


@app.route('/payment/ktb/1.0/execute', methods=['GET', 'POST'])  # passachon
def directlinkAPI_pd():
    response_ = getDirectlink_pd()
    return response_


@app.route('/uat/payment/ktb/1.0/datafeed', methods=['POST'])  # passachon
def fastpay_datafeed_uat():
    x = datetime.datetime.now()
    successCode = request.form.get("successcode")
    orderRef = request.form.get("orderRef")
    print(orderRef)
    amt = request.form.get("amt")  # amount
    cur = request.form.get("cur")  # THB
    cardNo = request.form.get("cardNo")  # accountNum
    payRef = request.form.get("payRef")
    print("OK")
    if successCode == '0':
        # cursor = mysql.connection.cursor()
        # sql = "UPDATE parking_log SET payment_name=%s,payment_status= %s ,payment_date = %s,payRef_ktb=%s WHERE orderNumber = %s"
        # val = ("2","1",x,payRef,orderRef)
        # cursor.execute(sql, val)
        # mysql.connection.commit()
        log_update = Parking_log.query.filter_by(orderNumber=orderRef).first()
        log_update.payment_name = '2'
        log_update.payment_status = '1'
        log_update.payment_date = x
        log_update.payRef_ktb = payRef
        capacity_count(log_update.parking_code, log_update.Id)
        cur = mysql.connection.cursor()
        sql = "SELECT parking_type_name,card_id,month,identity_card,parking_code from parking_log WHERE orderNumber = %s"
        val = (orderRef,)
        cur.execute(sql, val)
        result = cur.fetchone()
        if result:
            typeCard = result[0]
            cid = result[1]
            count_month = result[2]
            identity_card = result[3]
            parking_code = result[4]
            cursor = mysql.connection.cursor()
            cursor.execute(
                'select card_expire_date from parking_member where card_id=%s AND identity_card=%s AND vcard_type="TAFF"', (cid, identity_card))
            result = cursor.fetchone()
            if result[0] is not None:
                card_expire_date = result[0]
                re_log = Parking_log.query.filter_by(
                    orderNumber=orderRef).first()
                re_log.reexpire_after_void = card_expire_date
            renew_card_TAFF_orAll(cid, count_month, '0',
                                  identity_card, parking_code)
            db.session.commit()
            send_data_to_publish_service_with_ordernumber(orderRef)
            print("success")
    else:
        print("fail")
    db.session.commit()
    return "OK"


@app.route('/payment/ktb/1.0/datafeed', methods=['POST'])  # passachon
def fastpay_datafeed():
    x = datetime.datetime.now()
    successCode = request.form.get("successcode")
    orderRef = request.form.get("orderRef")
    print(orderRef)
    amt = request.form.get("amt")  # amount
    cur = request.form.get("cur")  # THB
    cardNo = request.form.get("cardNo")  # accountNum
    payRef = request.form.get("payRef")
    print("OK")
    if successCode == '0':
        # cursor = mysql.connection.cursor()
        # sql = "UPDATE parking_log SET payment_name=%s,payment_status= %s ,payment_date = %s,payRef_ktb=%s WHERE orderNumber = %s"
        # val = ("2","1",x,payRef,orderRef)
        # cursor.execute(sql, val)
        # mysql.connection.commit()
        log_update = Parking_log.query.filter_by(orderNumber=orderRef).first()
        log_update.payment_name = '2'
        log_update.payment_status = '1'
        log_update.payment_date = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        log_update.comments = 'datafeed ' + \
            datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        log_update.payRef_ktb = payRef
        capacity_count(log_update.parking_code, log_update.Id)
        cur = mysql.connection.cursor()
        sql = "SELECT parking_type_name,card_id,month,identity_card,parking_code from parking_log WHERE orderNumber = %s"
        val = (orderRef,)
        cur.execute(sql, val)
        result = cur.fetchone()
        if result:
            typeCard = result[0]
            cid = result[1]
            count_month = result[2]
            identity_card = result[3]
            parking_code = result[4]
            cursor = mysql.connection.cursor()
            cursor.execute(
                'select card_expire_date from parking_member where card_id=%s AND identity_card=%s AND vcard_type="TAFF"', (cid, identity_card))
            result = cursor.fetchone()
            if result is not None:
                card_expire_date = result[0]
                re_log = Parking_log.query.filter_by(
                    orderNumber=orderRef).first()
                re_log.reexpire_after_void = card_expire_date
            renew_card_TAFF_orAll(cid, count_month, '0',
                                  identity_card, parking_code)
            print("success")
            
        if log_update.transaction_type == "4":
            reserve_checkin_period = Parking_manage.query.filter_by(parking_name=log_update.parking_name).first(
            ).reserve_checkin_period
            log_update.qr_show_exp = log_update.payment_date + \
                datetime.timedelta(days=1)
            log_update.qr_code_exprie = log_update.payment_date + \
                datetime.timedelta(minutes=int(reserve_checkin_period))
            db.session.commit()
            if(__name__ == 'directlink'):
                sec = 60*reserve_checkin_period
                p = mp.Process(target=qr_opengate_timeout,
                               args=(orderRef, sec,))
                p.start()
        elif log_update.transaction_type in ['1', '2']:
            card_id = log_update.card_id
            mem = Parking_member.query.filter_by(card_id=card_id)\
                .filter(Parking_member.parking_code == log_update.parking_code).first()
            data = {
                    "parking_code": log_update.parking_code,    
                    "first_name": log_update.first_name,
                    "last_name": log_update.last_name,
                    "card_id": card_id,
                    "license_plate1": mem.license_plate1,
                    "license_plate2": mem.license_plate2,
                    "card_expire_date": mem.card_expire_date,
                    "service_start_date": log_update.service_start_date,
                }
            api = ApiMember(data)
            api.from_orm(mem)
            if log_update.transaction_type == "1":
                true_card_id = checkCardNotRandom(card_id)
                not_re_mem = checkCardNotReMem(log_update)
                print('true card id: ',true_card_id)
                if true_card_id :
                    if not_re_mem:
                        res = api.request_insert()[1]
                        if res == 404:
                            update_token_thread = Thread(target=api.try_to_request,args=('insert',))
                            update_token_thread.start()
                    else:
                        res = api.request_update()[1]
                        if res == 404:
                            update_token_thread = Thread(target=api.try_to_request,args=('update',))
                            update_token_thread.start()
            elif log_update.transaction_type == "2":
                res = api.request_update()[1]
                print('update: ',res)
                if res == 404:
                    update_token_thread = Thread(target=api.try_to_request,args=('update',))
                    update_token_thread.start()
    else:
        print("fail")
    db.session.commit()
    return "OK"


# passachon
@app.route('/uat/payment/ktb/1.0/execute/Register', methods=['POST'])
def get_responseRegister_uat():
    print("heloo cgpInapp")
    ref1 = session.get('identity_card')
    if request.form.get('site_name') == 'https://parking.mrta.co.th/uat/payment-methods/':
        term_seq = request.form.get('term_seq')  # นับใหม่ในแต่ละวัน
        ref1 = request.form.get('ref1')
        date = request.form.get('post_date')  # CCYYMMDD
        time = request.form.get('tran_time')  # HHMMSSss
        # xxx:function error, NN:error number but 00:success
        result = request.form.get('result')
        # Account No หรือ Account Ref ทีหน่วยงานจะให้ในการส่งคําสังตัดเงินเข้ามา
        account_ref = request.form.get('account_ref')
        cursor = mysql.connection.cursor()
        print("******************************CGPINAPP/////////////////////////")
        print(ref1, account_ref)
        if request.form.get('tran_type') == 'R':  # Register
            if result == '00':
             sql = "INSERT INTO account_number_ktb(identity_card,accountNumber,accountStatus) VALUES (%s, %s, %s)"
             val = (ref1, account_ref, "Active")
             cursor.execute(sql, val)
             mysql.connection.commit()
             cursor.close()
            else:
                print("error :", result)
        elif request.form.get('tran_type') == 'D':  # Delete
            if result == '00':
             cursor = mysql.connection.cursor()
             sql = "UPDATE account_number_ktb SET accountStatus= %s WHERE identity_card = %s"
             val = ("Inactive", ref1)
             cursor.execute(sql, val)
             mysql.connection.commit()
             cursor.close()
            else:
                print("error :", result)

    return "success"


@app.route('/payment/ktb/1.0/execute/Register', methods=['POST'])
def get_responseRegister():
    print("heloo cgpInapp")
    ref1 = session.get('identity_card')
    if request.form.get('site_name') == 'https://parking.mrta.co.th/payment-methods':
        term_seq = request.form.get('term_seq')  # นับใหม่ในแต่ละวัน
        ref1 = request.form.get('ref1')
        date = request.form.get('post_date')  # CCYYMMDD
        time = request.form.get('tran_time')  # HHMMSSss
        # xxx:function error, NN:error number but 00:success
        result = request.form.get('result')
        # Account No หรือ Account Ref ทีหน่วยงานจะให้ในการส่งคําสังตัดเงินเข้ามา
        account_ref = request.form.get('account_ref')
        cursor = mysql.connection.cursor()
        print("******************************CGPINAPP/////////////////////////")
        print(ref1, account_ref)
        if request.form.get('tran_type') == 'R':  # Register
            if result == '00':
             sql = "INSERT INTO account_number_ktb(identity_card,accountNumber,accountStatus) VALUES (%s, %s, %s)"
             val = (ref1, account_ref, "Active")
             cursor.execute(sql, val)
             mysql.connection.commit()
             cursor.close()
            else:
                print("error :", result)
        elif request.form.get('tran_type') == 'D':  # Delete
            if result == '00':
             cursor = mysql.connection.cursor()
             sql = "UPDATE account_number_ktb SET accountStatus= %s WHERE identity_card = %s"
             val = ("Inactive", ref1)
             cursor.execute(sql, val)
             mysql.connection.commit()
             cursor.close()
            else:
                print("error :", result)

    return "success"


#################################################################################################################
# รายการจองสิทธิ
@app.route('/parking-reserve')
def parking_reserve():
    cards = reserve(current_user.identity_card)

    cards_reserve = card_reserve(cards)

    return render_template('parking-reserve.html', cards_reserve=cards_reserve)


@app.route('/get-reserve', methods=['POST'])
def get_reserve():
    id_ = request.form.get('id')
    que = int(request.form.get('que'))
    log_update = Parking_log.query.filter_by(Id=id_).first()
    log_update.verify_status = 4
    log_update.q_no = f'Q{que:04}'
    log_update.q_up = que
    db.session.commit()
    return 'TRUE'


@app.route('/cancel-reserve', methods=['POST'])
def cancel_reserve():
    id_ = request.form.get('id')
    log_update = Parking_log.query.filter_by(Id=id_).first()
    log_update.verify_status = 3
    Parking_log.query.filter_by(parking_name=log_update.parking_name).filter(
        Parking_log.verify_status == 4).filter(Parking_log.q_up > log_update.q_up).update(
            {Parking_log.q_up: Parking_log.q_up - 1}
    )
    log_update.q_up = None
    log_update.q_no = None
    db.session.commit()
    return 'TRUE'

# ประวัติการทำรายการ


@app.route('/uat/payment-methods/history')
@app.route('/history')
def history():
    history_log = Parking_log.query.filter_by(identity_card=current_user.identity_card).filter(
        Parking_log.input_type != '' and Parking_log.input_type != None
    ).all()
    print(history_log)
    return render_template('history.html', history_log=history_log)

# ติดต่อรฟม.


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        email = request.form['email']
        type = request.form['type']
        description = request.form['description']

        # now = datetime.now()
        # today = now.strftime('%Y-%m-%d')

        with mysql.connection.cursor() as cursor:
            sql = """Insert into `contact` (`first_name`,`last_name`,`phone`,`email`,
            `type`,`description`)
            values(%s,%s,%s,%s,%s,%s)"""
            cursor.execute(sql, (first_name, last_name,
                                 phone, email, type, description))
            mysql.connection.commit()

        return redirect(url_for('contact'))
    # address = " 25 E 85th St, 10028 New York, NY"
    # pb.push_link("Cool site", "https://github.com")
    return render_template('contact.html')


@app.route('/contact2', methods=['GET', 'POST'])
def contact_2():
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        email = request.form['email']
        type = request.form['type']
        description = request.form['description']

        # now = datetime.now()
        # today = now.strftime('%Y-%m-%d')

        with mysql.connection.cursor() as cursor:
            sql = """Insert into `contact2` (`first_name`,`last_name`,`phone`,`email`,
            `type`,`description`)
            values(%s,%s,%s,%s,%s,%s)"""
            cursor.execute(sql, (first_name, last_name,
                                 phone, email, type, description))
            mysql.connection.commit()

        return redirect(url_for('contact'))
    return render_template('contact2.html')


# ข้อมูลผู้ใช้งาน
@app.route('/customer-profile', methods=['GET', 'POST'])
@login_required
def customer_profile():
    # 1 card
    home_form = Home_form()
    company_form = Company_form()
    car_form = Car_form()
    car_form2 = Car_form2()
    user_form = Change_username()
    identity_form = Change_identity()
    phone_form = Change_phone()
    home_form_card2 = Home_form2()
    company_form_card2 = Company_form2()
    password_form = Profilepassword()
    car_form3 = Car_form3()
    car_form4 = Car_form4()
    province = get_province()
    home_form.province.choices = [(i, i) for i in province]
    home_form_card2.province_card2.choices = [(i, i) for i in province]
    company_form.company_province.choices = [(i, i) for i in province]
    company_form_card2.company_province_card2.choices = [
        (i, i) for i in province]
    car_form.province_car1.choices = [(i, i) for i in province]
    car_form2.province_car2.choices = [(i, i) for i in province]
    car_form3.province_car1_card2.choices = [(i, i) for i in province]
    car_form4.province_car2_card2.choices = [(i, i) for i in province]
    car_form.brand_name1.choices = [
        (i.brand_name, i.brand_name) for i in Brand.query.all()]
    car_form2.brand_name2.choices = [
        (i.brand_name, i.brand_name) for i in Brand.query.all()]
    car_form3.brand_name1_card2.choices = [
        (i.brand_name, i.brand_name) for i in Brand.query.all()]
    car_form4.brand_name2_card2.choices = [
        (i.brand_name, i.brand_name) for i in Brand.query.all()]
    cards = owned_card(current_user.identity_card)
    cur = mysql.connection.cursor()
    cur.execute('select accountNumber from account_number_ktb where identity_card =%s AND accountStatus = "Active" ',
                (current_user.identity_card,))
    result = cur.fetchone()
    termS = generate_term_seq()
    ref1 = encrypt(current_user.identity_card)
    term_seq = encrypt(termS)
    if result:  # กรณีผูกบัญชีแล้ว สามารถกดชำระเงินได้เลยเพื่อตัดผ่านบัญชี
        ktb_ac = result[0]
        ktb_ac = "XXXX-X-XX"+ktb_ac[7:11]
    else:
        ktb_ac = " "

    if request.method == 'GET':
        identity_card = f'{current_user.identity_card[0]}-{current_user.identity_card[1:5]}- \
        {current_user.identity_card[5:10]}-{current_user.identity_card[10:12]}-{current_user.identity_card[12:]}'
        if current_user.phone == None:
            phone = '-'
        else:
            phone = str(current_user.phone)
            phone = f'{phone[:3]}-{phone[3:6]}-{phone[6:]}'
        if len(cards) == 0:
            card_id1 = '-'
            home_address = '-'
            card_id2 = '-'
            company_address = '-'
            brand_name1 = '-'
            color1 = '-'
            license_plate1 = '-'
            province_car1 = '-'
            brand_name2 = '-'
            color2 = '-'
            license_plate2 = '-'
            province_car2 = '-'
            card_count = len(cards)

            return render_template(
                'customer-profile.html', identity_card=identity_card, phone=phone,
                card_id1=card_id1, card_id2=card_id2, home_address=home_address, password_form=password_form,
                company_address=company_address, brand_name1=brand_name1, color1=color1, license_plate1=license_plate1,
                province_car1=province_car1, brand_name2=brand_name2, color2=color2, license_plate2=license_plate2,
                province_car2=province_car2, card_count=card_count, user_form=user_form, identity_form=identity_form,
                phone_form=phone_form, ktb_ac=ktb_ac, ref1=ref1, term_seq=term_seq)
        elif len(cards) == 1:

            card_id1 = f'{cards[0].card_id[:4]}-{cards[0].card_id[4:]}'
            home_address = create_home_address(cards[0])
            card_id2 = '-'
            company_address = create_company_address(cards[0])
            brand_name1 = cards[0].brand_name1
            color1 = cards[0].color1
            license_plate1 = cards[0].license_plate1
            province_car1 = cards[0].province_car1
            brand_name2 = cards[0].brand_name2
            color2 = cards[0].color2
            license_plate2 = cards[0].license_plate2
            province_car2 = cards[0].province_car2
            card_count = len(cards)

            return render_template(
                'customer-profile.html', identity_card=identity_card, phone=phone,
                card_id1=card_id1, card_id2=card_id2, home_address=home_address, password_form=password_form,
                company_address=company_address, brand_name1=brand_name1, color1=color1, license_plate1=license_plate1,
                province_car1=province_car1, brand_name2=brand_name2, color2=color2, license_plate2=license_plate2,
                province_car2=province_car2, card_count=card_count, home_form=home_form, company_form=company_form,
                car_form=car_form, car_form2=car_form2, user_form=user_form, identity_form=identity_form, phone_form=phone_form, ktb_ac=ktb_ac, ref1=ref1, term_seq=term_seq)

        elif len(cards) == 2:
            card_id1 = f'{cards[0].card_id[:4]}-{cards[0].card_id[4:]}'
            home_address = create_home_address(cards[0])
            company_address = create_company_address(cards[0])
            brand_name1 = cards[0].brand_name1
            color1 = cards[0].color1
            license_plate1 = cards[0].license_plate1
            province_car1 = cards[0].province_car1
            brand_name2 = cards[0].brand_name2
            color2 = cards[0].color2
            license_plate2 = cards[0].license_plate2
            province_car2 = cards[0].province_car2
            # card2
            card_id2 = f'{cards[1].card_id[:4]}-{cards[1].card_id[4:]}'
            home_address_card2 = create_home_address(cards[1])
            company_address_card2 = create_company_address(cards[1])
            brand_name1_card2 = cards[1].brand_name1
            color1_card2 = cards[1].color1
            license_plate1_card2 = cards[1].license_plate1
            province_car1_card2 = cards[1].province_car1
            brand_name2_card2 = cards[1].brand_name2
            color2_card2 = cards[1].color2
            license_plate2_card2 = cards[1].license_plate2
            province_car2_card2 = cards[1].province_car2
            card_count = len(cards)

            return render_template(
                'customer-profile.html', identity_card=identity_card, phone=phone, card_count=card_count,
                card_id1=card_id1, card_id2=card_id2, home_address=home_address, password_form=password_form,
                company_address=company_address, brand_name1=brand_name1, color1=color1, license_plate1=license_plate1,
                province_car1=province_car1, brand_name2=brand_name2, color2=color2, license_plate2=license_plate2,
                province_car2=province_car2,
                # card2
                home_address_card2=home_address_card2, company_address_card2=company_address_card2, brand_name1_card2=brand_name1_card2,
                color1_card2=color1_card2, license_plate1_card2=license_plate1_card2, province_car1_card2=province_car1_card2,
                brand_name2_card2=brand_name2_card2, color2_card2=color2_card2, license_plate2_card2=license_plate2_card2, province_car2_card2=province_car2_card2,
                home_form=home_form, company_form=company_form, car_form=car_form, car_form2=car_form2, user_form=user_form, identity_form=identity_form,
                phone_form=phone_form, home_form_card2=home_form_card2, company_form_card2=company_form_card2, car_form3=car_form3, car_form4=car_form4, ktb_ac=ktb_ac, ref1=ref1, term_seq=term_seq)

    if request.method == 'POST' and (user_form.name.data != '' or user_form.last_name.data != ''):
        first_name = user_form.name.data
        last_name = user_form.last_name.data
        if first_name == '' and last_name != '':
            Customer_register.query.filter_by(Id=current_user.Id).update(
                {Customer_register.last_name: last_name})
            pm = Parking_member.query.filter_by(
                identity_card=current_user.identity_card).all()
            for m in pm:
                m.last_name_th = last_name
            pl = Parking_log.query.filter_by(
                identity_card=current_user.identity_card).all()
            for l in pl:
                l.last_name = last_name
        elif first_name != '' and last_name == '':
            Customer_register.query.filter_by(Id=current_user.Id).update(
                {Customer_register.first_name: first_name})
            pm = Parking_member.query.filter_by(
                identity_card=current_user.identity_card).all()
            for m in pm:
                m.first_name_th = first_name
            pl = Parking_log.query.filter_by(
                identity_card=current_user.identity_card).all()
            for l in pl:
                l.first_name = first_name
        elif first_name != '' and last_name != '':
            Customer_register.query.filter_by(Id=current_user.Id).update(
                {Customer_register.last_name: last_name, Customer_register.first_name: first_name})
            pm = Parking_member.query.filter_by(
                identity_card=current_user.identity_card).all()
            for m in pm:
                m.last_name_th = last_name
                m.first_name_th = first_name
            pl = Parking_log.query.filter_by(
                identity_card=current_user.identity_card).all()
            for l in pl:
                l.last_name = last_name
                l.first_name = first_name
        else:
            pass
        db.session.commit()
        return redirect(url_for('customer_profile'))

    elif request.method == 'POST' and identity_form.identity.data != '':
        identity_card = identity_form.identity.data
        if len(identity_card) != 13:
            flash('Identity card to short!', category='danger')
        elif identity_card != '':
            Customer_register.query.filter_by(Id=current_user.Id).update(
                {Customer_register.identity_card: identity_card})
        elif identity_card == '':
            pass

        db.session.commit()
        return redirect(url_for('customer_profile'))

    elif request.method == 'POST' and phone_form.phone.data != '':
        print('phone form '*40)
        phone = phone_form.phone.data
        if phone != '':
            Customer_register.query.filter_by(Id=current_user.Id).update(
                {Customer_register.phone: phone})
            pm = Parking_member.query.filter_by(
                identity_card=current_user.identity_card).all()
            for m in pm:
                m.phone = phone
            pl = Parking_log.query.filter_by(
                identity_card=current_user.identity_card).all()
            for l in pl:
                l.phone = phone
        db.session.commit()
        return redirect(url_for('customer_profile'))

    elif request.method == 'POST' and (
        home_form.address_no.data != '' or home_form.village.data != '' or home_form.unit_home1.data != '' or home_form.province.data != None or
            home_form.district.data != None or home_form.sub_district.data != None or home_form.postal_code.data != None):
        address_no = home_form.address_no.data
        village = home_form.village.data
        province = home_form.province.data
        district = home_form.district.data
        sub_district = home_form.sub_district.data
        postal_code = home_form.postal_code.data
        unit_home = home_form.unit_home1.data
        print(unit_home)
        print('--')
        if address_no != '' and address_no != ' ' and address_no != None:
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.address_no: address_no})
        if village != '' and village != ' ' and village != None:
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.village: village})
        if province != '' and province != ' ' and province != None:
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.province: province})
        if district != '' and district != ' ' and district != None:
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.district: district})
        if sub_district != '' and sub_district != ' ' and sub_district != None:
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.sub_district: sub_district})
        if postal_code != '' and postal_code != ' ' and postal_code != None:
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.postal_code: postal_code})
        if unit_home != '' and unit_home != ' ' and unit_home != None:
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.unit_home: unit_home})

        db.session.commit()
        return redirect(url_for('customer_profile'))

    elif request.method == 'POST' and (
        company_form.company_no.data != '' or company_form.company_village.data != '' or company_form.unit_company1.data != '' or company_form.identity_com1.data != '' or company_form.company_province.data != None or
            company_form.company_district.data != None or company_form.company_sub_district.data != None or company_form.company_postal_code.data != None):
        company_no = company_form.company_no.data
        company_village = company_form.company_village.data
        company_province = company_form.company_province.data
        company_district = company_form.company_district.data
        company_sub_district = company_form.company_sub_district.data
        company_postal_code = company_form.company_postal_code.data
        identity_com = company_form.identity_com1.data
        unit_company = company_form.unit_company1.data
        if company_no != '':
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.company_no: company_no})
        if company_village != '':
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.company_village: company_village})
        if company_province != '' and company_province != ' ' and company_province != None:
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.company_province: company_province})
        if company_district != '' and company_district != ' ' and company_district != None:
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.company_district: company_district})
        if company_sub_district != '' and company_sub_district != ' ' and company_sub_district != None:
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.company_sub_district: company_sub_district})
        if company_postal_code != '' and company_postal_code != ' ' and company_postal_code != None:
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.company_postal_code: company_postal_code})
        if identity_com != '':
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.identity_com: identity_com})
        if unit_company != '':
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.unit_company: unit_company})
        db.session.commit()
        return redirect(url_for('customer_profile'))

    elif request.method == 'POST' and (
            car_form.license_plate1.data != '' or car_form.brand_name1.data != None or car_form.color1.data != '' or
            car_form.province_car1.data != None):
        license_plate = car_form.license_plate1.data
        color = car_form.color1.data
        brand_name = car_form.brand_name1.data
        province = car_form.province_car1.data
        if license_plate != '':
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.license_plate1: license_plate})
        if color != '':
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.color1: color})
        if brand_name != None and brand_name != '' and brand_name != ' ':
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.brand_name1: brand_name})
        if province != None and province != '' and province != ' ':
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.province_car1: province})
        db.session.commit()
        return redirect(url_for('customer_profile'))

    elif request.method == 'POST' and (
            car_form2.license_plate2.data != '' or car_form2.brand_name2.data != None or car_form2.color2.data != '' or
            car_form2.province_car2.data != None):
        license_plate = car_form2.license_plate2.data
        brand_name = car_form2.brand_name2.data
        color = car_form2.color2.data
        province = car_form2.province_car2.data
        if license_plate != '':
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.license_plate2: license_plate})
        if color != '':
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.color2: color})
        if brand_name != None and brand_name != '' and brand_name != ' ':
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.brand_name2: brand_name})
        if province != None and province != '' and province != ' ':
            Parking_member.query.filter_by(Id=cards[0].Id).update(
                {Parking_member.province_car2: province})
        db.session.commit()
        return redirect(url_for('customer_profile'))

    # --------------------------------------card2-----------------------------------------------------
    elif request.method == 'POST' and (
        home_form_card2.address_no_card2.data != '' or home_form_card2.village_card2.data != '' or home_form_card2.unit_home2.data != '' or home_form_card2.province_card2.data != None or
            home_form_card2.district_card2.data != None or home_form_card2.sub_district_card2.data != None or home_form_card2.postal_code_card2.data != None):
        address_no = home_form_card2.address_no_card2.data
        village = home_form_card2.village_card2.data
        province = home_form_card2.province_card2.data
        district = home_form_card2.district_card2.data
        sub_district = home_form_card2.sub_district_card2.data
        postal_code = home_form_card2.postal_code_card2.data
        unit_home = home_form_card2.unit_home2.data

        if address_no != '' and address_no != ' ' and address_no != None:
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.address_no: address_no})
        if village != '' and village != ' ' and village != None:
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.village: village})
        if province != '' and province != ' ' and province != None:
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.province: province})
        if district != '' and district != ' ' and district != None:
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.district: district})
        if sub_district != '' and sub_district != ' ' and sub_district != None:
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.sub_district: sub_district})
        if postal_code != '' and postal_code != ' ' and postal_code != None:
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.postal_code: postal_code})
        if unit_home != '' and unit_home != ' ' and unit_home != None:
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.unit_home: unit_home})

        db.session.commit()
        return redirect(url_for('customer_profile'))

    elif request.method == 'POST' and (
        company_form_card2.company_no_card2.data != '' or company_form_card2.company_village_card2.data != '' or company_form_card2.unit_company2.data != '' or company_form_card2.identity_com2.data != '' or company_form_card2.company_province_card2.data != None or
            company_form_card2.company_district_card2.data != None or company_form_card2.company_sub_district_card2.data != None or company_form_card2.company_postal_code_card2.data != None):
        company_no = company_form_card2.company_no_card2.data
        company_village = company_form_card2.company_village_card2.data
        company_province = company_form_card2.company_province_card2.data
        company_district = company_form_card2.company_district_card2.data
        company_sub_district = company_form_card2.company_sub_district_card2.data
        company_postal_code = company_form_card2.company_postal_code_card2.data
        identity_com = company_form_card2.identity_com2.data
        unit_company = company_form_card2.unit_company2.data
        if company_no != '':
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.company_no: company_no})
        if company_village != '':
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.company_village: company_village})
        if company_province != '' and company_province != ' ' and company_province != None:
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.company_province: company_province})
        if company_district != '' and company_district != ' ' and company_district != None:
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.company_district: company_district})
        if company_sub_district != '' and company_sub_district != ' ' and company_sub_district != None:
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.company_sub_district: company_sub_district})
        if company_postal_code != '' and company_postal_code != ' ' and company_postal_code != None:
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.company_postal_code: company_postal_code})
        if unit_company != '':
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.unit_company: unit_company})
        if identity_com != '':
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.identity_com: identity_com})
        db.session.commit()
        return redirect(url_for('customer_profile'))

    elif request.method == 'POST' and (
            car_form3.license_plate1_card2.data != '' or car_form3.brand_name1_card2.data != None or car_form3.color1_card2.data != '' or
            car_form3.province_car1_card2.data != None):
        license_plate = car_form3.license_plate1_card2.data
        color = car_form3.color1_card2.data
        brand_name = car_form3.brand_name1_card2.data
        province = car_form3.province_car1_card2.data

        if license_plate != '':
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.license_plate1: license_plate})
        if color != '':
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.color1: color})
        if brand_name != None and brand_name != '' and brand_name != ' ':
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.brand_name1: brand_name})
        if province != None and province != '' and province != ' ':
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.province_car1: province})
        db.session.commit()
        return redirect(url_for('customer_profile'))

    elif request.method == 'POST' and (
            car_form4.license_plate2_card2.data != '' or car_form4.brand_name2_card2.data != None or car_form4.color2_card2.data != '' or
            car_form4.province_car2_card2.data != None):
        license_plate = car_form4.license_plate2_card2.data
        color = car_form4.color2_card2.data
        brand_name = car_form4.brand_name2_card2.data
        province = car_form4.province_car2_card2.data

        if license_plate != '':
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.license_plate2: license_plate})
        if color != '':
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.color2: color})
        if brand_name != None and brand_name != '' and brand_name != ' ':
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.brand_name2: brand_name})
        if province != None and province != '' and province != ' ':
            Parking_member.query.filter_by(Id=cards[1].Id).update(
                {Parking_member.province_car2: province})
        db.session.commit()
        return redirect(url_for('customer_profile'))

    elif password_form.validate_on_submit():

        newpass = password_form.password.data
        current_user.password = bcrypt.generate_password_hash(
            newpass).decode('utf-8')
        db.session.commit()
        return redirect(url_for('customer_profile'))

    if password_form.errors != {}:
        for err_from, err_msg in zip(password_form.errors, password_form.errors.values()):
            flash(err_msg[0],
                  category='danger')
        return redirect(url_for('customer_profile'))

###################################################################################################


@app.route('/logout')
def logout():
    user_log = Login_logout_log.query.filter_by(
        user=current_user.email).order_by(Login_logout_log.Id.desc()).first()
    user_log.logout_datetime = datetime.datetime.today()
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))


@app.route('/district/<province>')
def district(province):
    if province == '':
        province = None
    district = get_district(province)
    return jsonify({'districtlist': district})


@app.route('/subdistrict/<province>/<district>')
def subdistrict(province, district):
    subdistrict = get_subdistrict(province, district)

    return jsonify({'subdistrictlist': subdistrict})


@app.route('/postcode/<province>/<district>/<subdistrict>')
def postcode(province, district, subdistrict):
    postcode = get_postcode(province, district, subdistrict)
    return jsonify({'postcodelist': postcode})


@app.route('/profile_image', methods=['POST'])
def profile_image():
    image = request.files['imageUpload']
    path = r'C:\D\project_mrta_parkingApp\mrta-app\static\image\manage\profile'
    image_path = os.path.join(path, secure_filename(
        current_user.identity_card + '_'+str(current_user.Id)+'.'+image.filename.split('.')[1]))
    list_file = os.listdir(path)
    for i in list_file:
        if i.startswith(current_user.identity_card + '_'+str(current_user.Id)):
            os.remove(os.path.join(path, i))
    image.save(image_path)
    current_user.profile = current_user.identity_card + '_' + \
        str(current_user.Id)+'.'+image.filename.split('.')[1]
    db.session.commit()
    return redirect(url_for('customer_profile'))


@app.route('/uat/payment-methods/address_info/<id_>/<address_type>')
def address_info(id_, address_type):
    log = Parking_log.query.filter_by(Id=id_).first()
    member = Parking_member.query.filter_by(card_id=log.card_id).filter(
        Parking_member.parking_code == log.parking_code).first()
    if address_type == 'company':
        address = f'ชื่อ: {member.first_name_th} {member.last_name_th} <br>'
        address += f'ที่อยู่: {member.company_no} ตำบล {member.company_sub_district} <br>'
        address += f'อำเภอ {member.company_district} จังหวัด {member.company_province} {member.company_postal_code}'
    if address_type != 'company':
        address = f'ชื่อ: {member.first_name_th} {member.last_name_th} <br>'
        address += f'ที่อยู่: {member.address_no} ตำบล {member.sub_district} <br>'
        address += f'อำเภอ {member.district} จังหวัด {member.province} {member.postal_code}'
    print(address)
    return jsonify({'address': address})


@app.route('/address_info/<id_>/<address_type>')
def address_info2(id_, address_type):
    log = Parking_log.query.filter_by(Id=id_).first()
    member = Parking_member.query.filter_by(card_id=log.card_id).filter(
        Parking_member.parking_code == log.parking_code).filter(or_(Parking_member.card_status == '1',Parking_member.card_status == None)).first()
    if address_type == 'company':
        address = f'ชื่อ: {member.first_name_th} {member.last_name_th} <br>'
        address += f'ที่อยู่: {member.company_no} ตำบล {member.company_sub_district} <br>'
        address += f'อำเภอ {member.company_district} จังหวัด {member.company_province} {member.company_postal_code}'
    if address_type != 'company':
        address = f'ชื่อ: {member.first_name_th} {member.last_name_th} <br>'
        address += f'ที่อยู่: {member.address_no} ตำบล {member.sub_district} <br>'
        address += f'อำเภอ {member.district} จังหวัด {member.province} {member.postal_code}'
    print(address)
    return jsonify({'address': address})


@app.route('/modal_address/<type_>/<id_>')
def modal_address(type_, id_):
    member = Parking_member.query.filter_by(Id=id_).first()
    if type_ == 'home':
        address = [{
            'address_no': member.address_no,
            'unit': member.unit_home,
            'village': member.village,
            'province': member.province,
            'district': member.district,
            'sub_district': member.sub_district,
            'postal_code': member.postal_code
        }]
    elif type_ == 'company':
        address = [{
            'address_no': member.company_no,
            'unit': member.company_unit,
            'village': member.company_village,
            'province': member.company_province,
            'district': member.company_district,
            'sub_district': member.company_sub_district,
            'postal_code': member.company_postal_code,
            'identity_com': member.identity_com
        }]
    return jsonify(address)


@app.route('/update_address_home', methods=['POST'])
def update_address_home():
    address_no = request.form.get('address_no')
    unit = request.form.get('unit')
    village = request.form.get('village')
    province = request.form.get('province')
    district = request.form.get('district')
    sub_district = request.form.get('sub_district')
    postal_code = request.form.get('postal_code')
    member_id = request.form.get('member_id')
    print(request.form)
    update_mem = Parking_member.query.filter_by(Id=member_id).first()
    update_mem.address_no = address_no
    update_mem.unit_home = unit
    update_mem.village = village
    update_mem.province = province
    update_mem.district = district
    update_mem.sub_district = sub_district
    update_mem.postal_code = postal_code
    db.session.commit()

    return redirect(url_for('parking_payment'))


@app.route('/update_address_work', methods=['POST'])
def update_address_work():
    address_no = request.form.get('address_no')
    unit = request.form.get('unit')
    village = request.form.get('village')
    province = request.form.get('province')
    district = request.form.get('district')
    sub_district = request.form.get('sub_district')
    postal_code = request.form.get('postal_code')
    member_id = request.form.get('member_id')
    identity_com = request.form.get('identity_com')

    update_mem = Parking_member.query.filter_by(Id=member_id).first()
    update_mem.company_no = address_no
    update_mem.company_unit = unit
    update_mem.company_village = village
    update_mem.company_province = province
    update_mem.company_district = district
    update_mem.company_sub_district = sub_district
    update_mem.company_postal_code = postal_code
    update_mem.identity_com = identity_com
    db.session.commit()
    return redirect(url_for('parking_payment'))


@app.route('/province_')
def province_():
    province = get_province()
    return jsonify({'province': province})


@app.route('/delete_account')
def delete_account():
    current_user.delete_date = datetime.date.today()
    db.session.commit()
    logout_user()
    flash('ขอบคุณที่ใช้บริการ', category='success')

    return redirect(url_for('index'))


@app.route('/checkdupcard/<id_card>/<station>')
def check_card_id_(id_card, station):
    print(id_card)
    print(station)
    parking_code = Parking_manage.query.filter_by(
        parking_name=station).first().parking_code
    card = Parking_member.query.filter_by(card_id=id_card).filter(Parking_member.parking_code == parking_code)\
        .filter(or_(Parking_member.card_status == '1', Parking_member.card_status == None)).first()
    if card:
        return jsonify({'status': 'dup'})
    else:
        return jsonify({'status': 'not dup'})


#policy
@app.route('/term')
def term_th():
    return render_template('term.html')


@app.route('/privacy')
def privacy_th():
    return render_template('privacy.html')

#FAQ


@app.route('/th-faq')
def faq_th():
    return render_template('faq.html')

#line-OA


@app.route('/video01')
def video_01():
    return render_template('video01.html')


@app.route('/test')
def canva_01():
    return render_template('2canva.html')


@app.route('/appdownload')
def download_01():
    return render_template('appdownload.html')


@app.route('/notification-list')
def notification_list():
    messages = Message_box.query.filter_by(
        identity_card=current_user.identity_card).all()
    print(messages)
    return render_template('notification-list.html', messages=messages)


@app.route('/message_box')
def message_box():
    messages_box = Message_box.query.filter_by(
        identity_card=current_user.identity_card).all()
    messages = []
    for message in messages_box:
        d = {}
        d['id'] = message.Id
        d['card_id'] = message.card_id
        d['des_noti'] = message.des_noti
    return jsonify(messages)


@app.route('/waiting-confirm')
def waiting_confirm():
    return render_template('waiting-confirm.html')

# ใบเสร็จอย่างย่อ


@app.route('/receipt')
def receipt():
    return render_template('receipt.html')


# เพิ่มหน้า bill pop  version 2 Tee
@app.route('/billpopup')
def billpopupt():
    return render_template('billpopup.html')

# เพิ่มหน้า billslist  version 2 Tee


@app.route('/billslist')
def billslist():
    return render_template('billslist.html')

# เพิ่มหน้า popup-gatein  version 2 Tee


@app.route('/popup-gatein')
def popup_gatein():
    return render_template('popup-gatein.html')

# เพิ่มหน้า  reserve-payment-success  version 2 Tee


@app.route('/reserve-payment-success')
def reserve_payment_success():
    return render_template('reserve-payment-success.html')

# เพิ่มหน้า  history-parking-detaill  version 2 Tee


@app.route('/history-parking-detaill')
def history_parking_detaill():
    return render_template('history-parking-detaill.html')

# เพิ่มหน้า bill  version 2 Aof


@app.route('/bill')
def bill():
    return render_template('bill.html')


# เพิ่มหน้า bill-detail  version 2 Aof
@app.route('/bill-detail')
def bill_detail():
    return render_template('bill-detail.html')


# เพิ่มหน้า notifications  version 2 Aof
@app.route('/notifications')
def notifications():
    return render_template('notifications.html')


# เพิ่มหน้า qrcode  version 2 Aof
@app.route('/qrcode')
def qr_code():
    return render_template('qrcode.html')


# เพิ่มหน้า history-reserve-parking  version 2 Aof
@app.route('/history-reserve-parking')
def history_reserve_parking():
    return render_template('history-reserve-parking.html')


# เพิ่มหน้า orangeparking-spaces  version 2 Aof
@app.route('/orangeparking-spaces')
def orangeparking_spaces():
    return render_template('orangeparking-spaces.html')


# เพิ่มหน้า allparking-spaces-empty  version 2 Aof
@app.route('/allparking-spaces-empty')
def allparking_spaces_empty():
    return render_template('allparking-spaces-empty.html')


# เพิ่มหน้า car-list  version 2 Aof
@app.route('/car-list')
def car_list():
    return render_template('car-list.html')


# เพิ่มหน้า find-mycar  version 2 Aof
@app.route('/find-mycar')
def find_mycar():
    return render_template('find-mycar.html')


# เพิ่มหน้า more  version 2 Aof
@app.route('/more')
def more():
    return render_template('more.html')

# @app.route('/api/testmail')
# def testmail():
#     msg = Message('Reset Password',
#                         sender='parkandride@mrta.co.th', recipients=['kowdhon@gmail.com'])
#     msg.body = f'Please click this link for reset password : '
#     mail.send(msg)
#     return jsonify({'message':'success'})


@app.route('/api/check-reserve')
def check_reserve():
    today = datetime.datetime.today()
    Parking = Parking_log.query.filter(Parking_log.identity_card == current_user.identity_card)\
        .order_by(Parking_log.parking_reserve_date.desc()).first()
    print(Parking)
    # payment_exp = Parking.parking_reserve_date + datetime.timedelta(minutes=10)
    if Parking.qr_show_exp == None:
        return jsonify({'message':None})
    elif Parking.qr_show_exp > today :
        return jsonify({'message':'qrcode'})
    return jsonify({'message':None})

@app.route('/api/v1/blue-line/create-myqrcode-for-dev',methods=["POST"])
def create_myqrcode_for_dev():
    request_body = request.get_json()
    identity_card = request_body.get('identity_card')
    mockqrcode = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
    new_logvisitor = Parking_logvisitor(
        qrcode=mockqrcode,
        identity_card = identity_card,
        deactivate='0'
    )
    db.session.add(new_logvisitor)
    db.session.commit()
    return jsonify({'id':new_logvisitor.id,'qrcode':mockqrcode})

@app.errorhandler(500)
def handle_bad_request(e):
    return '<h1>Apologize for any inconvenience , Something went wrong</h1>', 500

import smartparking_app.mockmyqrcode
#smartparking
inject()

if __name__ == '__main__':

    app.run(debug=False)
