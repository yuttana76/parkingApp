from smartparking.payment.domain.base.aggregate import AggregateBase
from smartparking.parking.domain.registry import Registry
from datetime import datetime
import libscrc


class Transaction(AggregateBase):
    
    def save_to_database(self):
        Registry().paymentlog.create_new_transaction(self)
        
    def if_latest_transaction_from_owner_not_success(self):
        return Registry().paymentlog.get_owner_latest_transaction_status(self.owner)
        
    def get_owner_latest_transaction(self) :
        return Registry().paymentlog.from_owner(self.owner)
    
    def add_ordernumber_to_trasaction(self):
        orderNumber = 'DLY' + self.parking_code + str(self.Id).zfill(10)
        self.orderNumber = orderNumber
        
    def add_termseq_to_transaction(self):
        now = datetime.today()
        date = now.date()
        today = now.strftime('%Y''%m''%d''%H''%M')
        number_of_transaction_from_this_day = Registry().paymentlog.get_number_of_transaction_today(date)
        term_seq = today + str(number_of_transaction_from_this_day)
        self.term_seq = term_seq
        
    def update(self):
        Registry().paymentlog.update_from_object(self)
        
    def update_service_charge(self,newtransaction:AggregateBase):
        self.amount = newtransaction.amount
        self.fine = newtransaction.fine
        self.total = newtransaction.total
        self.vat = newtransaction.vat  
        
    def get_prompt_qrcode(self):
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
        merchant_account_information+="0213" + '0994000165706' #Ref1
        merchant_account_information+="0318" + self.orderNumber #Ref2
        
        
        currency ="5303"+"764" # "764"  คือเงินบาทไทย
        country="5802TH"
        if self.total : # กรณีกำหนดเงิน
            money = str(self.total)
            check_money=money.split('.') # แยกจาก .
            if len(check_money)==1 or len(check_money[1])==1: # กรณีที่ไม่มี . หรือ มีทศนิยมแค่หลักเดียว
                money="54"+"0"+str(len(str(float(money)))+1)+str(float(money))+"0"
            else:
                money="54"+"0"+str(len(str(money)))+str(money) # กรณีที่มีทศนิยมครบ
            

        check_sum=Version+one_time+merchant_account_information+currency+money+country+"6304" 
        check_sum1=hex(libscrc.ccitt_aug(check_sum.encode("ascii"),0xFFFF)).replace('0x','')
        if len(check_sum1)<4: # # แก้ไขข้อมูล check_sum ไม่ครบ 4 หลัก
            check_sum1=("0"*(4-len(check_sum1)))+check_sum1
        check_sum+=check_sum1
        
        return check_sum.upper()
    
    #cash
    def paid_with_cash(self):
        self.payment_status = '1'
        self.payment_name = '1'
        self.payment_date = datetime.today()
    
    def paid_with_edc(self):
        self.payment_status = '1'
        self.payment_name = '2'
        self.payment_date = datetime.today()
        
    def get_invoice_no(self):
        invoice = self.parking_code + datetime.today().strftime('%d%m%Y') + Registry().paymentlog.get_number_of_success_transaction_in_this_day(self.parking_code)
        self.invoice_no = invoice
        return invoice
    
    def from_ordernumber(self,ordernumber:str) -> AggregateBase:
        transaction = Registry().paymentlog.from_ordernumber(ordernumber)
        return transaction