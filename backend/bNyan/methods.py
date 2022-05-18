import os 
import hashlib

from fastapi.responses import FileResponse
from fastapi import Response, UploadFile, HTTPException, Request


from .constants_ import mime_types as MT 

from . import threading_
from . import file_handling
from . import reg
from . import constants_ 
from . import exceptions
from . import util
from . import database
from . import models 
from . import bn_logging
from . import config 

LOGGER = bn_logging.get_logger(constants_.BNYAN_METHODS[0], constants_.BNYAN_METHODS[1])

try:
    import image_size_reader as isr

except ImportError as imperr:

    LOGGER.critical("image-size-reader could not be found, this module is required, install it from https://github.com/Minnowo/image-size-reader")


def name_check(path : str, checks = [reg.INVALID_PATH_CHAR]):

    l = len(path)
    
    # length check
    if (l < constants_.MIN_IMG_PATH_LENGTH):
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    if (l > constants_.MAX_IMG_PATH_LENGTH):
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    for i in checks:

        if i.search(path):

            raise exceptions.API_400_BAD_REQUEST_EXCEPTION


def get_clean_name(path : str, rout : str):

    path = os.path.join(rout, path[0:2], path)

    if not os.path.isfile(path):

        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    return path 
    
def get_clean_name_or_die(path : str, rout : str, checks = None):

    if checks is None:
        name_check(path)

    else:
        name_check(path, checks)

    return get_clean_name(path, rout)



def clean_path(path : str, rout : str, cleans=[reg.INVALID_PATH_CHAR.sub]):
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


def get_static_route_from_mime(mime : int):
    """ returns the static route where a file should be accessed via the static url from the given mime type """
    
    if mime in MT.IMAGE_MIMES:
        return constants_.STATIC_IMAGE_ROUTE

    if mime in MT.VIDEO_MIMES:
        return constants_.STATIC_VIDEO_ROUTE

    if mime in  MT.AUDIO_MIMES:
        return constants_.STATIC_VIDEO_ROUTE

    return None 

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

    image_name = get_clean_name_or_die(image_name, constants_.STATIC_IMAGE_PATH)
    
    return FileResponse(image_name)


# returns a FileReponse object
def get_thumbnail(image_name : str, request : Request):
    """ returns a FileResponse with the requested image """

    image_name = get_clean_name_or_die(image_name, constants_.STATIC_THUMBNAIL_PATH)

    return FileResponse(image_name)


def stream_video(video_name : str, request : Request):
    """ returns a partial response with bytes from the request video file """

    if request is None:
        raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    video_name = get_clean_name_or_die(video_name, constants_.STATIC_VIDEO_PATH)

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


def get_video(video_name : tuple, request : Request):
    """ Returns a full video with a 200 request, this is used to transer .ts video files for hls"""

    (dire, file) = video_name

    name_check(dire)
    name_check(file)

    video_path = get_clean_name(os.path.join(dire, file), constants_.STATIC_VIDEO_PATH)

    # file name check
    # video_name = clean_path(video_name, constants_.STATIC_VIDEO_PATH, [reg.INVALID_PATH_WITHOUT_SEP.sub]) # allow / and \ in the path name
    
    total_response_size = os.stat(video_path).st_size

    with open(video_path, "rb") as reader:

        data = reader.read(total_response_size)

        headers={
            "Accept-Ranges" : "bytes",
            "Content-Range" : f"bytes {0}-{total_response_size}/{total_response_size}",
            "Content-Type"  : "video/ts"
        }
        return Response(data, status_code=constants_.status_codes.RESPONSE, headers=headers) 


def get_m3u8(file : str, request : Request):
    
    file = get_clean_name_or_die(file, constants_.STATIC_M3U8_PATH)

    return FileResponse(file, status_code=constants_.status_codes.RESPONSE)


def static_lookup(file_hash : str):
    
    LOGGER.error("This endpoint is depricated")
    raise Exception("Depricated endpoint")

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















def generate_thumbnail(data):

    try:
        src = data.get("src")
        dst = data.get("dst")
        mime = data.get("mime")

        if not file_handling.image_handling.generate_save_image_thumbnail(
            src, dst, mime, 
            constants_.THUMBNAIL_SIZE, 
            file_handling.image_handling.THUMBNAIL_SCALE_DOWN_ONLY):
            LOGGER.warning("failed to generate thumbnail for: " + src)

    except Exception as e:

        LOGGER.warning(e)



def add_file_to_database(sha256 : bytes, file_size : int, mime : int, delete_on_httperr : str, **kwargs):

    db_file = models.File(
        hash=sha256, 
        size=file_size, 
        mime=mime, 
        width=kwargs.get("width", 0), 
        height=kwargs.get("height", 0), 
        duration=kwargs.get("duration", 0), 
        num_words=kwargs.get("num_words", 0), 
        has_audio=kwargs.get("has_audio", False))

    try:
        
        # will throw an exception if the file is in the database 
        database.Methods.add_file(db_file)

    except HTTPException as e:
        
        LOGGER.warning("error thrown adding file to the database -> {}".format(e))

        util.remove_file(delete_on_httperr) # delete the temp file 

        raise e 




def process_video(data):
    """ passed into a worker queue to split and encode a video into ts files, and then creates the m3u8 file """

    try:

        m3u8 = file_handling.video_handling.split_video(data["file_path"], data["output"])

    except Exception as e:

        LOGGER.error(e)
        
        util.remove_file(data["file_path"])

        return 

    util.rename_file(m3u8, data["m3u8_output"], replace=True)

    lines = []

    with open(data["m3u8_output"], "r") as reader:

        for line in reader:

            if reg.IS_TS_FILENAME.match(line):

                lines.append(data["ts_url"] + line)
                continue

            lines.append(line)

    with open(data["m3u8_output"], "w") as writer:

        writer.writelines(lines)

    try:
        
        # it's pretty dumb that this will throw multiple arg error for 'mime'
        if 'mime' in data['video_info']:
            del data['video_info']['mime']

        add_file_to_database(data["sha256_bytes"], data["file_size"], data["mime"], data["file_path"], **data["video_info"])

    except Exception as e:

        LOGGER.error(e)


def add_image_to_database(sha256_bytes : bytes, file_size : int , mime : int, filename : str):
    """ adds the image file to the database """

    width, height = isr.get_image_size(filename)

    kwargs = {
        "width" : width,
        "height" : height, 
        "has_audio" : False,
    }

    add_file_to_database(sha256_bytes, file_size, mime, filename, **kwargs)



async def process_file_upload(file : UploadFile):

    header_bytes = await file.read(256)

    try:
        
        # if the mime is an unknown mp4 or wm, we will need ffmpeg to validate the video
        # if this is the case we have to download the whole file 
        mime = file_handling.get_mime_from_bytes(header_bytes)

    except exceptions.FFMPEG_Required_Exception:
        
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

    await file.close()

    sha256_bytes = h_sha256.digest()

    # if the file is in the database give up here
    if database.Methods.file_hash_exists(sha256_bytes):
        
        util.remove_file(tempname)

        raise exceptions.API_409_FILE_EXISTS_EXCEPTION

    # we need to use ffmpeg to check the video
    if mime == MT.UNDETERMINED_VIDEO or mime in constants_.VIDEO_MIMES:

        ffmpeg_lines = file_handling.video_handling.get_ffmpeg_info_lines(tempname)

        video_info = file_handling.video_handling.get_video_information_from_ffmpeg_lines(ffmpeg_lines)
        
        mime = video_info["mime"]

        if mime == MT.APPLICATION_UNKNOWN:

            LOGGER.warning("unknown video, ffmpeg could not determine video format -> assuming invalid file")

            util.remove_file(tempname)

            raise exceptions.API_400_BAD_FILE_EXCEPTION
        

    file_ext = constants_.mime_ext_lookup.get(mime, None)

    # i probably just forgot to add the mime to the extension map if this is true 
    if not file_ext:

        LOGGER.warning("could not find a file extension for mime type of '{}'".format(mime))
        
        raise exceptions.API_400_BAD_FILE_EXCEPTION


    sha256_hex   = sha256_bytes.hex()
    file_size    = os.path.getsize(tempname)

    static_path = get_static_path_from_mime(mime)
    filename    = os.path.join(static_path, sha256_hex[0:2], sha256_hex + file_ext)

    # rename the file
    if not util.rename_file(tempname, filename):
        LOGGER.warning("Cannot rename file '{0}' -> '{1}' hash '{2}' assuming file exists".format(tempname, filename, sha256_hex))


    if static_path == constants_.STATIC_IMAGE_PATH:

        tdata = {
            "src" : filename,
            "dst" : os.path.join(constants_.STATIC_THUMBNAIL_PATH, sha256_hex[0:2], sha256_hex + file_ext),
            "mime" : mime, 
        }

        threading_.append_worker_data(constants_.THREAD_THUMBNAIL, tdata, generate_thumbnail)

        add_image_to_database(sha256_bytes, file_size, mime, filename)
        return 



    if static_path != constants_.STATIC_VIDEO_PATH:
        
        add_file_to_database(sha256_bytes, file_size, mime, filename)

        return


    ts_folder = os.path.join(static_path, sha256_hex[0:2], sha256_hex )

    if not util.create_directory(ts_folder):

        LOGGER.warning("Cannot create ts folder '{0}' for video file '{1}'".format(ts_folder, filename))

        util.remove_file(filename)

        raise exceptions.API_500_OSERROR


    data = {
        "file_path"    : filename,
        "output"       : ts_folder,
        "m3u8_output"  : os.path.join(constants_.STATIC_M3U8_PATH, sha256_hex[0:2], sha256_hex + ".m3u8"),
        "ts_url"       : "http://{0}/static/v/{1}?ts=".format(config.get((), "server_address"), sha256_hex),
        "sha256_bytes" : sha256_bytes,
        "file_size"    : file_size,
        "mime"         : mime,
        "video_info"   : video_info
    }

    threading_.append_worker_data(constants_.THREAD_FFMPEG, data, process_video)

        



CATEGORY_MAP = {
    "t" : get_thumbnail,
    "i" : get_image,
    "v" : stream_video,
    "m3u8" : get_m3u8
}

