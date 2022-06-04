
import requests
import os 
import json 
from .logging_ import get_logger

IP   = "localhost"
PORT = "721"
HOST = "http://{}:{}/".format(IP, PORT)

API_ENDPOINTS = {
    'file_upload' : HOST + "create/file",
    'create_tag'  : HOST + "create/tag",
    'tag_file'    : HOST + "create/map",

}

__LOGGER = get_logger('uNyan __init__')


def upload_file(path):

    if not os.path.isfile(path):
        __LOGGER.warning("File {} does not exist".format(path))
        return False

    headers = {
        "accept" : "applications/json",
    }

    payload = {
        'data' : open(path, 'rb')
    }

    try:

        response = requests.post(API_ENDPOINTS['file_upload'], files=payload, headers=headers)
    
    except Exception as e:
        
        __LOGGER.error(e, stack_info=True)
        return False

    return response.status_code == 200



def create_tag(tag):

    headers = {
        'content-type' : 'application/json'
    }
    
    try:

        response = requests.post(API_ENDPOINTS['create_tag'], json=tag, headers=headers)
    
    except Exception as e:
        
        __LOGGER.error(e, stack_info=True)
        return {}

    try:

        return response.json()

    except json.JSONDecodeError:

        return {}

    except Exception as e:

        __LOGGER.error(e, stack_info=True)
        return {}
  


def tag_file(file_id, tag_id):

    headers = {
        'content-type' : 'application/json'
    }

    data = {
        'file_id' : file_id,
        'tag_id'  : tag_id 
    }

    try:

        response = requests.post(API_ENDPOINTS['tag_file'], json=data, headers=headers)
    
    except Exception as e:
        
        __LOGGER.error(e, stack_info=True)
        return False

    return response.status_code == 200