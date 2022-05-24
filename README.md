

## 4Nyan
A LAN site meant to stream video, audio, text, and images from a local server over LAN.


*This is very early in development and currently very unusable (unless you want to only stream video using mpv)*

### Current Features

- HLS (http live streaming) of video using m3u8 files
- Image serving endpoint
- Basic database layout
- Very bare bones frontend used to test the HLS

### Plans for the future

- Youtube-like UI for video streaming
- Danbooru-like gallery of randomly tagged images 
- nHentai-like manga / book reader 
- Serving books as PDF or HTML
- Audio *eventually*

## Frontend 
The frontend is built using [Reactjs](https://reactjs.org/), with [Bootstrap](https://getbootstrap.com/docs/5.1/getting-started/download/) for css. 

## Backend
The backend is built using [FastAPI](https://fastapi.tiangolo.com/), using Python [3.7.6](https://www.python.org/downloads/release/python-376/) (I'm assuming anything 3.7+ will work just fine).

## Database
The database is [SQLite](https://sqlite.org/index.html), this is being used with [SQLAlchemy](https://www.sqlalchemy.org/) for all queries and connections.

## Dependencies
- [requirements.txt](./backend/bNyan/requirements.txt) (python libraries from pip)
- https://github.com/Minnowo/image-size-reader (for reading image sizes used for thumbnails)
- https://github.com/FFmpeg/FFmpeg (ffmpeg and ffprobe)
- https://github.com/shaka-project/shaka-packager (will be used for dash and hls file creation)




https://github.com/Dash-Industry-Forum/dash.js/issues/2259
https://github.com/aminyazdanpanah/python-ffmpeg-video-streaming#dash