import math
def number_format(num, places=0):
    return '{:20,.2f}'.format(num)

def ThaiBahtConversion(amount_number):
    amount_number = number_format(amount_number, 2).replace(" ","")
    pt = amount_number.find(".")
    number,fraction = "",""
    amount_number1 = amount_number.split('.')
    if (pt == False):
        number = amount_number
    else:
        amount_number = amount_number.split('.')
        number = amount_number[0]
        fraction = int(amount_number1[1]) 
    ret = ""
    number=eval(number.replace(",",""))
    baht = ReadNumber(number)
    if (baht != ""):
        ret += baht + "บาท"
    satang = ReadNumber(fraction)
    if (satang != ""):
        ret += satang + "สตางค์"
    else:
        ret += "ถ้วน"
    return ret
 
def ReadNumber(number):
    position_call = ["แสน", "หมื่น", "พัน", "ร้อย", "สิบ", ""]
    number_call = ["", "หนึ่ง", "สอง", "สาม","สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"]
    number = number
    ret = ""
    if (number == 0): return ret
    if (number > 1000000):
        ret += ReadNumber(int(number / 1000000)) + "ล้าน"
        number = int(math.fmod(number, 1000000))
    divider = 100000
    pos = 0
    while(number > 0):
        d=int(number/divider)
        if (divider == 10) and (d == 2):
            ret += "ยี่"
        elif (divider == 10) and (d == 1):
            ret += ""
        elif ((divider == 1) and (d == 1) and (ret != "")):
            ret += "เอ็ด"
        else:
            ret += number_call[d]
        if(d):
            ret += position_call[pos]
        else:
            ret += ""
        number=number % divider
        divider=divider / 10
        pos += 1
    return ret
 
def change_to_thaitime(date):
    month_list = ['','มกราคม','กุมภาพันธ์','มีนาคม','เมษายน','พฤษภาคม','มิถุนายน','กรกฎาคม','สิงหาคม','กันยายน','ตุลาคม','พฤศจิกายน','ธันวาคม']
    result_date = 'วันที่ '
    result_date += str(int(date.split('-')[0]))+' '
    result_date += month_list[int(date.split('-')[1])]+' '
    result_date += str(int(date.split('-')[2]) + 543)
    return result_date