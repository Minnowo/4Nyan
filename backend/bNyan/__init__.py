
from asyncio import constants
import os 
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm 

from . import exceptions
from . import methods 
from . import reg
from . import models 
from . import database 
from . import constants_
from . import auth 

import hashlib

app = FastAPI()



origins = [
    "http://localhost:722",
    "localhost:722",
    "0.0.0.0:722",
    
    # frontend 
    "http://192.168.1.149:722",
    "192.168.1.149:722",
]

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

@app.post('/create/user')
def register_user(request : Request, data: OAuth2PasswordRequestForm = Depends()):
    print("uwu")
    _ = database.methods.create_user(data)
    print(_)
    return _ 

    username = data.username
    password = data.password

    print(username)
    print(password)

    return {
        "username" : username,
        "password" : password
    }

@app.post('/auth/token')
def login(request : Request, data: OAuth2PasswordRequestForm = Depends()):

    username = data.username
    password = data.password

    user = auth.authenticate_user(username, password)

    if not user:
        raise exceptions.API_401_CREDENTIALS_EXCEPTION
    
    access_token = auth.manager.create_access_token(
        data = {
            "username" : username,
            "user_id"  : user.user_id
        }
    )

    return {'access_token': access_token, 'token_type': 'bearer'}


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

    database.Base.metadata.create_all()
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
