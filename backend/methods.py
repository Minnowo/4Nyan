from urllib.request import Request
import exceptions
import constants 
import os 
import reg
from fastapi.responses import FileResponse, StreamingResponse
from fastapi import Response

CHUNK_SIZE         = 1024 * 1024    # 1mb 
BYTES_PER_RESPONSE = CHUNK_SIZE * 8 # ~8mb


def file_check(path : str, rout : str):

    l = len(path)

    # length check
    if (l < constants.MIN_IMG_PATH_LENGTH):
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    if (l > constants.MAX_IMG_PATH_LENGTH):
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    path = os.path.join(rout, reg.INVALID_PATH_CHAR.sub("", path))

    if not os.path.isfile(path):
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



#  https://github.com/tiangolo/fastapi/issues/1240
def get_video(video_name : str, request : Request):

    if request is None:
        raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    # file name check
    video_name = file_check(video_name, "static\\v\\")

    stream = open(video_name, "rb")

    total_response_size = os.stat(video_name).st_size

    # get start byte range from header, default to 0 
    _range = reg.RANGE_HEADER.search(
                                request.headers.get("Range", "bytes=0-"))

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
            "Content-Type": "video/mp4"
        },
        status_code=206
    )

CATEGORY_MAP = {
    "i" : get_image,
    "v" : get_video
}
