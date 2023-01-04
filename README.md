

## 4Nyan
A LAN site meant to stream video, audio, text, and images from a local server over LAN.


*This is very early in development and currently very unusable (unless you want to only stream video using mpv)*

### Current Features

- Can stream video using a single static endpoint

### Plans for the future

- HLS (http live streaming) of video using m3u8 files
- Youtube-like UI for video streaming
- Danbooru-like gallery of randomly tagged images 
- nHentai-like manga / book reader 
- Serving books as PDF or HTML
- Audio *eventually*

## Backend
The backend is built using [FastAPI](https://fastapi.tiangolo.com/), using Python [3.7.6](https://www.python.org/downloads/release/python-376/) (I'm assuming anything 3.7+ will work just fine).

## Database
The database is [SQLite](https://sqlite.org/index.html) via the `sqlite3` python module. 

## Dependencies
- [requirements.txt](./aNyan/requirements.txt) (python libraries from pip)
- https://github.com/Minnowo/image-size-reader (for reading image sizes used for thumbnails)
- https://github.com/FFmpeg/FFmpeg (ffmpeg and ffprobe)




https://github.com/Dash-Industry-Forum/dash.js/issues/2259
https://github.com/aminyazdanpanah/python-ffmpeg-video-streaming#dash