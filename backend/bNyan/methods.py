import exceptions
import constants 
import os 
import reg
import status_codes

from urllib.request import Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi import Response

CHUNK_SIZE         = 1024 * 1024    # 1mb 
BYTES_PER_RESPONSE = CHUNK_SIZE * 8 # ~8mb


def file_check(path : str, rout : str, cleans=[reg.INVALID_PATH_CHAR.sub]):

    l = len(path)

    # length check
    if (l < constants.MIN_IMG_PATH_LENGTH):
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    if (l > constants.MAX_IMG_PATH_LENGTH):
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    for i in cleans:
        path = i("", path)

    path = os.path.join(rout, path)

    if not os.path.isfile(path):
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    return path 

def folder_check(path : str, rout : str, cleans=[reg.INVALID_PATH_CHAR.sub]):

    l = len(path)

    # length check
    if (l < constants.MIN_IMG_PATH_LENGTH):
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    if (l > constants.MAX_IMG_PATH_LENGTH):
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    for i in cleans:
        path = i("", path)

    path = os.path.join(rout, path)

    if not os.path.isdir(path):
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    return path 

def iter_file(stream, chunk_size, start, size):
    bytes_read = 0

    stream.seek(start)

    while bytes_read < size:
        bytes_to_read = min(chunk_size, size - bytes_read)

        yield stream.read(bytes_to_read)
        
        bytes_read = bytes_read + bytes_to_read

    stream.close()


# returns a FileReponse object
def get_image(image_name : str, request : Request):

    image_name = file_check(image_name, "static\\i\\")

    return FileResponse(image_name)

# https://stribny.name/blog/2020/07/real-time-data-streaming-using-fastapi-and-websockets/
#  https://github.com/tiangolo/fastapi/issues/1240
def DEPRICATED_get_video_1(video_name : str, request : Request):

    if request is None:
        raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    # file name check
    video_name = file_check(video_name, "static\\v\\")

    stream = open(video_name, "rb")

    total_response_size = os.stat(video_name).st_size

    # get start byte range from header, default to 0 
    _range = reg.RANGE_HEADER.search(
                                request.headers.get("range", "bytes=0-"))

    if not _range: # doesn't match regex, bad header request 
        raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    start_byte_requested = int(_range.group(1))
    end_byte_planned     = min(start_byte_requested + BYTES_PER_RESPONSE, total_response_size)

    chunk_generator = iter_file(
                                stream,    
                                chunk_size=CHUNK_SIZE,
                                start=start_byte_requested,
                                size=BYTES_PER_RESPONSE
                            )
    
    return StreamingResponse(
        chunk_generator,
        headers={
            "Accept-Ranges": "bytes",
            "Content-Range": f"bytes {start_byte_requested}-{end_byte_planned}/{total_response_size}",
            "Content-Type": "video/mkv"
        },
        status_code=206
    )


def stream_video(video_name : str, request : Request):
    
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
    """ Returns a full video with a 200 request, this is used for the m3u8 files to have a direct link """

    # file name check
    video_name = file_check(video_name, "static\\v\\", [reg.INVALID_PATH_WITHOUT_SEP.sub])
    
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

    headers = {
        # "Content-Type" : "application/x-mpegURL"
        }

    return FileResponse(file, status_code=status_codes.RESPONSE, headers=headers)


CATEGORY_MAP = {
    "i" : get_image,
    "v" : stream_video,
    "m3u8" : get_m3u8
}

