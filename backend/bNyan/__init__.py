

import os 
from fastapi import FastAPI, Request, Depends, File, UploadFile, Query, Body
from fastapi.security import OAuth2PasswordRequestForm 
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from typing import List 
from typing import Optional, Union

from . import file_handling

from . import exceptions
from . import methods 
from . import reg
from . import models 
from . import database 
from . import constants_
from . import auth 
from . import util 
from . import bn_logging
from . import config
from . import threading_

import hashlib

LOGGER = bn_logging.get_logger(constants_.BNYAN_MAIN[0], constants_.BNYAN_MAIN[1])

app = FastAPI()

origins = [
    "http://localhost:722",
    "localhost:722",
    "0.0.0.0:722",
    
    # frontend 
    "http://192.168.1.149:722",
    "192.168.1.149:722",
]

app.add_middleware(GZipMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



# DEBUG STUFF 
@app.get('/get_file')
async def getfile(request : Request, file_id : str = ""):
    
    raise exceptions.API_404_NOT_FOUND_EXCEPTION

    if not file_id:
        raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    print(hashlib.sha256(file_id.encode()).digest())
    print(hashlib.sha256(file_id.encode()).digest().hex())
    print(bytes.fromhex(hashlib.sha256(file_id.encode()).digest().hex()))

    return methods.static_lookup(file_id)

@app.get("/search/get_file_tags")
async def search_tags(request : Request, fid : List[int] = Query(None), fh : List[str] = Query(None)):

    if fh:

        fh = [bytes.fromhex(h) for h in fh if reg.IS_RAW_HEXADECIMAL.match(h)]



@app.get("/search/get_files")
async def search_files(request : Request, sort_t : int = 4, sort_a : bool = False, fid : List[int] = Query(None)):

    htag = request.headers.get("content_tag", None)
    etag = config.get((), "content_tag")
    
    if htag:

        if htag == etag:

            return {}

    search = models.FileSearch()
    search.sort_type = sort_t
    search.sort_asc = sort_a
    search.hash_ids = fid
    
    files = [ ]
    for file in database.Methods.search_files(search):

        # convert the hash to hex so it's json safe 
        file.hash = file.hash.hex()

        # builds the static url,
        # 'http://' + '0.0.0.0:700' + '/' + 'static/i' + 'filename' + '.ext'

        leading = "http://" + config.get((), "server_address") + "/"
        ending  = file.hash + constants_.mime_ext_lookup.get(file.mime, "") 

        file.static_url = ( leading + methods.get_static_route_from_mime(file.mime) + "/" + ending, 
                            leading + constants_.STATIC_THUMBNAIL_ROUTE + "/" + ending )
        
        files.append(file)
        

    return {
        "content_tag" : etag,
        "content" : files 
    }


@app.post("/create/tag")
async def create_tag(request : Request, tag : Union[models.Tag, List[models.Tag]]): #, user = Depends(auth.manager)):

    print(tag)
    
    print(type(tag))

    return {
        "tag" : tag,
    }


@app.post("/create/file")
async def create_item(request : Request, data: UploadFile = File(...), user = Depends(auth.manager)):

    data_size = util.parse_int(request.headers.get('content-length', None), None)

    if not data or not data_size:
        raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    # if the file is ~1 gb there's also going to be data with it, so give 50mb of room
    if data_size > (constants_.GIGABYTE + constants_.MEGABYTE * 50):
        raise exceptions.API_400_BAD_FILE_EXCEPTION

    await methods.process_file_upload(data)

    config.set((), "content_tag", os.urandom(32).hex())
    
    return True 



@app.post('/create/user')
async def register_user(request : Request, data: OAuth2PasswordRequestForm = Depends()):
    
    return database.methods.create_user(data)


@app.post('/auth/token')
async def login(request : Request, data: OAuth2PasswordRequestForm = Depends()):

    username = data.username
    password = data.password

    user = auth.load_user(username)

    if not user:
        raise exceptions.API_401_CREDENTIALS_EXCEPTION

    if not auth.verify_password(password, user.hashed_password):
        raise exceptions.API_401_CREDENTIALS_EXCEPTION

    access_token = auth.manager.create_access_token(
        data = {
            "sub" : username,
        }
    )

    return {
        'access_token': access_token, 
        'token_type': 'bearer',
        'username'  : username,
        'user_id'   : user.user_id
    }


@app.get('/static/{category}/{path}')
async def staticv1(category: str, path: str, request : Request, ts : str = ""):

    cat = methods.CATEGORY_MAP.get(category, None)
    
    if cat is None:
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    if ts: # should probably check category or make the function just take the ts arg 

        return methods.get_video((path, ts), request)

    return cat(path, request)

@app.get('/favicon.ico')
async def favicon():
    
    if(os.path.isfile(constants_.STATIC_FAVICON_PATH)):
        return FileResponse(constants_.STATIC_FAVICON_PATH)

    raise exceptions.API_404_NOT_FOUND_EXCEPTION

def main():
    import uvicorn

    LOGGER.info("=" * 128)
    LOGGER.info("Starting...")
    
    LOGGER.info("Loading main config...")
    config.load(constants_.MAIN_CONFIG)


    server_ip   = config.get((), "server_ip", None)
    port_number = config.get((), "port", None)
    server_address = "{}:{}".format(server_ip, port_number)

    if server_ip is None:
        raise Exception("Server IP must be set in {} -> 'server_ip' : '0.0.0.0'".format(constants_.MAIN_CONFIG))

    if port_number is None:
        raise Exception("Port number must be set in {} -> 'port' : 721".format(constants_.MAIN_CONFIG))

    config.set((), "server_address", server_address)

    if not config.get((), "content_tag", None):

        config.set((), "content_tag", os.urandom(32).hex())


    LOGGER.info("Creating static paths...")
    util.create_directory(constants_.STATIC_VIDEO_PATH)
    util.create_directory(constants_.STATIC_IMAGE_PATH)
    util.create_directory(constants_.STATIC_THUMBNAIL_PATH)
    util.create_directory(constants_.STATIC_M3U8_PATH)
    util.create_directory(constants_.STATIC_TEMP_PATH)
    util.create_directory(constants_.STATIC_AUDIO_PATH)

    util.create_directory(constants_.BIN_FOLDER)

    for i in range(0xff + 1):

        f = hex(i)[2:].zfill(2)
        
        util.create_directory(os.path.join(constants_.STATIC_VIDEO_PATH, f))
        util.create_directory(os.path.join(constants_.STATIC_IMAGE_PATH, f))
        util.create_directory(os.path.join(constants_.STATIC_THUMBNAIL_PATH, f))
        util.create_directory(os.path.join(constants_.STATIC_M3U8_PATH, f))
        util.create_directory(os.path.join(constants_.STATIC_AUDIO_PATH, f))

    LOGGER.info("Creating database tables.")
    database.Base.metadata.create_all()

    try:
        threading_.spawn_worker_thread(constants_.THREAD_FFMPEG, lambda x : None)
        threading_.spawn_worker_thread(constants_.THREAD_THUMBNAIL, lambda x : None)

        LOGGER.info("Running app -> http://{}/".format(server_address))
        
        uvicorn.run(app, host="0.0.0.0", port=port_number)

    except Exception as e:
        LOGGER.critical(e.__repr__())

    finally:

        threading_.cleanup_all_threads()

        config.save(constants_.MAIN_CONFIG)

    return 0
















def m3u8_test():

    from .m3u8 import PlaylistGenerator, VideoSplitter

    output = "D:\\Programming\\.PROJECTS\\4Nyan\\backend\\bNyan\\static\\v\\RnM_S4E1\\"
    segment_size = 10
    splitter = VideoSplitter("X:\\ffmpeg\\ffmpeg.exe", "X:\\ffmpeg\\ffprobe.exe")
    splitter.split_video("D:\\Programming\\.PROJECTS\\4Nyan\\backend\\bNyan\\static\\v\\Rick and Morty - S04E01.mkv", output, segment_size)

    entries = PlaylistGenerator.generate_from_directory("http://192.168.1.149:721/static/v/" + os.path.basename(output), output, segment_size)

    print(entries)
    return 0
