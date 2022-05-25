import os 
from re import compile
from fastapi.responses import Response
VIDEO_STREAM_CHUNK_SIZE = 1024 * 1024
RANGE_HEADER = compile(r"bytes=(?P<min>[0-9]+)\-(?P<max>[0-9]+)?")

class Request():

    def __init__(self) -> None:
        self.headers = {}
        self.method = "get"


def size(bytes, size_unit):
    """
    size units:
    0 : bytes
    1 : kilobytes
    2 : megabytes
    3 : gigabytes
    ...
    """
    return bytes / (1 << (size_unit * 10))


def _stream_video(video_name : str, request ):
    """ returns a partial response with bytes from the request video file """

    if request is None:
        raise Exception('400 bad request')
        # raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    # video_name = get_clean_name_or_die(video_name, constants_.STATIC_VIDEO_PATH)


    # get start byte range from header, default to 0 
    _range = RANGE_HEADER.search(request.headers.get("range", "bytes=0-"))

    if not _range: # doesn't match regex, bad header request 
        raise Exception('400 bad request')
        # raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    file_size = os.stat(video_name).st_size

    seek_to = int(_range.group('min'))
    read_to = min(int(_range.group('max') or seek_to + VIDEO_STREAM_CHUNK_SIZE), file_size)

    bytes_to_read = read_to - seek_to

    if bytes_to_read < 0:
        raise Exception('400 bad request')

    
    headers={
            "Accept-Ranges" : "bytes",
            "Content-Range" : f"bytes {seek_to}-{read_to}/{file_size}",
            "Content-Type"  : "video/mp4"
        }

    if request.method == "HEAD":
        return headers 

    with open(video_name, "rb") as reader:

        reader.seek(seek_to)

        data = reader.read(bytes_to_read)
        
        return Response(data, status_code=206, headers=headers)


req = Request()
req.headers['range'] = 'bytes=999-20000'

print(_stream_video("blankfile", req).headers)


import math 


print(math.log(1048576, 1024))

