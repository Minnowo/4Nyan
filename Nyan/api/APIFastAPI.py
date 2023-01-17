import os
import logging
from functools import wraps

from fastapi import (
    FastAPI,
    APIRouter,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from typing import List
from typing import Optional, Union

from . import APIExceptions
from . import APIGlobals
from ..core import NyanController, NyanData, NyanLogging as logging, NyanGlobals


class Nyan_API(FastAPI):
    def __init__(self):

        FastAPI.__init__(self)

        origins = [
            "http://localhost:722",
            "localhost:722",
            "0.0.0.0:722",
        ]

        self.add_middleware(GZipMiddleware)
        self.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


class Nyan_Router(APIRouter):
    def __init__(self, name: str, controller: NyanController.Nyan_Controller) -> None:

        APIRouter.__init__(self)

        self.name_unique = f"{name} created at {NyanData.time_now()}"

        self.name = name

        self.controller = controller

        logging.info(f"Creating APIRouter with name: {name}")

    def __hash__(self) -> int:
        return self.name_unique.__hash__()

    @staticmethod
    def die_if_shutdown_endpoint_wrapper_async(func):
        @wraps(func)
        async def wrapped(*args, **kwargs):

            Nyan_Router.die_if_shutdown()

            return await func(*args, **kwargs)

        return wrapped

    @staticmethod
    def die_if_shutdown_wrapper_async(func):
        async def wrapped(*args, **kwargs):

            Nyan_Router.die_if_shutdown()

            return await func(*args, **kwargs)

        return wrapped

    @staticmethod
    def die_if_shutdown_wrapper(func):
        def wrapped(*args, **kwargs):

            Nyan_Router.die_if_shutdown()

            return func(*args, **kwargs)

        return wrapped

    @staticmethod
    def die_if_shutdown():

        if NyanGlobals.view_shutdown or NyanGlobals.model_shutdown or APIGlobals.shutdown_api:

            raise APIExceptions.API_500_SHUTTING_DOWN_EXCEPTION
