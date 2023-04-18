import libscrc
#stationCode:รหัสสถานี
def newMember(stationCode,id) :
    zero_filled_number = str(id).zfill(10) #Run number มี 10 ตำแหน่ง 0000000001
    ref2 = "NMB"+stationCode+zero_filled_number
    # print(ref2)

    return ref2
def reMember(stationCode,id) :
    zero_filled_number = str(id).zfill(10)
    ref2 = "REM"+stationCode+zero_filled_number
    # print(ref2)

    return ref2

def genRef2(a,id_,station):
    
    if a == 0:
       return newMember(station,id_)
    else:
       return reMember(station,id_)


