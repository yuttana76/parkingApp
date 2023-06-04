from datetime import datetime
from sqlalchemy.sql.expression import text
from app import Parking_manage
import requests
from bs4 import BeautifulSoup as bs
import json
import os 

url = 'https://bds.mrta.co.th/BDS/service/SvcPRt.asmx/GetParkRT?AccessKey=gqQPvm29Sf.pOPEtlQSr9.7dvYSKLe2A=='
def get_button(line):
    if line == 'สายสีน้ำเงิน':
        return 'box-parking1'
    elif line == 'สายสีม่วง':
        return 'box-parking2'
    elif line == 'สายสีเขียว':
        return 'box-parking3'
    
with open(r"{}".format(os.environ['NCARREM_FILE']),'r',encoding='utf-8') as ncarrem_json:
    read_carrem_json = json.load(ncarrem_json)
    
    
def popNput(obj,data_to_json):
    for index,line in enumerate(data_to_json):
        if line['name'] == obj['name']:
            data_to_json.pop(index)
            data_to_json.append(obj)
            break
    else:
        data_to_json.append(obj)
    return data_to_json

def retrieveNcarrem(obj,data_to_json):
    for line in data_to_json:
        if line['name'] == obj['name']:
            obj['ncarrem'] = line['ncarrem']
            obj['date'] = line['date']
            break
    else:
        return obj
    return obj

def get_api_parking():
    data_to_json = read_carrem_json.copy()
    try :
        res = requests.get(url,timeout=0.5)
        res.encoding = 'utf-8'
        soup = bs(res.text,'html.parser')
        data = []
        all_station = Parking_manage.query.all()
        station_list = [(i.latitude,i.longitude,i.parking_name,i.line_name,i.parking_status) for i in all_station]
        cups = soup.find_all('table')
        for lat,long,name,line,status in station_list:
            json_data = {}
            station_dict = {}
            if name == 'สถานีสุขุมวิท':
                continue
            for cup in cups:
                if name == 'สถานีหลักสอง':
                    ncarrem = 0
                    for cup in cups:
                        if cup.find('latitude').text == lat and cup.find('longitude').text == long:
                            scrapping_text = cup.find('ncarrem').text
                            if scrapping_text.isnumeric():
                                ncarrem += int(scrapping_text)
                    station_dict['name'] = name
                    station_dict['color'] = get_button(line)
                    station_dict['ncarrem'] = ncarrem
                    station_dict['date'] = datetime.today().strftime('%Y/%m/%d %H:%M:%S')
                elif cup.find('latitude').text == lat and cup.find('longitude').text == long:
                    station_dict['name'] = name
                    station_dict['color'] = get_button(line)
                    ncarrem = cup.find('ncarrem').text
                    station_dict['ncarrem'] = ncarrem if ncarrem == 'N/A' or int(ncarrem) >= 0 else 0
                    station_dict['date'] = datetime.today().strftime('%Y/%m/%d %H:%M:%S')
                else:
                    continue
            if station_dict == {}:
                station_dict['name'] = name
                station_dict['color'] = get_button(line)
                station_dict['ncarrem'] = 'N/A'
                station_dict['date'] = datetime.today().strftime('%Y/%m/%d %H:%M:%S')
            if name in ['สถานีห้วยขวาง','สถานีศูนย์วัฒนธรรม (อาคารจอด)','สถานีเพชรบุรี','สถานีแยก คปอ.','สถานีคูคต']:
                station_dict['button'] = 'submit'
            elif status == 'inactive':
                station_dict['button'] = 'button'
            else:
                station_dict['button'] = 'submit'
            if name not in ['สถานีศูนย์วัฒนธรรม (ลาน1)','สถานีศูนย์วัฒนธรรม (รัชดาภิเษกซอย 6)','ฝั่งตรงข้ามศูนย์การประชุมแห่งชาติสิริกิติ์']:
                if station_dict['ncarrem'] != 'N/A':
                    json_data['name'] = station_dict['name']
                    json_data['ncarrem'] = station_dict['ncarrem']
                    json_data['date'] = station_dict['date']
                    data_to_json = popNput(json_data,data_to_json)
                else:
                    station_dict = retrieveNcarrem(station_dict,data_to_json)
                data.append(station_dict)
        if data_to_json != read_carrem_json:
            with open(r"{}".format(os.environ['NCARREM_FILE']),'w',encoding='utf-8') as write_to_ncarrem_json:
                json.dump(data_to_json,write_to_ncarrem_json,ensure_ascii=False)
        return data
    except Exception as e:
        data = []
        all_station = Parking_manage.query.all()
        station_list = [(i.latitude,i.longitude,i.parking_name,i.line_name,i.parking_status) for i in all_station]
        for lat,long,name,line,status in station_list:
            station_dict = {}
            if station_dict == {}:
                station_dict['name'] = name
                station_dict['color'] = get_button(line)
                station_dict['ncarrem'] = 'N/A'
                station_dict['date'] = datetime.today().strftime('%Y/%m/%d %H:%M:%S')
            if name in ['สถานีห้วยขวาง','สถานีศูนย์วัฒนธรรม (อาคารจอด)','สถานีเพชรบุรี','สถานีแยก คปอ.','สถานีคูคต']:
                station_dict['button'] = 'submit'
            elif status == 'inactive':
                station_dict['button'] = 'button'
            else:
                station_dict['button'] = 'submit'
            if name not in ['สถานีศูนย์วัฒนธรรม (ลาน1)','สถานีศูนย์วัฒนธรรม (รัชดาภิเษกซอย 6)','ฝั่งตรงข้ามศูนย์การประชุมแห่งชาติสิริกิติ์']:
                if station_dict['ncarrem'] == 'N/A':
                    station_dict = retrieveNcarrem(station_dict,data_to_json)
                data.append(station_dict)
        return data
def get_api_parking_eng():
    data_to_json = read_carrem_json.copy()
    try:
        res = requests.get(url,timeout=0.5)
        res.encoding = 'utf-8'
        soup = bs(res.text,'html.parser')
        data = []
        all_station = Parking_manage.query.all()
        station_list = [(i.latitude,i.longitude,i.parking_name_eng,i.line_name,i.parking_status,i.parking_name) for i in all_station]
        cups = soup.find_all('table')
        json_data = {}
        for lat,long,name,line,status,nameth in station_list:
            station_dict = {}
            for cup in cups:
                if nameth == 'สถานีหลักสอง':
                    ncarrem = 0
                    for cup in cups:
                        if cup.find('latitude').text == lat and cup.find('longitude').text == long:
                            scrapping_text = cup.find('ncarrem').text
                            if scrapping_text.isnumeric():
                                ncarrem += int(scrapping_text)
                    station_dict['name'] = name
                    station_dict['color'] = get_button(line)
                    station_dict['ncarrem'] = ncarrem
                    station_dict['nameth'] = nameth
                    station_dict['date'] = datetime.today().strftime('%Y/%m/%d %H:%M:%S')
                elif cup.find('latitude').text == lat and cup.find('longitude').text == long:
                    station_dict['name'] = name
                    station_dict['nameth'] = nameth
                    station_dict['color'] = get_button(line)
                    ncarrem = cup.find('ncarrem').text
                    station_dict['ncarrem'] = ncarrem if ncarrem == 'N/A' or int(ncarrem) >= 0 else 0
                    station_dict['date'] = datetime.today().strftime('%Y/%m/%d %H:%M:%S')
                else:
                    continue
            if station_dict == {}:
                station_dict['name'] = name
                station_dict['nameth'] = nameth
                station_dict['color'] = get_button(line)
                station_dict['ncarrem'] = 'N/A'
                station_dict['date'] = datetime.today().strftime('%Y/%m/%d %H:%M:%S')
            if nameth in ['สถานีห้วยขวาง','สถานีศูนย์วัฒนธรรม (อาคารจอด)','สถานีเพชรบุรี','สถานีแยก คปอ.','สถานีคูคต']:
                station_dict['button'] = 'submit'
            elif status == 'inactive':
                station_dict['button'] = 'button'
            else:
                station_dict['button'] = 'submit'
            if nameth not in ['สถานีศูนย์วัฒนธรรม (ลาน1)','สถานีศูนย์วัฒนธรรม (รัชดาภิเษกซอย 6)','ฝั่งตรงข้ามศูนย์การประชุมแห่งชาติสิริกิติ์']:
                if station_dict['ncarrem'] != 'N/A':
                    json_data['name'] = station_dict['nameth']
                    json_data['ncarrem'] = station_dict['ncarrem']
                    json_data['date'] = station_dict['date']
                    data_to_json = popNput(json_data,data_to_json)
                else:
                    station_dict = retrieveNcarrem(station_dict,data_to_json)
                data.append(station_dict)
        if data_to_json != read_carrem_json:
            with open(r"{}".format(os.environ['NCARREM_FILE']),'w',encoding='utf-8') as write_to_ncarrem_json:
                json.dump(data_to_json,write_to_ncarrem_json,ensure_ascii=False)
        return data
    except:
        data = []
        all_station = Parking_manage.query.all()
        station_list = [(i.latitude,i.longitude,i.parking_name_eng,i.line_name,i.parking_status,i.parking_name) for i in all_station]
        for lat,long,name,line,status,nameth in station_list:
            station_dict = {}
            if station_dict == {}:
                station_dict['name'] = name
                station_dict['nameth'] = nameth
                station_dict['color'] = get_button(line)
                station_dict['ncarrem'] = 'N/A'
                station_dict['date'] = datetime.today().strftime('%Y/%m/%d %H:%M:%S')
            if nameth in ['สถานีห้วยขวาง','สถานีศูนย์วัฒนธรรม (อาคารจอด)','สถานีเพชรบุรี','สถานีแยก คปอ.','สถานีคูคต']:
                station_dict['button'] = 'submit'
            elif status == 'inactive':
                station_dict['button'] = 'button'
            else:
                station_dict['button'] = 'submit'
            if nameth not in ['สถานีศูนย์วัฒนธรรม (ลาน1)','สถานีศูนย์วัฒนธรรม (รัชดาภิเษกซอย 6)','ฝั่งตรงข้ามศูนย์การประชุมแห่งชาติสิริกิติ์']:
                if station_dict['ncarrem'] == 'N/A':
                    station_dict = retrieveNcarrem(station_dict,data_to_json)
                data.append(station_dict)
        return data

def get_blueline():
    data_to_json = read_carrem_json.copy()
    try:
        res = requests.get(url,timeout=0.5)
        res.encoding = 'utf-8'
        soup = bs(res.text,'html.parser')
        data = []
        all_blue = Parking_manage.query.filter_by(line_name = 'สายสีน้ำเงิน').all()
        station_list = [(i.latitude,i.longitude,i.parking_name,i.parking_status) for i in all_blue]
        cups = soup.find_all('table')
        for lat,long,name,status in station_list:
            station_dict = {}
            for cup in cups:
                if name == 'สถานีหลักสอง':
                    ncarrem = 0
                    for cup in cups:
                        if cup.find('latitude').text == lat and cup.find('longitude').text == long:
                            scrapping_text = cup.find('ncarrem').text
                            if scrapping_text.isnumeric():
                                ncarrem += int(scrapping_text)
                    station_dict['name'] = name
                    station_dict['color'] = 'box-parking1'
                    station_dict['ncarrem'] = ncarrem
                elif cup.find('latitude').text == lat and cup.find('longitude').text == long:
                    station_dict['name'] = name
                    station_dict['color'] = 'box-parking1'
                    ncarrem = cup.find('ncarrem').text
                    station_dict['ncarrem'] = ncarrem if ncarrem == 'N/A' or int(ncarrem) >= 0 else 0
                else:
                    continue
            if station_dict =={}:
                station_dict['name'] = name
                station_dict['ncarrem'] = 'N/A'
                station_dict['color'] = 'box-parking1'
            if name in ['สถานีห้วยขวาง','สถานีศูนย์วัฒนธรรม (อาคารจอด)','สถานีเพชรบุรี','สถานีแยก คปอ.','สถานีคูคต']:
                station_dict['button'] = 'submit'
            elif status == 'inactive':
                station_dict['button'] = 'button'
            else:
                station_dict['button'] = 'submit'
            if name not in ['สถานีศูนย์วัฒนธรรม (ลาน1)','สถานีศูนย์วัฒนธรรม (รัชดาภิเษกซอย 6)','ฝั่งตรงข้ามศูนย์การประชุมแห่งชาติสิริกิติ์']:
                if station_dict['ncarrem'] == 'N/A':
                    station_dict = retrieveNcarrem(station_dict,data_to_json)
                data.append(station_dict)
        return data
    except:
        data = []
        all_blue = Parking_manage.query.filter_by(line_name = 'สายสีน้ำเงิน').all()
        station_list = [(i.latitude,i.longitude,i.parking_name,i.parking_status) for i in all_blue]
        for lat,long,name,status in station_list:
            station_dict = {}
            if station_dict =={}:
                station_dict['name'] = name
                station_dict['ncarrem'] = 'N/A'
                station_dict['color'] = 'box-parking1'
            if name in ['สถานีห้วยขวาง','สถานีศูนย์วัฒนธรรม (อาคารจอด)','สถานีเพชรบุรี','สถานีแยก คปอ.','สถานีคูคต']:
                station_dict['button'] = 'submit'
            elif status == 'inactive':
                station_dict['button'] = 'button'
            else:
                station_dict['button'] = 'submit'
            if name not in ['สถานีศูนย์วัฒนธรรม (ลาน1)','สถานีศูนย์วัฒนธรรม (รัชดาภิเษกซอย 6)','ฝั่งตรงข้ามศูนย์การประชุมแห่งชาติสิริกิติ์']:
                if station_dict['ncarrem'] == 'N/A':
                    station_dict = retrieveNcarrem(station_dict,data_to_json)
                data.append(station_dict)
        return data

def get_blueline_eng():
    data_to_json = read_carrem_json.copy()
    try:
        res = requests.get(url,timeout=0.5)
        res.encoding = 'utf-8'
        soup = bs(res.text,'html.parser')
        data = []
        all_blue = Parking_manage.query.filter_by(line_name = 'สายสีน้ำเงิน').all()
        station_list = [(i.latitude,i.longitude,i.parking_name_eng,i.parking_status,i.parking_name) for i in all_blue]
        cups = soup.find_all('table')
        for lat,long,name,status,nameth in station_list:
            station_dict = {}
            for cup in cups:
                if nameth == 'สถานีหลักสอง':
                    ncarrem = 0
                    for cup in cups:
                        if cup.find('latitude').text == lat and cup.find('longitude').text == long:
                            scrapping_text = cup.find('ncarrem').text
                            if scrapping_text.isnumeric():
                                ncarrem += int(scrapping_text)
                    station_dict['name'] = name
                    station_dict['color'] = 'box-parking1'
                    station_dict['ncarrem'] = ncarrem
                    station_dict['nameth'] = nameth
                elif cup.find('latitude').text == lat and cup.find('longitude').text == long:
                    station_dict['name'] = name
                    station_dict['nameth'] = nameth
                    station_dict['color'] = 'box-parking1'
                    ncarrem = cup.find('ncarrem').text
                    station_dict['ncarrem'] = ncarrem if ncarrem == 'N/A' or int(ncarrem) >= 0 else 0
                else:
                    continue
            if station_dict =={}:
                station_dict['name'] = name
                station_dict['nameth'] = nameth
                station_dict['ncarrem'] = 'N/A'
                station_dict['color'] = 'box-parking1'
            if nameth in ['สถานีห้วยขวาง','สถานีศูนย์วัฒนธรรม (อาคารจอด)','สถานีเพชรบุรี','สถานีแยก คปอ.','สถานีคูคต']:
                station_dict['button'] = 'submit'
            elif status == 'inactive':
                station_dict['button'] = 'button'
            else:
                station_dict['button'] = 'submit'
            if nameth not in ['สถานีศูนย์วัฒนธรรม (ลาน1)','สถานีศูนย์วัฒนธรรม (รัชดาภิเษกซอย 6)','ฝั่งตรงข้ามศูนย์การประชุมแห่งชาติสิริกิติ์']:
                if station_dict['ncarrem'] == 'N/A':
                    station_dict = retrieveNcarrem(station_dict,data_to_json)
                data.append(station_dict)
        return data 
    except:
        data = []
        all_blue = Parking_manage.query.filter_by(line_name = 'สายสีน้ำเงิน').all()
        station_list = [(i.latitude,i.longitude,i.parking_name_eng,i.parking_status,i.parking_name) for i in all_blue]
        for lat,long,name,status,nameth in station_list:
            station_dict = {}
            if station_dict =={}:
                station_dict['name'] = name
                station_dict['nameth'] = nameth
                station_dict['ncarrem'] = 'N/A'
                station_dict['color'] = 'box-parking1'
            if nameth in ['สถานีห้วยขวาง','สถานีศูนย์วัฒนธรรม (อาคารจอด)','สถานีเพชรบุรี','สถานีแยก คปอ.','สถานีคูคต']:
                station_dict['button'] = 'submit'
            elif status == 'inactive':
                station_dict['button'] = 'button'
            else:
                station_dict['button'] = 'submit'
            if nameth not in ['สถานีศูนย์วัฒนธรรม (ลาน1)','สถานีศูนย์วัฒนธรรม (รัชดาภิเษกซอย 6)','ฝั่งตรงข้ามศูนย์การประชุมแห่งชาติสิริกิติ์']:
                if station_dict['ncarrem'] == 'N/A':
                    station_dict = retrieveNcarrem(station_dict,data_to_json)
                data.append(station_dict)
        return data

def get_purpleline():
    data_to_json = read_carrem_json.copy()
    try:
        res = requests.get(url,timeout=0.5)
        res.encoding = 'utf-8'
        soup = bs(res.text,'html.parser')
        data = []
        all_blue = Parking_manage.query.filter_by(line_name = 'สายสีม่วง').all()
        station_list = [(i.latitude,i.longitude,i.parking_name,i.parking_status) for i in all_blue]
        cups = soup.find_all('table')
        for lat,long,name,status in station_list:
            station_dict = {}
            for cup in cups:
                if cup.find('latitude').text == lat and cup.find('longitude').text == long:
                    station_dict['name'] = name
                    station_dict['color'] = 'box-parking2'
                    ncarrem = cup.find('ncarrem').text
                    station_dict['ncarrem'] = ncarrem if ncarrem == 'N/A' or int(ncarrem) >= 0 else 0
                else:
                    continue
            if station_dict =={}:
                station_dict['name'] = name
                station_dict['ncarrem'] = 'N/A'
                station_dict['color'] = 'box-parking2'
            if status =='inactive':
                station_dict['button'] = 'button'
            else:
                station_dict['button'] = 'submit'
            if station_dict['ncarrem'] == 'N/A':
                    station_dict = retrieveNcarrem(station_dict,data_to_json)
            data.append(station_dict)
        return data
    except:
        data = []
        all_blue = Parking_manage.query.filter_by(line_name = 'สายสีม่วง').all()
        station_list = [(i.latitude,i.longitude,i.parking_name,i.parking_status) for i in all_blue]
        for lat,long,name,status in station_list:
            station_dict = {}
            if station_dict =={}:
                station_dict['name'] = name
                station_dict['ncarrem'] = 'N/A'
                station_dict['color'] = 'box-parking2'
            if status =='inactive':
                station_dict['button'] = 'button'
            else:
                station_dict['button'] = 'submit'
            if station_dict['ncarrem'] == 'N/A':
                    station_dict = retrieveNcarrem(station_dict,data_to_json)
            data.append(station_dict)
        return data

def get_purpleline_eng():
    data_to_json = read_carrem_json.copy()
    try:
        res = requests.get(url,timeout=0.5)
        res.encoding = 'utf-8'
        soup = bs(res.text,'html.parser')
        data = []
        all_blue = Parking_manage.query.filter_by(line_name = 'สายสีม่วง').all()
        station_list = [(i.latitude,i.longitude,i.parking_name_eng,i.parking_status,i.parking_name) for i in all_blue]
        cups = soup.find_all('table')
        for lat,long,name,status,nameth in station_list:
            station_dict = {}
            for cup in cups:
                if cup.find('latitude').text == lat and cup.find('longitude').text == long:
                    station_dict['name'] = name
                    station_dict['nameth'] = nameth
                    station_dict['color'] = 'box-parking2'
                    ncarrem = cup.find('ncarrem').text
                    station_dict['ncarrem'] = ncarrem if ncarrem == 'N/A' or int(ncarrem) >= 0 else 0
                else:
                    continue
            if station_dict =={}:
                station_dict['name'] = name
                station_dict['nameth'] = nameth
                station_dict['ncarrem'] = 'N/A'
                station_dict['color'] = 'box-parking2'
            if status =='inactive':
                station_dict['button'] = 'button'
            else:
                station_dict['button'] = 'submit'
            if station_dict['ncarrem'] == 'N/A':
                    station_dict = retrieveNcarrem(station_dict,data_to_json)
            data.append(station_dict)
        return data
    except:
        data = []
        all_blue = Parking_manage.query.filter_by(line_name = 'สายสีม่วง').all()
        station_list = [(i.latitude,i.longitude,i.parking_name_eng,i.parking_status,i.parking_name) for i in all_blue]
        for lat,long,name,status,nameth in station_list:
            station_dict = {}
            if station_dict =={}:
                station_dict['name'] = name
                station_dict['nameth'] = nameth
                station_dict['ncarrem'] = 'N/A'
                station_dict['color'] = 'box-parking2'
            if status =='inactive':
                station_dict['button'] = 'button'
            else:
                station_dict['button'] = 'submit'
            if station_dict['ncarrem'] == 'N/A':
                    station_dict = retrieveNcarrem(station_dict,data_to_json)
            data.append(station_dict)
        return data

def get_greenline():
    data_to_json = read_carrem_json.copy()
    try:
        res = requests.get(url,timeout=0.5)
        res.encoding = 'utf-8'
        soup = bs(res.text,'html.parser')
        data = []
        all_blue = Parking_manage.query.filter_by(line_name = 'สายสีเขียว').all()
        station_list = [(i.latitude,i.longitude,i.parking_name,i.parking_status) for i in all_blue]
        cups = soup.find_all('table')
        for lat,long,name,status in station_list:
            station_dict = {}
            for cup in cups:
                if cup.find('latitude').text == lat and cup.find('longitude').text == long:
                    station_dict['name'] = name
                    station_dict['color'] = 'box-parking3'
                    ncarrem = cup.find('ncarrem').text
                    station_dict['ncarrem'] = ncarrem if ncarrem == 'N/A' or int(ncarrem) >= 0 else 0
                else:
                    continue
            if station_dict =={}:
                station_dict['name'] = name
                station_dict['ncarrem'] = 'N/A'
                station_dict['color'] = 'box-parking3'
            if status =='inactive':
                station_dict['button'] = 'button'
            else:
                station_dict['button'] = 'submit'
            if station_dict['ncarrem'] == 'N/A':
                    station_dict = retrieveNcarrem(station_dict,data_to_json)
            data.append(station_dict)
        return data
    except:
        data = []
        all_blue = Parking_manage.query.filter_by(line_name = 'สายสีเขียว').all()
        station_list = [(i.latitude,i.longitude,i.parking_name,i.parking_status) for i in all_blue]
        for lat,long,name,status in station_list:
            station_dict = {}
            if station_dict =={}:
                station_dict['name'] = name
                station_dict['ncarrem'] = 'N/A'
                station_dict['color'] = 'box-parking3'
            if status =='inactive':
                station_dict['button'] = 'button'
            else:
                station_dict['button'] = 'submit'
            if station_dict['ncarrem'] == 'N/A':
                    station_dict = retrieveNcarrem(station_dict,data_to_json)
            data.append(station_dict)
        return data

def get_greenline_eng():
    data_to_json = read_carrem_json.copy()
    try:
        res = requests.get(url,timeout=0.5)
        res.encoding = 'utf-8'
        soup = bs(res.text,'html.parser')
        data = []
        all_blue = Parking_manage.query.filter_by(line_name = 'สายสีเขียว').all()
        station_list = [(i.latitude,i.longitude,i.parking_name_eng,i.parking_status,i.parking_name) for i in all_blue]
        cups = soup.find_all('table')
        for lat,long,name,status,nameth in station_list:
            station_dict = {}
            for cup in cups:
                if cup.find('latitude').text == lat and cup.find('longitude').text == long:
                    station_dict['name'] = name
                    station_dict['nameth'] = nameth
                    station_dict['color'] = 'box-parking3'
                    ncarrem = cup.find('ncarrem').text
                    station_dict['ncarrem'] = ncarrem if ncarrem == 'N/A' or int(ncarrem) >= 0 else 0
                else:
                    continue
            if station_dict =={}:
                station_dict['name'] = name
                station_dict['nameth'] = nameth
                station_dict['ncarrem'] = 'N/A'
                station_dict['color'] = 'box-parking3'
            if status =='inactive':
                station_dict['button'] = 'button'
            else:
                station_dict['button'] = 'submit'
            if station_dict['ncarrem'] == 'N/A':
                    station_dict = retrieveNcarrem(station_dict,data_to_json)
            data.append(station_dict)
        return data
    except:
        data = []
        all_blue = Parking_manage.query.filter_by(line_name = 'สายสีเขียว').all()
        station_list = [(i.latitude,i.longitude,i.parking_name_eng,i.parking_status,i.parking_name) for i in all_blue]
        for lat,long,name,status,nameth in station_list:
            station_dict = {}
            if station_dict =={}:
                station_dict['name'] = name
                station_dict['nameth'] = nameth
                station_dict['ncarrem'] = 'N/A'
                station_dict['color'] = 'box-parking3'
            if status =='inactive':
                station_dict['button'] = 'button'
            else:
                station_dict['button'] = 'submit'
            if station_dict['ncarrem'] == 'N/A':
                    station_dict = retrieveNcarrem(station_dict,data_to_json)
            data.append(station_dict)
        return data

def find_availability(station_name):
    data_to_json = read_carrem_json.copy()
    try:
        res = requests.get(url,timeout=0.5)
        res.encoding = 'utf-8'
        soup = bs(res.text,'html.parser')
        station = Parking_manage.query.filter_by(parking_name=station_name).first()
        for i in soup.find_all('table'):
            if station_name == 'สถานีหลักสอง':
                    n = 0
                    for cup in soup.find_all('table'):
                        if cup.find('latitude').text == station.latitude and cup.find('longitude').text == station.longitude:
                            scrapping_text = cup.find('ncarrem').text
                            if scrapping_text.isnumeric():
                                n += int(cup.find('ncarrem').text)
                    ncarrem = str(n)
            elif i.find('latitude').text == station.latitude and i.find('longitude').text == station.longitude:
                scrapping_text = i.find('ncarrem').text
                ncarrem = scrapping_text if scrapping_text == 'N/A' or int(scrapping_text) >= 0 else 0
                break
            else:
                ncarrem = 'N/A'
        if station.parking_visitor_status == 'inactive':
            return {'ncarrem':'N/A','date':datetime.today().strftime('%Y/%m/%d %H:%M:%S')}
        if ncarrem == 'N/A':
            station_dict = {'name':station_name,'ncarrem':'N/A','date':datetime.today().strftime('%Y/%m/%d %H:%M:%S')}
            station_dict = retrieveNcarrem(station_dict,data_to_json)
            return station_dict
        else:
            return {'ncarrem':ncarrem,'date':datetime.today().strftime('%Y/%m/%d %H:%M:%S')}
    except:
        station_dict = {'name':station_name,'ncarrem':'N/A','date':datetime.today().strftime('%Y/%m/%d %H:%M:%S')}
        station_dict = retrieveNcarrem(station_dict,data_to_json)
        return station_dict