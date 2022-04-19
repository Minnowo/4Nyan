import os 

from urllib.request import Request
from fastapi.responses import FileResponse
from fastapi import Response

from . import reg
from . import status_codes
from . import constants_
from . import exceptions
from . import util
from . import database
# from .database.tables_postgres import *

CHUNK_SIZE         = 1024 * 1024    # 1mb 
BYTES_PER_RESPONSE = CHUNK_SIZE * 8 # ~8mb


def file_check(path : str, rout : str, cleans=[reg.INVALID_PATH_CHAR.sub]):
    """ checks if the given file exists in the given rout and cleans the path with the list of given regex.sub """
    
    l = len(path)
    
    # length check
    if (l < constants_.MIN_IMG_PATH_LENGTH):
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    if (l > constants_.MAX_IMG_PATH_LENGTH):
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    for i in cleans:
        path = i("", path)

    path = os.path.join(rout, path)

    if not os.path.isfile(path):
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    return path 



# returns a FileReponse object
def get_image(image_name : str, request : Request):
    """ returns a FileResponse with the requested image """
    image_name = file_check(image_name, "static\\i\\")

    return FileResponse(image_name)



def stream_video(video_name : str, request : Request):
    """ returns a partial response with bytes from the request video file """

    if request is None:
        raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    # file name check
    video_name = file_check(video_name, "static\\v\\")

    total_response_size = os.stat(video_name).st_size

    # get start byte range from header, default to 0 
    _range = reg.RANGE_HEADER.search(
                                request.headers.get("range", "bytes=0-"))

    if not _range: # doesn't match regex, bad header request 
        raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    start_byte_requested = int(_range.group(1))
    end_byte_planned     = min(start_byte_requested + BYTES_PER_RESPONSE, total_response_size)

    with open(video_name, "rb") as reader:

        reader.seek(start_byte_requested)

        data = reader.read(end_byte_planned)

        headers={
            "Accept-Ranges" : "bytes",
            "Content-Range" : f"bytes {start_byte_requested}-{end_byte_planned}/{total_response_size}",
            "Content-Type"  : "video/mp4"
        }
        return Response(data, status_code=status_codes.PARTIAL_RESPONSE, headers=headers)


def get_video(video_name : str, request : Request):
    """ Returns a full video with a 200 request, this is used to transer .ts video files for hls"""

    # file name check
    video_name = file_check(video_name, "static\\v\\", [reg.INVALID_PATH_WITHOUT_SEP.sub]) # allow / and \ in the path name
    
    total_response_size = os.stat(video_name).st_size

    with open(video_name, "rb") as reader:

        data = reader.read(total_response_size)

        headers={
            "Accept-Ranges" : "bytes",
            "Content-Range" : f"bytes {0}-{total_response_size}/{total_response_size}",
            "Content-Type"  : "video/ts"
        }
        return Response(data, status_code=status_codes.RESPONSE, headers=headers) 


def get_m3u8(file : str, request : Request):
    
    file = file_check(file, "static\\m3u8\\")

    return FileResponse(file, status_code=status_codes.RESPONSE)




def static_lookup(file_hash : str):
    
    # ensure only hexadeciaml is given 
    file_hash = reg.IS_HEXADECIMAL.match(file_hash)

    if not file_hash:
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    # get the match 
    hexadecimal = file_hash.group(1)

    # convert into bytes 
    digest = bytes.fromhex(hexadecimal)

    # look for the file record in the database 
    file = database.methods.get_file_by_hash(digest)

    # return the file information 
    file_info_json = file.dict()
    file_info_json["filename"] = hexadecimal + constants_.mime_ext_lookup.get(file.mime, "")

    return file_info_json


CATEGORY_MAP = {
    "i" : get_image,
    "v" : stream_video,
    "m3u8" : get_m3u8
}

