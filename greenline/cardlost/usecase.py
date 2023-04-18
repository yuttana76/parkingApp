from greenline.cardlost.model import Card_lost, Dataerror, InvalidStationCode
import requests 

def send_card_lost_data_to_cit(stationCode,token_id,memberCardNamOld,memberCardNamNew,requests=requests):
    try:
        cardlost = Card_lost(
            stationCode = stationCode,
            token_id = token_id,
            memberCardNamNew = memberCardNamNew,
            memberCardNamOld = memberCardNamOld
        )
        status = cardlost.send_message(requests=requests)
        return status
    except InvalidStationCode:
        return 'Invalid station code' 
    except Dataerror as e:
        return e.message
    except Exception as e:
        return False