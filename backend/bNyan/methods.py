import os 
import hashlib
import asyncio
from urllib.error import HTTPError

from urllib.request import Request
from fastapi.responses import FileResponse
from fastapi import Response, UploadFile, HTTPException

from . import reg
from . import constants_ 
from . import exceptions
from . import util
from . import database
from . import models 
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


async def get_valid_file_header(data : UploadFile, data_length : int):
    """ 
    Gets the header from the file, returns a tuple with a bool signaling if the header is valid, the valid header, and the bytes read from the file
    
    This function expects the file position to be at 0 and this function doesn't reset the position to 0 after reading.

    Returns (bool, valid_header, read_bytes)
    """

    length = min(constants_.file_headers.LONGEST_FILE_HEADER_LENGTH, data_length)
    header = await data.read(length)

    # search through valid byte headers (this is sorted from smallest -> greatest)
    for valid_header in constants_.file_headers.ALL_FILE_HEADERS:

        if header.startswith(valid_header):
            return (True, valid_header, header)
            
    return (False, b"", header)


def get_static_path_from_mime(mime : int):
    """ returns the static path where a file should be stored based of the given mime type """
    
    if mime in constants_.mime_types.IMAGE_MIMES:
        return constants_.STATIC_IMAGE_PATH

    if mime in constants_.mime_types.VIDEO_MIMES:
        return constants_.STATIC_VIDEO_PATH

    if mime in  constants_.mime_types.AUDIO_MIMES:
        return constants_.STATIC_VIDEO_PATH

    return constants_.STATIC_TEMP_PATH



# returns a FileReponse object
def get_image(image_name : str, request : Request):
    """ returns a FileResponse with the requested image """
    image_name = file_check(image_name, constants_.STATIC_IMAGE_PATH)

    return FileResponse(image_name)


def stream_video(video_name : str, request : Request):
    """ returns a partial response with bytes from the request video file """

    if request is None:
        raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    # file name check
    video_name = file_check(video_name, constants_.STATIC_VIDEO_PATH)

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
        return Response(data, status_code=constants_.status_codes.PARTIAL_RESPONSE, headers=headers)


def get_video(video_name : str, request : Request):
    """ Returns a full video with a 200 request, this is used to transer .ts video files for hls"""

    # file name check
    video_name = file_check(video_name, constants_.STATIC_VIDEO_PATH, [reg.INVALID_PATH_WITHOUT_SEP.sub]) # allow / and \ in the path name
    
    total_response_size = os.stat(video_name).st_size

    with open(video_name, "rb") as reader:

        data = reader.read(total_response_size)

        headers={
            "Accept-Ranges" : "bytes",
            "Content-Range" : f"bytes {0}-{total_response_size}/{total_response_size}",
            "Content-Type"  : "video/ts"
        }
        return Response(data, status_code=constants_.status_codes.RESPONSE, headers=headers) 


def get_m3u8(file : str, request : Request):
    
    file = file_check(file, constants_.STATIC_M3U8_PATH)

    return FileResponse(file, status_code=constants_.status_codes.RESPONSE)


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


async def process_file_upload(file : UploadFile, data_length : int):

    # check for valid header, get the valid header, and get the read bytes
    valid, header, read_bytes = await get_valid_file_header(file, data_length)

    if not valid:
        raise exceptions.API_400_BAD_FILE_EXCEPTION

    # get a temp file 
    tempname = util.get_temp_file_in_path(constants_.STATIC_TEMP_PATH)

    # make use of the valid header, get the mime type and file extension
    mime     = constants_.header_mime_lookup.get(header, constants_.mime_types.UNKNOWN)
    file_ext = constants_.mime_ext_lookup.get(mime)

    # begin our sha256 hash, this will be made as we download the file
    h_sha256 = hashlib.sha256()
    h_sha256.update(read_bytes)

    with open(tempname, "wb") as writer:
        
        # make sure to write the bytes read getting the header
        writer.write(read_bytes)

        # download the file in chunks 
        async for chunk in util.iter_file_async(file):

            h_sha256.update(chunk)

            writer.write(chunk)

    # get our sha256 hash
    sha256 = h_sha256.digest()
    file_size = os.path.getsize(tempname)

    # generate a file model to add the file into the database 
    db_file = models.File(
        hash=sha256, 
        size=file_size, 
        mime=mime, 
        width=0, 
        height=0, 
        duration=0, 
        num_words=0, 
        has_audio=False)

    try:
        # will throw an exception if the file is in the database 
        database.Methods.add_file(db_file)
    except HTTPException as e:
        util.remove_file(tempname) # delete the temp file 
        raise e 

    # get the new filename 
    filename = os.path.join(get_static_path_from_mime(mime), sha256.hex() + file_ext)

    # rename the file
    if not util.rename_file(tempname, filename):
        print("=" * 64)
        print("   SHA256:", sha256)
        print("     File: ", filename)
        print("Temp File: ", tempname)
        print("Could not rename from temp path to given path, reason unknown")
        print("=" * 64)
    



CATEGORY_MAP = {
    "i" : get_image,
    "v" : stream_video,
    "m3u8" : get_m3u8
}

