

import requests
import os 
import json 

with open("..\\..\\backend\\bnyan\\db\\main.json",'r') as reader:

    s = json.load(reader)

    if 'server_ip' not in s:
        raise Exception("need server ip")

    if 'port' not in s:
        raise Exception('need port')

    SI = 'http://{}:{}/'.format(s['server_ip'], s['port'])


def upload_file(path):

    URL = SI + "create/file"

    if not os.path.isfile(path):
        print("file does not exist")
        return 

    headers = {
            "accept" : "applications/json",
            # "content-type" : "multipart/form-data",
            "Content-Disposition": 'attachment; filename="{}"'.format(os.path.basename(path)),
    }

    payload = {
        'data' : open(path, 'rb') #.read()
    }

    response = requests.post(URL, files=payload, headers=headers)

    print(response.headers)
    print(response.encoding)

    print(response.status_code)
    print(response.text)


def create_tag(tag):

    URL = SI + "create/tag"

    headers = {
        'content-type' : 'application/json'
    }

    response = requests.post(URL, json=tag, headers=headers)
    
    print(response.status_code)
    print(response.text)


def create_map(file_id, tag_id):

    URL = SI + "create/map"

    headers = {
        'content-type' : 'application/json'
    }

    data = {
        'file_id' : file_id,
        'tag_id'  : tag_id 
    }

    response = requests.post(URL, json=data, headers=headers)
    
    print(response.status_code)
    print(response.text)

# upload_file("C:\\Users\\minno\\Downloads\\cat.jpg")
# create_tag('category:video')
# create_map(0,6)
# create_map(13, 9)
create_tag("category:pictures")
for i in range(10):
    create_map(i, 10)
