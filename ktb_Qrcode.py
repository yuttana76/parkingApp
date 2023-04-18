import libscrc


def text_qr(money,ref1,ref2):
    Version = "0002"+"01"
    one_time="010212" # 12 ใช้ครั้งเดียว Dynamic Qr payment 
    # (11) แบบ Static : QR Code จะไม่เปล
    # เปลี่ยนแปลง ร้านค้าสามารถพิมพ์
    # และติดไว้ที่ร้านค้าได้ตลอด จนกว่าข้อมูลการชำระเงินจะเปลี่ยนไป
    # โดยลูกค้าเป็นผู้ใส่จำนวนเงินเอง
    # (12) แบบ Dynamic : QR Code จะเปลี่ยนในทุกรายการ เช่น การระบุ
    # ราคาสินค้าในแต่ละรายการ โดยลูกค้าไม่ต้องใส่จำนวนเงิน กรณีนี้
    # QR Code จะถูกสร้างขึ้นจาก mobile application ของร้านค้าในแต่
    # ละรายการ
  
    merchant_account_information="3078" # ข้อมูลผู้ขาย
    merchant_account_information+="0016"+"A000000677010112" # ภายในประเทศ
    #******************************************************************************************************
    merchant_account_information+="0115"+"0994000165706"+"11" #Biller ID tax_id = 0994000165706 suffix = 11  
    #******************************************************************************************************
    merchant_account_information+="0213" + ref1 #Ref1
    merchant_account_information+="0318" + ref2 #Ref2
    
    
    currency ="5303"+"764" # "764"  คือเงินบาทไทย
    country="5802TH"
    if money!="": # กรณีกำหนดเงิน
        check_money=money.split('.') # แยกจาก .
        if len(check_money)==1 or len(check_money[1])==1: # กรณีที่ไม่มี . หรือ มีทศนิยมแค่หลักเดียว
            money="54"+"0"+str(len(str(float(money)))+1)+str(float(money))+"0"
        else:
            money="54"+"0"+str(len(str(money)))+str(money) # กรณีที่มีทศนิยมครบ
          

    check_sum=Version+one_time+merchant_account_information+currency+money+country+"6304" 
    check_sum1=hex(libscrc.ccitt_aug(check_sum.encode("ascii"),0xFFFF)).replace('0x','')
    print(check_sum1)
    if len(check_sum1)<4: # # แก้ไขข้อมูล check_sum ไม่ครบ 4 หลัก
        print('?')
        check_sum1=("0"*(4-len(check_sum1)))+check_sum1
    check_sum+=check_sum1
    print(check_sum.upper())
    print("*******************************************************")
    return check_sum.upper() # upper ใช้คืนค่าสตริงเป็นตัวพิมพ์ใหญ่






