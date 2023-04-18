import os
from app import app
import datetime
from werkzeug.utils import secure_filename

def custom_file(file,card_id,filename):
    if file == None:
        file = ''
        return file
    elif file.filename == '':
        file = ''
        return file
    elif file.filename != '':
        list_file = os.listdir(r'{}'.format(app.config['UPLOAD_FOLDER']))
        date = str(datetime.datetime.today()).split(' ')[0]
        filetype = file.filename.split('.')[1]
        #check duplicated file
        path = os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f'{filename}_{date}-no_{card_id}.{filetype}'))
        for name in list_file:
            if name.startswith(f'{filename}_{date}-no_{card_id}'):
                    os.remove(r'{}\{}'.format(app.config['UPLOAD_FOLDER'],name))
        #save file and rename
        file.save(path)
        file = f'{filename}_{date}-no_{card_id}.{filetype}'
        return file
