import os
import logging

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


from ..core import aNyanController, aNyanLogging as logging, aNyanData


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
    def __init__(self, name: str, controller: aNyanController.Nyan_Controller) -> None:

        APIRouter.__init__(self)

        self.name_unique = f"{name} created at {aNyanData.time_now()}"

        self.name = name

        self.controller = controller

        logging.info(f"Creating APIRouter with name: {name}")

    def __hash__(self) -> int:
        return self.name_unique.__hash__()
