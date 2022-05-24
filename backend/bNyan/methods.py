import os 
import hashlib

from fastapi.responses import FileResponse
from fastapi import Response, UploadFile, HTTPException, Request

from typing import Union

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
from . import text

LOGGER = bn_logging.get_logger(constants_.BNYAN_METHODS[0], constants_.BNYAN_METHODS[1])

try:
    import image_size_reader as isr

except ImportError as imperr:

    LOGGER.critical("image-size-reader could not be found, this module is required, install it from https://github.com/Minnowo/image-size-reader")


def name_check(path : Union[str, tuple], checks = [reg.INVALID_PATH_CHAR]):

    if isinstance(path, tuple):

        l = sum(len(i) for i in path)

    else:

        l = len(path)
    
    # length check
    if (l < constants_.MIN_IMG_PATH_LENGTH):
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    if (l > constants_.MAX_IMG_PATH_LENGTH):
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    if isinstance(path, tuple):

        for p in path:
            
            for i in checks:

                if i.search(p):

                    raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    else:

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
    
    if util.in_range(mime, constants_.mime_types.IMAGE_MIME_RANGE):
        return constants_.STATIC_IMAGE_ROUTE

    if util.in_range(mime, constants_.mime_types.VIDEO_MIME_RANGE):
        return constants_.STATIC_VIDEO_ROUTE

    if util.in_range(mime, constants_.mime_types.AUDIO_MIME_RANGE):
        return constants_.STATIC_AUDIO_ROUTE

    # if mime in MT.IMAGE_MIMES:
    #     return constants_.STATIC_IMAGE_ROUTE

    # if mime in MT.VIDEO_MIMES:
    #     return constants_.STATIC_VIDEO_ROUTE

    # if mime in  MT.AUDIO_MIMES:
    #     return constants_.STATIC_VIDEO_ROUTE

    return "None" 

def get_static_path_from_mime(mime : int):
    """ returns the static path where a file should be stored based of the given mime type """

    if util.in_range(mime, constants_.mime_types.IMAGE_MIME_RANGE):
        return constants_.STATIC_IMAGE_PATH

    if util.in_range(mime, constants_.mime_types.VIDEO_MIME_RANGE):
        return constants_.STATIC_VIDEO_PATH
        
    if util.in_range(mime, constants_.mime_types.AUDIO_MIME_RANGE):
        return constants_.STATIC_AUDIO_PATH

    # if mime in MT.IMAGE_MIMES:
    #     return constants_.STATIC_IMAGE_PATH

    # if mime in MT.VIDEO_MIMES:
    #     return constants_.STATIC_VIDEO_PATH

    # if mime in  MT.AUDIO_MIMES:
    #     return constants_.STATIC_AUDIO_PATH

    return constants_.STATIC_TEMP_PATH








def _get_image(image_name : str, request : Request):
    """ returns a FileResponse with the requested image """

    headers = {
        'accept-range' : 'bytes',
        'content-type' : 'image/jpeg',
        'filename' : image_name
    }

    if request.method == "HEAD":
        return headers

    image_name = get_clean_name_or_die(image_name, constants_.STATIC_IMAGE_PATH)

    return FileResponse(image_name, headers=headers, media_type="image")


def _get_thumbnail(image_name : str, request : Request):
    """ returns a FileResponse with the requested image """

    headers = {
        'accept-range' : 'bytes',
        'content-type' : 'image/jpeg', # important for direct links to show the actual image
        'filename' : image_name
    }

    if request.method == "HEAD":
        return headers

    image_name = get_clean_name_or_die(image_name, constants_.STATIC_THUMBNAIL_PATH)

    return FileResponse(image_name, headers=headers, media_type="image")


def _stream_video(video_name : str, request : Request):
    """ returns a partial response with bytes from the request video file """

    if request is None:
        raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    video_name = get_clean_name_or_die(video_name, constants_.STATIC_VIDEO_PATH)

    total_response_size = os.stat(video_name).st_size

    # get start byte range from header, default to 0 
    _range = reg.RANGE_HEADER.search(request.headers.get("range", "bytes=0-"))

    if not _range: # doesn't match regex, bad header request 
        raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    start_byte_requested = int(_range.group(1))
    end_byte_planned     = min(start_byte_requested + constants_.VIDEO_STREAM_CHUNK_SIZE, total_response_size)

    headers={
            "Accept-Ranges" : "bytes",
            "Content-Range" : f"bytes {start_byte_requested}-{end_byte_planned}/{total_response_size}",
            "Content-Type"  : "video/mp4"
        }

    if request.method == "HEAD":
        return headers 

    with open(video_name, "rb") as reader:

        reader.seek(start_byte_requested)

        data = reader.read(end_byte_planned)
        
        return Response(data, status_code=constants_.status_codes.PARTIAL_RESPONSE, headers=headers)


def _get_video(video_name : tuple, request : Request):
    """ Returns a full video with a 200 request, this is used to transer .ts video files for hls"""

    name_check(video_name)

    (dire, file) = video_name

    video_path = get_clean_name(os.path.join(dire, file), constants_.STATIC_VIDEO_PATH)

    # file name check
    # video_name = clean_path(video_name, constants_.STATIC_VIDEO_PATH, [reg.INVALID_PATH_WITHOUT_SEP.sub]) # allow / and \ in the path name
    
    total_response_size = os.stat(video_path).st_size

    headers={
            "Accept-Ranges" : "bytes",
            "Content-Range" : f"bytes {0}-{total_response_size}/{total_response_size}",
            "Content-Type"  : "video/ts",
            "Content-Disposition": 'attachment; filename="{}"'.format(file),
        }

    if video_path.endswith(".vtt"):
        headers["Content-Type"] = "text/vtt"

    if request.method == "HEAD":
        return headers 

    with open(video_path, "rb") as reader:

        data = reader.read(total_response_size)

        
        return Response(data, status_code=constants_.status_codes.RESPONSE, headers=headers) 


def _get_m3u8(m3u8_path : tuple, request : Request):

    name_check(m3u8_path)

    (dire, file) = m3u8_path

    headers={
            "Accept-Ranges" : "bytes",
            "Content-Type"  : "application/vnd.apple.mpegurl",
            "Content-Disposition": 'attachment; filename="{}"'.format(file),
        }

    if request.method == "HEAD":
        return headers

    m3u8_path = get_clean_name(os.path.join(dire, file), constants_.STATIC_M3U8_PATH)

    return FileResponse(m3u8_path, status_code=constants_.status_codes.RESPONSE, headers=headers)















def generate_thumbnail(data):

    try:
        src = data.get("src")
        dst = data.get("dst")
        mime = data.get("mime")

        if mime == constants_.mime_types.UNDETERMINED_VIDEO: # video 

            if not file_handling.video_handling.generate_thumbnail(src, dst, constants_.THUMBNAIL_SIZE):
    
                LOGGER.warning("Failed to generate thumbnail for: {}".format(src))

        elif not file_handling.image_handling.generate_save_image_thumbnail(src, dst, mime, 
                    constants_.THUMBNAIL_SIZE, file_handling.image_handling.THUMBNAIL_SCALE_DOWN_ONLY):

            LOGGER.warning("Failed to generate thumbnail for: ".format(src))

    except exceptions.FFMPEG_Exception as e:

        LOGGER.warning("FFMPEG exception while generating thumbnail for {}. -> {}".format(src, e))

    except Exception as e:

        LOGGER.error("Error while generating thumbnail for {}.".format(src), e, exc_info=True)



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

        if "tags" in kwargs:

            for t in kwargs["tags"]:

                LOGGER.info("Adding tag '{}' to file: '{}'".format(t, sha256.hex()))

                try:
                    
                    tag = database.Methods.create_tag(t)
                    database.Methods.add_tag_to_file(models.Tag_File(tag_id=tag.tag_id, file_id = db_file.hash_id))

                except HTTPException:
                    
                    continue 

                except Exception as e:
                    LOGGER.error("Exception thrown adding tag to file ", e, exc_info=True)



    except HTTPException as e:
        
        LOGGER.warning("Exception thrown adding file to the database -> {}".format(e))

        util.remove_file(delete_on_httperr) # delete the temp file 

        raise e 




def process_video(data):
    """ passed into a worker queue to split and encode a video into ts files, and then creates the m3u8 file """

    source_video = data['file_path']
    output_dir   = data['output']
    ts_url       = data['ts_url']
    m3u8_url     = data['m3u8_url']
    sha256_hex   = data['sha256_hex']

    try:

        m3u8 = file_handling.video_handling.split_video(source_video, output_dir, 6, ts_url, ts_url, m3u8_url)

    except exceptions.FFMPEG_Exception as e:

        LOGGER.error(e)
        
        util.remove_file(source_video)

        return 

    hash = os.path.basename(output_dir)
    m3u8_directory = os.path.join(constants_.STATIC_M3U8_PATH, hash[0:2], hash)
    
    util.create_directory(m3u8_directory)

    util.rename_file(m3u8[0], os.path.join(m3u8_directory, "master.m3u8"), replace=True)
    util.rename_file(m3u8[1], os.path.join(m3u8_directory, "index.m3u8") , replace=True)

    if len(m3u8) == 3:
        util.rename_file(m3u8[2], os.path.join(m3u8_directory, "index_vtt.m3u8") , replace=True)

    tdata = {
            "src" : source_video,
            "dst" : os.path.join(constants_.STATIC_THUMBNAIL_PATH, sha256_hex[0:2], sha256_hex + ".jpg"),
            "mime" : constants_.mime_types.UNDETERMINED_VIDEO, 
        }

    threading_.append_worker_data(constants_.THREAD_THUMBNAIL, tdata, generate_thumbnail)

    try:
        
        # it's pretty dumb that this will throw multiple arg error for 'mime'
        del data['video_info']['mime']

        add_file_to_database(data["sha256_bytes"], data["file_size"], data["mime"], source_video, **data["video_info"])

    except Exception as e:

        LOGGER.error(e, exc_info=True)


def add_image_to_database(sha256_bytes : bytes, file_size : int , mime : int, filename : str, **kwargs):
    """ adds the image file to the database """

    width, height = isr.get_image_size(filename)

    kwargs.update({
        "width" : width,
        "height" : height, 
        "has_audio" : False,
    })

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

    original_filename = file.filename

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
        

    file_ext = constants_.MIME_EXT_LOOKUP.get(mime, None)

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


    kwargs = {
        "tags" : [
            "filename:" + original_filename
        ]
    }

    if static_path == constants_.STATIC_IMAGE_PATH:

        tdata = {
            "src" : filename,
            "dst" : os.path.join(constants_.STATIC_THUMBNAIL_PATH, sha256_hex[0:2], sha256_hex + ".jpg"),
            "mime" : mime, 
        }

        threading_.append_worker_data(constants_.THREAD_THUMBNAIL, tdata, generate_thumbnail)

        add_image_to_database(sha256_bytes, file_size, mime, filename, **kwargs)
        return 



    if static_path != constants_.STATIC_VIDEO_PATH:
        
        add_file_to_database(sha256_bytes, file_size, mime, filename, **kwargs)

        return


    ts_folder = os.path.join(static_path, sha256_hex[0:2], sha256_hex )

    if not util.create_directory(ts_folder):

        LOGGER.warning("Cannot create ts folder '{0}' for video file '{1}'".format(ts_folder, filename))

        util.remove_file(filename)

        raise exceptions.API_500_OSERROR

    video_info.update(kwargs)

    data = {
        "file_path"    : filename,
        "output"       : ts_folder,
        "m3u8_output"  : os.path.join(constants_.STATIC_M3U8_PATH, sha256_hex[0:2], sha256_hex),
        "ts_url"       : "http://{0}/static/v/{1}?ts={2}".format(config.get((), "server_address"), sha256_hex, '{}'),
        "m3u8_url"     : "http://{0}/static/m3u8/{1}?ts={2}".format(config.get((), "server_address"), sha256_hex, '{}'),
        "sha256_hex"   : sha256_hex,
        "sha256_bytes" : sha256_bytes,
        "file_size"    : file_size,
        "mime"         : mime,
        "video_info"   : video_info
    }
    
    threading_.append_worker_data(constants_.THREAD_FFMPEG, data, process_video)

        

def get_thumbnail(path, request):
    
    if isinstance(path, tuple):

        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    return _get_thumbnail(path, request)


def get_image(path, request):

    if isinstance(path, tuple):

        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    return _get_image(path, request) 


def get_video(path, request):

    if isinstance(path, tuple):

        return _get_video(path, request)

    return _stream_video(path, request) 


def get_m3u8(path, request):
    
    if isinstance(path, tuple):

        return _get_m3u8(path, request) 

    raise exceptions.API_404_NOT_FOUND_EXCEPTION
    

CATEGORY_MAP = {
    "t"    : get_thumbnail,
    "i"    : get_image,
    "v"    : get_video, 
    "m3u8" : get_m3u8
}

