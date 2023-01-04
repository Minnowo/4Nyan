import os
import logging

from fastapi import (
    FastAPI,
    APIRouter,
    HTTPException,
    Request,
    Depends,
    File,
    UploadFile,
    Query,
    Body,
)
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional, Union, List

from . import APIConstants
from . import APIExceptions
from . import APIAuth
from . import APIFiles
from . import APIGlobals

from ..core import (aNyanData, aNyanConstants,
aNyanController,aNyanDB,aNyanExceptions,aNyanGlobals,aNyanLogging,aNyanPaths,aNyanPubSub,aNyanTemp,aNyanThreading)


class Routing(APIRouter):

    def __init__(self, controller: aNyanController.Nyan_Controller) -> None:
        
        APIRouter.__init__(self)
        
        self.controller = controller


class Default_Routing(Routing):
    def __init__(self, controller: aNyanController.Nyan_Controller):

        Routing.__init__(self, controller)

        self.add_api_route("/heartbeat", self.heartbeat, methods=["GET", "HEAD"])
        self.add_api_route("/", self.heartbeat, methods=["GET", "HEAD"])

    async def heartbeat(self, request: Request):

        return {"nyaa~": "OwO", "-w-": "^w^", ";3c": "OwU"}


class Search_Routing(Routing):
    def __init__(self, controller: aNyanController.Nyan_Controller):

        Routing.__init__(self, controller)

        self.add_api_route("/search/get_file_tags", self.search_tags, methods=["GET"])
        self.add_api_route("/search/get_categories", self.search_categories, methods=["GET"])
        self.add_api_route("/search/get_files", self.search_files, methods=["GET"])
        self.add_api_route("/search/get_videos", self.search_videos, methods=["GET"])

        self.last_cache_reload = aNyanData.time_now()
        self.video_search_cache = set()

    async def search_videos(self, request: Request):

        if not os.path.isdir(APIConstants.STATIC_VIDEO_PATH):
            return APIExceptions.API_500_OSERROR

        if len(self.video_search_cache) == 0 or aNyanData.time_has_passed(self.last_cache_reload + 60):

            self.last_cache_reload = aNyanData.time_now()

            for file in os.listdir(APIConstants.STATIC_VIDEO_PATH):

                ext = aNyanData.get_file_extension(file)

                mime = aNyanConstants.EXT_MIME_LOOKUP.get(ext, None)

                if not mime:
                    continue

                if mime in aNyanConstants.VIDEO_MIMES:

                    self.video_search_cache.add(APIConstants.SERVER_ADDRESS + "static/v/" + file)

        return self.video_search_cache

    async def search_tags(self, request: Request, fid: List[int] = Query(None), fh: List[str] = Query(None)):

        raise APIExceptions.API_404_USER_NOT_FOUND_EXCEPTION

    async def search_categories(self, request: Request):

        raise APIExceptions.API_404_USER_NOT_FOUND_EXCEPTION

    async def search_files(
        self,
        request: Request,
        sort_t: int = 4,
        sort_a: bool = False,
        fid: List[int] = Query(None),  # hash id
        tid: List[int] = Query(None),  # tag id
        nid: List[int] = Query(None),  # namespace id
        sid: List[int] = Query(None),  # subtag id
    ):

        raise APIExceptions.API_404_USER_NOT_FOUND_EXCEPTION


class Static_Routing(Routing):
    def __init__(self, controller: aNyanController.Nyan_Controller):

        Routing.__init__(self, controller)

        self.add_api_route("/static/{category}/{path}", self.staticv1, methods=["HEAD", "GET"])
        self.add_api_route("/favicon.ico", self.favicon, methods=["HEAD", "GET"])

    async def favicon(self, request: Request):

        pass
        # if os.path.isfile(constants_.STATIC_FAVICON_PATH):
        #     return FileResponse(constants_.STATIC_FAVICON_PATH)

        # raise exceptions.API_404_NOT_FOUND_EXCEPTION

    async def staticv1(self, request: Request, category: str, path: str):

        callback = {
            "v": APIFiles.stream_video,
            "i": APIFiles.get_image,
            "t": APIFiles.get_thumbnail,
        }.get(category, None)

        if callback:

            return callback(request, path)


class Auth_Routing(Routing):
    def __init__(self, controller: aNyanController.Nyan_Controller):

        Routing.__init__(self, controller)

        self.add_api_route("/create/user", self.register_user, methods=["POST"])
        self.add_api_route("/auth/token", self.login, methods=["POST"])

    async def register_user(self, request: Request, data: OAuth2PasswordRequestForm = Depends()):

        raise APIExceptions.API_404_USER_NOT_FOUND_EXCEPTION

    async def login(self, request: Request, data: OAuth2PasswordRequestForm = Depends()):

        raise APIExceptions.API_404_USER_NOT_FOUND_EXCEPTION
        username = data.username
        password = data.password

        user = APIAuth.load_user(username)

        if not user:
            raise APIExceptions.API_401_CREDENTIALS_EXCEPTION

        if not APIAuth.verify_password(password, user.hashed_password):
            raise APIExceptions.API_401_CREDENTIALS_EXCEPTION

        access_token = APIAuth.manager.create_access_token(
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
