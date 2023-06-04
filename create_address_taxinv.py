from PIL import ImageFont
import os

font = ImageFont.truetype(r'{}'.format(os.environ.get('SARABUNFONT_FILE',r'C:\D\project_mrta_parkingApp\mrta-app\static\font\sarabun\Sarabun-Light.ttf')), 14)
def create_address(obj):
    address = ''
    keys = [('address_no',''),('unit_home',''),
            ('village','หมู่ที่ '),('alley','ซ.'),('street','ถ.'),
            ('sub_district','ต.','แขวง'),('district','อ.','เขต'),
            ('province','จ.',''),('postal_code','')]
    for key in keys:
        if getattr(obj,'province') == 'กรุงเทพมหานคร' and key[0] in ['sub_district','district','province']:
            if font.getsize(address.split('<br>')[-1] + key[2] + getattr(obj,key[0]) if getattr(obj,key[0]) not in ['',None,' '] else '')[0]  < 311:
                address += key[2]+ getattr(obj,key[0]) + ' ' if getattr(obj,key[0]) not in ['',None,' '] else ''
            else:
                address +='<br>' + ' '+key[2]+ getattr(obj,key[0]) + ' ' if getattr(obj,key[0]) not in ['',None,' '] else ''
        else:
            if font.getsize(address.split('<br>')[-1] + key[1] +getattr(obj,key[0]) if getattr(obj,key[0]) not in ['',None,' '] else '')[0] < 311:
                address +=key[1]+ getattr(obj,key[0]) + ' ' if getattr(obj,key[0]) not in ['',None,' '] else ''
            else:
                address +='<br>' + ' '+key[1]+ getattr(obj,key[0]) + ' ' if getattr(obj,key[0]) not in ['',None,' '] else ''
    return address

def create_address_company(obj):
    address = ''
    keys = [('company_no',''),('company_unit',''),('company_village','หมู่ที่ '),('company_alley','ซ.'),
            ('company_street','ถ.'),('company_sub_district','ต.','แขวง'),('company_district','อ.','เขต'),
            ('company_province','จ.',''),('company_postal_code','')]
    for key in keys:
        if getattr(obj,'company_province') == 'กรุงเทพมหานคร' and key[0] in ['company_sub_district','company_district','company_province']:
            if font.getsize(address.split('<br>')[-1] + key[2] + getattr(obj,key[0]) if getattr(obj,key[0]) not in ['',None,' '] else '')[0]  < 311:
                address += key[2]+ getattr(obj,key[0]) + ' ' if getattr(obj,key[0]) not in ['',None,' '] else ''
            else:
                address +='<br>' + ' '+key[2]+ getattr(obj,key[0]) + ' ' if getattr(obj,key[0]) not in ['',None,' '] else ''
        else:
            if font.getsize(address.split('<br>')[-1] + key[1] +getattr(obj,key[0]) if getattr(obj,key[0]) not in ['',None,' '] else '')[0] < 311:
                address +=key[1]+ getattr(obj,key[0]) + ' ' if getattr(obj,key[0]) not in ['',None,' '] else ''
            else:
                address +='<br>' + ' '+key[1]+ getattr(obj,key[0]) + ' ' if getattr(obj,key[0]) not in ['',None,' '] else ''
    return address

