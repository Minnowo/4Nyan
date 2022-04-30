

import os 
from fastapi import FastAPI, Request, Depends, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm 
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware

from . import exceptions
from . import methods 
from . import reg
from . import models 
from . import database 
from . import constants_
from . import auth 
from . import util 
from . import bn_logging

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
    

    if not file_id:
        raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    print(hashlib.sha256(file_id.encode()).digest())
    print(hashlib.sha256(file_id.encode()).digest().hex())
    print(bytes.fromhex(hashlib.sha256(file_id.encode()).digest().hex()))

    return methods.static_lookup(file_id)


@app.post("/create/file")
async def create_item(request : Request, data: UploadFile = File(...) ): #, user = Depends(auth.manager)):

    data_size = util.parse_int(request.headers.get('content-length', None), None)

    if not data or not data_size:
        raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    # if the file is ~1 gb there's also going to be data with it, so give 50mb of room
    if data_size > (constants_.GIGABYTE + constants_.MEGABYTE * 50):
        raise exceptions.API_400_BAD_FILE_EXCEPTION

    await methods.process_file_upload(data)
    
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
        ts = reg.INVALID_PATH_CHAR.sub("", ts)

        return methods.get_video(os.path.join(path, ts), request)

    return cat(path, request)


def main():
    import uvicorn

    LOGGER.info("=" * 128)
    LOGGER.info("Starting...")
    LOGGER.info("Creating static paths...")

    util.create_directory(constants_.STATIC_VIDEO_PATH)
    util.create_directory(constants_.STATIC_IMAGE_PATH)
    util.create_directory(constants_.STATIC_M3U8_PATH)
    util.create_directory(constants_.STATIC_TEMP_PATH)
    util.create_directory(constants_.STATIC_AUDIO_PATH)

    util.create_directory(constants_.BIN_FOLDER)

    LOGGER.info("Creating database tables.")
    database.Base.metadata.create_all()

    LOGGER.info("Running app...")
    uvicorn.run(app, host="0.0.0.0", port=721)

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
