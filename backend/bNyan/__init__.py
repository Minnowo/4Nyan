
from asyncio import constants
import os 
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from . import exceptions
from . import methods 
from . import reg
from . import models 
from . import database 
from . import constants

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

    print(file_id)
    return methods.static_lookup(file_id, request)


# DEBUG STUFF 
@app.get('/add_file')
async def addfile(request : Request):
    
    f = "D://file.txt"
    
    file = models.File(
                hash      = hashlib.sha256(f.encode()).digest(),
                size      = os.stat(f).st_size,
                mime      = constants.IMAGE_PNG,
                width     = 0,
                height    = 0,
                duration  = 0,
                num_words = 2,
                has_audio = False
            )

    database.Methods.add_file(file)


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

# from flask import Flask

# app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8000)