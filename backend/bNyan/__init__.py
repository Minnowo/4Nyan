

import os
from fastapi import FastAPI, HTTPException, Request, Depends, File, UploadFile, Query, Body
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


@app.post("/delete/file")
async def delete_file(request : Request, file : Union[int, str, List[Union[int, str]]]):
    
    if not file:
        raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    if isinstance(file, str):
        
        if not reg.IS_RAW_HEXADECIMAL.match(file):
            raise exceptions.API_400_BAD_REQUEST_EXCEPTION

        f = database.Methods.remove_file(bytes.fromhex(file))

        if f:
            util.remove_file_db(f)

        return 
        

    if isinstance(file, int):
        
        f = database.Methods.remove_file(file)

        if f:
            util.remove_file_db(f)

        return 

    
    for x in database.Methods.remove_files(
                        i if isinstance(i, int) else bytes.fromhex(i) 
        
                        for i in file 
        
                        if isinstance(i, int) or 
                            isinstance(i, str) and reg.IS_RAW_HEXADECIMAL.match(i)
                        ):

        util.remove_file_db(x)




@app.get("/search/get_file_tags")
async def search_tags(request : Request, fid : List[int] = Query(None), fh : List[str] = Query(None)):

    tag = {}

    if fh:

        raise exceptions.API_500_NOT_IMPLEMENTED

        fh = [bytes.fromhex(h) for h in fh if reg.IS_RAW_HEXADECIMAL.match(h)]

    
    if fid:

        for id in fid:
        
            tag[id] = [t for t in database.Methods.get_file_tags_from_id(id)]
        
    return tag 


@app.get("/search/get_categories/")
async def search_categories(request : Request):

    return list(database.Methods.get_categories())


@app.get("/search/get_files")
async def search_files(request : Request, 
                        sort_t : int = 4, sort_a : bool = False, 
                        fid : List[int] = Query(None), # hash id
                        tid : List[int] = Query(None), # tag id 
                        nid : List[int] = Query(None), # namespace id 
                        sid : List[int] = Query(None)  # subtag id 
                        ):

    htag = request.headers.get("content_tag", None)
    etag = config.get((), "content_tag")
    
    if htag:

        if htag == etag:

            return {}

    search = models.FileSearch(
        sort_type     = sort_t,
        sort_asc      = sort_a,
        hash_ids      = fid,
        tag_ids       = tid,
        namespace_ids = nid,
        subtag_ids    = sid,
    )
    
    files = [ ]
    for file in database.Methods.search_files(search):

        if methods.get_static_route_from_mime(file.mime) == 'None':
            continue

        # convert the hash to hex so it's json safe 
        file.hash = file.hash.hex()

        # builds the static url,
        # 'http://' + '0.0.0.0:700' + '/' + 'static/i' + 'filename' + '.ext'

        leading = "http://{}/".format(config.get((), "server_address"))
        ending  = file.hash + constants_.MIME_EXT_LOOKUP.get(file.mime, "") 

        urls    = {
            "content" : [ leading + methods.get_static_route_from_mime(file.mime) + "/" + ending ],
            "thumbs"  : [ leading + constants_.STATIC_THUMBNAIL_ROUTE + "/" + file.hash + ".jpg" ],
            "subs"    : []
        }

        if file.mime in constants_.VIDEO_MIMES:
            
            m3u8_dir = os.path.join(constants_.STATIC_M3U8_PATH, file.hash[0:2], file.hash)
            
            if os.path.isfile(os.path.join(m3u8_dir, "master.m3u8")):

                urls["content"].append(leading + constants_.STATIC_M3U8_ROUTE + "/" + file.hash + "?ts=master.m3u8")

            if os.path.isfile(os.path.join(m3u8_dir, "index.m3u8")):

                urls["content"].append(leading + constants_.STATIC_M3U8_ROUTE + "/" + file.hash + "?ts=index.m3u8")

            if os.path.isfile(os.path.join(m3u8_dir, "index_vtt.m3u8")):

                urls["subs"].append(leading + constants_.STATIC_M3U8_ROUTE + "/" + file.hash + "?ts=index_vtt.m3u8")


            # this is temporary until i figure out how i want to do subtitles
            # i'm thinking i will add each subtitle to the database as it's own file
            # and make a group to link them to their video and use tags for name / title and other info
            # rn this is just a lazy solution to see if this works 
            ###############################################################################################################
            subs_dir = os.path.join(constants_.STATIC_SUBTITLE_PATH, file.hash[0:2], file.hash)

            if os.path.isdir(subs_dir):

                for i in os.listdir(subs_dir):

                    if not reg.SUBTITLE_FILE.match(i):
                        continue

                    urls["subs"].append(leading + constants_.STATIC_SUBTITLE_ROUTE + "/" + file.hash + "?ts={}".format(i))
            ###############################################################################################################

        file.static_url = urls

        files.append(file)
        

    return {
        "content_tag" : etag,
        "content" : files 
    }


@app.post("/create/tag")
async def create_tag(request : Request, tag : Union[str, List[str]]): #, user = Depends(auth.manager)):

    if isinstance(tag, str):
        
        return database.Methods.create_tag(tag)

    
    if isinstance(tag, list):
        
        i = []
        for t in tag:
            
            try:
                i.append(database.Methods.create_tag(t))
            
            except HTTPException:
                pass 

        return i

    raise exceptions.API_400_BAD_REQUEST_EXCEPTION


@app.post("/create/file")
async def create_item(request : Request, data: UploadFile = File(...) ): #, user = Depends(auth.manager)):

    data_size = util.parse_int(request.headers.get('content-length', None), None)

    if not data or not data_size:
        raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    # if the file is ~1 gb there's also going to be data with it, so give 50mb of room
    if data_size > (constants_.GIGABYTE + constants_.MEGABYTE * 50):
        raise exceptions.API_400_BAD_FILE_EXCEPTION

    await methods.process_file_upload(data)

    config.set((), "content_tag", os.urandom(32).hex())
    

@app.post("/create/map")
async def create_map(request : Request, ftmap : Union[models.Tag_File, List[models.Tag_File]]):
    
    database.Methods.add_tag_to_file(ftmap)


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


@app.head('/static/{category}/{path}')
async def statichead(category: str, path: str, request : Request, ts : str = ""):
    cat = methods.CATEGORY_MAP.get(category, None)
    
    if cat is None:
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    if ts:

        return cat((path, ts), request)

    return cat(path, request)

@app.get('/static/{category}/{path}')
async def staticv1(category: str, path: str, request : Request, ts : str = ""):

    cat = methods.CATEGORY_MAP.get(category, None)
    
    if cat is None:
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    if ts:

        return cat((path, ts), request)

    return cat(path, request)



@app.get('/favicon.ico')
async def favicon():
    
    if(os.path.isfile(constants_.STATIC_FAVICON_PATH)):
        return FileResponse(constants_.STATIC_FAVICON_PATH)

    raise exceptions.API_404_NOT_FOUND_EXCEPTION



@app.get('/heartbeat')
@app.get('/')
async def heartbeat():
    
    return {
        "nyaa~" : "OwO",
        "-w-"   : "^w^",
        ";3c"   : "OwU"
    }


@app.get("/dash")
async def dash():

    man = "http://localhost:721/static/v/00man.mpd"
    vid = "http://localhost:721/static/v/00video.mp4"
    aud = "http://localhost:721/static/v/00audio.mp4"

    return FileResponse(man)

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
    database.Methods.add_defaults()

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












