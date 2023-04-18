from pydantic import BaseModel,validator

class Card_lost(BaseModel):
    stationCode:str
    token_id:str 
    memberCardNamOld:str 
    memberCardNamNew:str 
    username:str = 'jpark'
    password:str = "jPark54321"
    
    @validator('stationCode')
    def stationCode_should_be_N1013_or_N1014(cls,value):
        stationcode_transform = {'N1013':'GN23','N1014':'GN24'}
        if value not in list(stationcode_transform.keys()):
            raise InvalidStationCode 
        return stationcode_transform.get(value)
    
    def send_message(self,requests):
        url = 'https://uatparkandride.mrta.co.th/jpark/v1/member/cardlost'
        response = requests.post(data=self.dict(),url=url)
        if response.json().get('error'):
            raise Dataerror(response.json().get('message'))
        return True

        
class InvalidStationCode(Exception):
    pass 

class Dataerror(Exception):
    def __init__(self,message):
        super(Dataerror,self).__init__()
        self.message = message

# card = Card_lost(stationCode='N1013',token_id='a',memberCardNamOld='a',memberCardNamNew='a')
# card.send_message()