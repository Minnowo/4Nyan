
import requests
import os 
import json 
import logging
from urllib.parse import urlencode
from re import compile 
from . import logging_
from . import exceptions_


IP   = "127.0.0.1"
PORT = "721"
HOST = "http://{}:{}/".format(IP, PORT)

API_ENDPOINTS = {
    # post requests
    'file_upload' : HOST + "create/file",
    'create_tag'  : HOST + "create/tag",
    'tag_file'    : HOST + "create/map",
    'create_user' : HOST + "create/user",
    'login'       : HOST + "auth/token",
    'delete_file' : HOST + "delete/file",

    # get requests
    'heartbeat'      : HOST + "heartbeat",
    'get_file_tags'  : HOST + "search/get_file_tags",
    'get_categories' : HOST + "search/get_categories",
    'get_files'      : HOST + "search/get_files",
    'static'         : HOST + "static/{category}/{path}",
}

__LOGGER = logging_.get_logger('uNyan __init__', log_level=logging.ERROR)

IS_DIGIT  = compile(r"^([0-9]+)$")
IS_SHA256 = compile(r"^(?:0[xX])?(?P<hex>[a-fA-F0-9]{64})$")



def __post_for_json_response(*args, **kwargs):

    try:

        response = requests.post(*args, **kwargs)
    
    except Exception as e:
        
        __LOGGER.error(e, stack_info=True)

        return {}, -1

    try:

        return response.json(), response.status_code

    except json.JSONDecodeError:

        return {}, response.status_code

    except Exception as e:

        __LOGGER.error(e, stack_info=True)

        return {}, response.status_code



def __post_for_empty_response(*args, **kwargs):

    try:

        response = requests.post(*args, **kwargs)
    
    except Exception as e:
        
        __LOGGER.error(e, stack_info=True)

        return -1

    return response.status_code



def __get_for_json_response(*args, **kwargs):

    try:

        response = requests.get(*args, **kwargs)
    
    except Exception as e:
        
        __LOGGER.error(e, stack_info=True)

        return {}, -1

    try:

        return response.json(), response.status_code

    except json.JSONDecodeError:

        return {}, response.status_code

    except Exception as e:

        __LOGGER.error(e, stack_info=True)

        return {}, response.status_code


def delete_files(file_id_and_sha256 : list, headers : dict = None):
    
    _headers = {
        'conotent-type' : 'application/json'
    }

    if headers:
        _headers.update(headers)

    return __post_for_empty_response(API_ENDPOINTS['delete_file'], json=file_id_and_sha256, headers=_headers)

def get_files():

    _headers = {
        "accept" : "applications/json",
    }

    return __get_for_json_response(API_ENDPOINTS['get_files'], headers=_headers)

def get_file_tags(file_id_and_sha256 : list, headers : dict = None):
    
    if not file_id_and_sha256:
        raise exceptions_.Empty_Query_Error("file_id_and_sha256 list is empty or null")

    file_ids  = urlencode({ 'fid' : set(filter(lambda x : IS_DIGIT.match(str(x)) , file_id_and_sha256)) }, doseq=True)
    file_hash = urlencode({ 'fh'  : set(filter(lambda x : IS_SHA256.match(str(x)), file_id_and_sha256)) }, doseq=True)
    
    url = API_ENDPOINTS['get_file_tags'] + "?"

    if file_ids and file_hash:

        url += file_ids + "&" + file_hash

    elif file_ids:

        url += file_ids

    elif file_hash:

        url += file_hash

    else:

        raise exceptions_.Empty_Query_Error("file_id_and_sha256 list did not contain any numbers or sha256 hash")

    return __get_for_json_response(url, headers=headers)

def heartbeat(headers : dict = None):

    return __get_for_json_response(API_ENDPOINTS['heartbeat'], headers=headers)


def upload_file(path, headers : dict = None):
    """
    Sends a file upload request and returns the status code of the response, 200 means the file was accepted
    """

    _headers = {
        "accept" : "applications/json",
    }

    payload = {
        'data' : open(path, 'rb')
    }

    if headers:
        _headers.update(headers)

    return __post_for_empty_response(API_ENDPOINTS['file_upload'], files=payload, headers=_headers)



def create_tag(tag : str, headers : dict = None):
    """
    Sends a create tag request and returns the json response and status code, this endpoint returns the tag even if it already exists
    """

    _headers = {
        'content-type' : 'application/json'
    }

    if headers:
        _headers.update(headers)

    return __post_for_json_response(API_ENDPOINTS['create_tag'], json=tag, headers=_headers)
    


def tag_file(file_id : int, tag_id : int, headers : dict = None):
    """
    Sends a tag file request and returns the status code, 200 means the file was tagged
    """

    _headers = {
        'content-type' : 'application/json'
    }

    data = {
        'file_id' : file_id,
        'tag_id'  : tag_id 
    }

    if headers:
        _headers.update(headers)

    return __post_for_empty_response(API_ENDPOINTS['tag_file'], json=data, headers=_headers)


def create_user(username : str, password : str, headers : dict = None):
    """
    Sends a create user request and returns the json response and status code 
    """

    if not username or not password:
        raise exceptions_.Credential_Error("Invalid username or password")

    _headers = {
        'content-type' : 'application/x-www-form-urlencoded'
    }

    data = {
        "username" : str(username),
        "password" : str(password)
    }

    if headers:
        _headers.update(headers)

    return __post_for_json_response(API_ENDPOINTS['create_user'], data=data, headers=_headers)


def login_user(username : str, password : str, headers : dict = None):
    """
    Sends a login request and returns the json response and status code
    """

    if not username or not password:
        raise exceptions_.Credential_Error("Invalid username or password")

    _headers = {
        'content-type' : 'application/x-www-form-urlencoded'
    }

    data = {
        "username" : str(username),
        "password" : str(password)
    }

    if headers:
        _headers.update(headers)
    
    return __post_for_json_response(API_ENDPOINTS['login'], data=data, headers=_headers)
