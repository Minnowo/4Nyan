from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Union, Tuple
from fastapi import Query

######## Auth ########


class Token(BaseModel):
    access_token: str
    token_type: str


class Token_Data(BaseModel):
    username: str = None


######## Files ########


class File(BaseModel):
    hash_id: int = None
    hash: Union[bytes, str]
    size: int
    mime: int
    width: int
    height: int
    duration: int
    has_audio: bool
    date_added: datetime = None


class File_Response(File):

    static_url: dict = None


class File_Search(BaseModel):

    sort_asc: bool = True
    sort_type: int = 0

    hash_ids: List[int] = None
    hashes: List[str] = None

    tag_names: List[str] = None
    tag_ids: List[int] = None

    namespace_ids: List[int] = None
    subtag_ids: List[int] = None


class Tag(BaseModel):

    tag_id: int = None
    namespace_id: int = None
    subtag_id: int = None
    namespace: str = None
    tag: str


class Tag_File(BaseModel):

    file_id: int
    tag_id: int


######## User ########


class User(BaseModel):
    user_id: int = None
    username: str
    create_at: datetime = None


class User_In(User):
    password: str


class User_Auth_In(User):
    hashed_password: str


class Login(BaseModel):
    username: str
    password: str


class Access_Token(BaseModel):
    token: bytes
    token_type: str
