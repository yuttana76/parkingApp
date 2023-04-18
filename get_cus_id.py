from app import Parking_member

def generate_cus_id():
    member = Parking_member.query.filter(Parking_member.Id >= 0).all()
    cus_list = []
    for i in member:
        if i.cus_id:
            if int(i.cus_id.split('c')[1]) not in cus_list :
                cus_list.append(int(i.cus_id.split('c')[1]))
            else:
                continue
        else:
            continue
    return 'c' +'{:09}'.format(int(max(cus_list))+1)