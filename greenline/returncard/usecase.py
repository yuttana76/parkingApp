from greenline.returncard.model import Card_return,Dataerror,InvalidStationCode
import requests 

def send_card_return_data_to_cit(stationCode,token_id,memberCardName):
    try:
        cardreturn = Card_return(
            stationCode = stationCode,
            token_id = token_id,
            memberCardName = memberCardName
        )
        status = cardreturn.send_message(requests=requests)
        return status
    except InvalidStationCode:
        return 'Invalid station code' 
    except Dataerror as e:
        return e.message
    except Exception as e:
        return False