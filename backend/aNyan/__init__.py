import os
import logging

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    Depends,
    File,
    UploadFile,
    Query,
    Body,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from typing import List
from typing import Optional, Union

from . import exceptions
from . import methods
from . import reg
from . import models
from . import constants_
from . import auth
from . import util
from . import config
from . import threading_


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
    allow_headers=["*"],
)


@app.post("/delete/file")
async def delete_file(request: Request, file: Union[int, str, List[Union[int, str]]]):

    raise exceptions.API_404_USER_NOT_FOUND_EXCEPTION


@app.get("/search/get_file_tags")
async def search_tags(request: Request, fid: List[int] = Query(None), fh: List[str] = Query(None)):

    raise exceptions.API_404_USER_NOT_FOUND_EXCEPTION


@app.get("/search/get_categories/")
async def search_categories(request: Request):

    raise exceptions.API_404_USER_NOT_FOUND_EXCEPTION


@app.get("/search/get_files")
async def search_files(
    request: Request,
    sort_t: int = 4,
    sort_a: bool = False,
    fid: List[int] = Query(None),  # hash id
    tid: List[int] = Query(None),  # tag id
    nid: List[int] = Query(None),  # namespace id
    sid: List[int] = Query(None),  # subtag id
):

    raise exceptions.API_404_USER_NOT_FOUND_EXCEPTION


@app.post("/create/tag")
async def create_tag(request: Request, tag: Union[str, List[str]]):  # , user = Depends(auth.manager)):

    raise exceptions.API_404_USER_NOT_FOUND_EXCEPTION


@app.post("/create/file")
async def create_item(request: Request, data: UploadFile = File(...)):  # , user = Depends(auth.manager)):

    data_size = util.parse_int(request.headers.get("content-length", None), None)

    if not data or not data_size:
        raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    # if the file is ~1 gb there's also going to be data with it, so give 50mb of room
    if data_size > (constants_.GIGABYTE + constants_.MEGABYTE * 50):
        raise exceptions.API_400_BAD_FILE_EXCEPTION

    await methods.process_file_upload(data)

    config.set((), "content_tag", os.urandom(32).hex())


@app.post("/create/map")
async def create_map(request: Request, ftmap: Union[models.Tag_File, List[models.Tag_File]]):

    raise exceptions.API_404_USER_NOT_FOUND_EXCEPTION


@app.post("/create/user")
async def register_user(request: Request, data: OAuth2PasswordRequestForm = Depends()):

    raise exceptions.API_404_USER_NOT_FOUND_EXCEPTION


@app.post("/auth/token")
async def login(request: Request, data: OAuth2PasswordRequestForm = Depends()):

    username = data.username
    password = data.password

    user = auth.load_user(username)

    if not user:
        raise exceptions.API_401_CREDENTIALS_EXCEPTION

    if not auth.verify_password(password, user.hashed_password):
        raise exceptions.API_401_CREDENTIALS_EXCEPTION

    access_token = auth.manager.create_access_token(
        data={
            "sub": username,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": username,
        "user_id": user.user_id,
    }


@app.head("/static/{category}/{path}")
async def statichead(category: str, path: str, request: Request, ts: str = ""):
    cat = methods.CATEGORY_MAP.get(category, None)

    if cat is None:
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    if ts:

        return cat((path, ts), request)

    return cat(path, request)


@app.get("/static/{category}/{path}")
async def staticv1(category: str, path: str, request: Request, ts: str = ""):

    cat = methods.CATEGORY_MAP.get(category, None)

    if cat is None:
        raise exceptions.API_404_NOT_FOUND_EXCEPTION

    if ts:

        return cat((path, ts), request)

    return cat(path, request)


@app.get("/favicon.ico")
async def favicon():

    if os.path.isfile(constants_.STATIC_FAVICON_PATH):
        return FileResponse(constants_.STATIC_FAVICON_PATH)

    raise exceptions.API_404_NOT_FOUND_EXCEPTION


@app.get("/heartbeat")
@app.get("/")
async def heartbeat():

    return {"nyaa~": "OwO", "-w-": "^w^", ";3c": "OwU"}


def main():
    import uvicorn

    logging.info("Starting...")

    logging.info("Loading main config...")
    config.load(constants_.MAIN_CONFIG)

    server_ip = config.get((), "server_ip", None)
    port_number = config.get((), "port", None)
    server_address = "{}:{}".format(server_ip, port_number)

    if server_ip is None:
        raise Exception("Server IP must be set in {} -> 'server_ip' : '0.0.0.0'".format(constants_.MAIN_CONFIG))

    if port_number is None:
        raise Exception("Port number must be set in {} -> 'port' : 721".format(constants_.MAIN_CONFIG))

    config.set((), "server_address", server_address)

    if not config.get((), "content_tag", None):

        config.set((), "content_tag", os.urandom(32).hex())

    logging.info("Creating static paths...")
    util.create_directory(constants_.STATIC_VIDEO_PATH)
    util.create_directory(constants_.STATIC_IMAGE_PATH)
    util.create_directory(constants_.STATIC_THUMBNAIL_PATH)
    util.create_directory(constants_.STATIC_M3U8_PATH)
    util.create_directory(constants_.STATIC_TEMP_PATH)
    util.create_directory(constants_.STATIC_AUDIO_PATH)

    util.create_directory(constants_.BIN_FOLDER)

    for i in range(0xFF + 1):

        f = hex(i)[2:].zfill(2)

        util.create_directory(os.path.join(constants_.STATIC_VIDEO_PATH, f))
        util.create_directory(os.path.join(constants_.STATIC_IMAGE_PATH, f))
        util.create_directory(os.path.join(constants_.STATIC_THUMBNAIL_PATH, f))
        util.create_directory(os.path.join(constants_.STATIC_M3U8_PATH, f))
        util.create_directory(os.path.join(constants_.STATIC_AUDIO_PATH, f))

    try:
        threading_.spawn_worker_thread(constants_.THREAD_FFMPEG, lambda x: None)
        threading_.spawn_worker_thread(constants_.THREAD_THUMBNAIL, lambda x: None)

        logging.info("Running app -> http://{}/".format(server_address))

        uvicorn.run(app, host="0.0.0.0", port=port_number)

    except Exception as e:
        logging.critical(e.__repr__(), stack_info=True)

    finally:

        threading_.cleanup_all_threads()

        config.save(constants_.MAIN_CONFIG)

    return 0
