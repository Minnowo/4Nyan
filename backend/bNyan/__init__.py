
import exceptions

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from methods import CATEGORY_MAP

app = FastAPI()

origins = [
    "http://localhost:3000",
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get('/')
async def get_item():
    return "hello world"

@app.get('/static/{category}/')
async def get_item1(category : str):
    return category 


@app.get('/static/{category}/{path}')
async def staticv1(category: str, path: str, request : Request):
    
    cat = CATEGORY_MAP.get(category, None)

    if cat is None:
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    return cat(path, request)


def main():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=721)

    return 0

def m3u8_test():

    from .m3u8 import PlaylistGenerator, VideoSplitter

    playlist_entries = [
                            {
                            'name':  "Awesomevideo_001.mp4",
                            'duration' : '10.04',
                            }
            ]

    playlist = PlaylistGenerator(playlist_entries).generate()

    output = "D:\\Programming\\.PROJECTS\\4Nyan\\backend\\bNyan\\static\\v\\split\\"
    splitter = VideoSplitter("X:\\ffmpeg\\ffmpeg.exe", "X:\\ffmpeg\\ffprobe.exe")
    splitter.split_video("D:\\Programming\\.PROJECTS\\4Nyan\\backend\\bNyan\\static\\v\\fall2.mp4", output, 10)

    entries = PlaylistGenerator.generate_from_directory(output, 10)

    print(entries)
    return 0

# from flask import Flask

# app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8000)