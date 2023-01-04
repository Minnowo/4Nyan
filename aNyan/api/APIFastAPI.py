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
