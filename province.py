import json
import os

with open(r"{}".format(os.environ.get('PROVINCE_FILE',r'C:\D\project_mrta_parkingApp\mrta-app\ProvinceTH.json')), encoding="utf-8") as json_data:
            data = json.load(json_data)

def get_province():
    province = ['']
    for i in data:
        if i['province'] not in province:
            province.append(i['province'])
        else:
            continue
    return province

def get_district(province_):
    district = [{'name':''}]
    dup =[]
    if province_ != '':
        for i in data:
            d = {}
            if i['province'] == province_ and i['district'] not in dup :
                d['name'] =i['district']
                district.append(d)
                dup.append(i['district'])
            else:
                continue
    
    return district

def get_subdistrict(province_,district_):
    subdistrict =['']
    for i in data:
        if i['province'] == province_ and i['district'] == district_ :
            subdistrict.append(i['subdistrict'])
    return list(dict.fromkeys(subdistrict))

def get_postcode(province_,district_,subdistrict_):
    postcode =['']
    for i in data:
        if i['province']==province_ and i['district'] == district_ and i['subdistrict'] == subdistrict_ :
            postcode.append(i['postcode'])
    return list(dict.fromkeys(postcode))