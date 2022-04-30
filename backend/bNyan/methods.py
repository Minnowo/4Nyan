import os 
import hashlib

from fastapi.responses import FileResponse
from fastapi import Response, UploadFile, HTTPException, Request

from .constants_ import mime_types as MT 

from . import file_handling
from . import reg
from . import constants_ 
from . import exceptions
from . import util
from . import database
from . import models 
from . import bn_logging
from . import m3u8

LOGGER = bn_logging.get_logger(constants_.BNYAN_METHODS[0], constants_.BNYAN_METHODS[1])
VIDEO_PROCESS = m3u8.VideoSplitter()

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
    
    if mime in MT.IMAGE_MIMES:
        return constants_.STATIC_IMAGE_PATH

    if mime in MT.VIDEO_MIMES:
        return constants_.STATIC_VIDEO_PATH

    if mime in  MT.AUDIO_MIMES:
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
    end_byte_planned     = min(start_byte_requested + constants_.VIDEO_STREAM_CHUNK_SIZE, total_response_size)

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


async def process_file_upload(file : UploadFile):

    header_bytes = await file.read(256)

    try:
        
        # if the mime is an unknown mp4 or wm, we will need ffmpeg to validate the video
        # if this is the case we have to download the whole file 
        mime = file_handling.get_mime_from_bytes(header_bytes)

    except exceptions.FFMPEGRequiredException:
        
        mime = MT.UNDETERMINED_VIDEO


    if mime == MT.APPLICATION_UNKNOWN:
        raise exceptions.API_400_BAD_FILE_EXCEPTION


    # get a temp file 
    tempname = util.get_temp_file_in_path(constants_.STATIC_TEMP_PATH)

    # begin our sha256 hash, this will be made as we download the file
    h_sha256 = hashlib.sha256()
    h_sha256.update(header_bytes)

    with open(tempname, "wb") as writer:
        
        # make sure to write the bytes read getting the header
        writer.write(header_bytes)

        # download the file in chunks 
        async for chunk in util.iter_file_async(file, chunk_size=constants_.IMAGE_UPLOAD_CHUNK_SIZE):

            h_sha256.update(chunk)

            writer.write(chunk)


    # we need to use ffmpeg to check the video
    if mime == MT.UNDETERMINED_VIDEO:

        mime = file_handling.get_video_mime(tempname)

        if mime == MT.APPLICATION_UNKNOWN:

            LOGGER.warning("unknown video, ffmpeg could not determine video format -> assuming invalid file")

            util.remove_file(tempname)

            raise exceptions.API_400_BAD_FILE_EXCEPTION


    file_ext = constants_.mime_ext_lookup.get(mime, None)

    # i probably just forgot to add the mime to the extension map if this is true 
    if not file_ext:

        LOGGER.warning("could not find a file extension for mime type of '{}'".format(mime))
        
        raise exceptions.API_400_BAD_FILE_EXCEPTION


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
        
        LOGGER.warning("error thrown adding file to the database -> {}".format(e))

        util.remove_file(tempname) # delete the temp file 
        raise e 

    sha256_hex  = sha256.hex()
    static_path = get_static_path_from_mime(mime)
    filename    = os.path.join(static_path, sha256_hex + file_ext)

    # rename the file
    if not util.rename_file(tempname, filename):
        LOGGER.warning("Cannot rename file '{0}' -> '{1}' hash '{2}' assuming file exists".format(tempname, filename, sha256_hex))
    
    print(filename)

    if static_path != constants_.STATIC_VIDEO_PATH:
        return

    ts_folder = os.path.join(static_path, sha256_hex)

    if not util.create_directory(ts_folder):
        LOGGER.warning("Cannot create ts folder '{0}' for video file '{1}'".format(ts_folder, filename))

        # util.remove_file(tempname)
        raise exceptions.API_500_OSERROR


    try:
        LOGGER.info("Processing video: {}".format(filename))
        VIDEO_PROCESS.split_video(filename, ts_folder, constants_.TS_FILE_DURATION)

    except m3u8.exceptions.FFMPEG_Exception as e:
        
        LOGGER.error(e)

        database.Methods.remove_file(sha256)
        
        raise exceptions.API_400_BAD_FILE_EXCEPTION
        

    LOGGER.info("Generating m3u8")

    # TODO: change the 0.0.0.0 into server ip 
    LOGGER.warning("TODO: change the 0.0.0.0 into server ip -> methods.py line 303")
    m = m3u8.PlaylistGenerator.generate_from_directory("http://0.0.0.0/static/v/" + sha256_hex + "?ts=", ts_folder, constants_.TS_FILE_DURATION)
    
    m3u8_file =  os.path.join(constants_.STATIC_M3U8_PATH, sha256_hex + ".m3u8")

    with open(m3u8_file, "w") as writer:
        writer.write(m)

    LOGGER.info(m3u8_file)

        



CATEGORY_MAP = {
    "i" : get_image,
    "v" : stream_video,
    "m3u8" : get_m3u8
}

