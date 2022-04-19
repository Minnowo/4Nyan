from pydantic import BaseModel
from datetime import datetime

######## Auth ########


class Token(BaseModel):
    access_token: str
    token_type  : str


class TokenData(BaseModel):
    username: str = None


class File(BaseModel):
    hash_id   : int = None
    hash      : bytes
    size      : int
    mime      : int
    width     : int  
    height    : int  
    duration  : int  
    num_words : int 
    has_audio : bool

######## User ########

class User(BaseModel):
    user_id   : int = None
    username  : str
    create_at : datetime = None


class UserIn(User):
    password: str


class UserAuthIn(User):
    hashed_password: str


class Login(BaseModel):
    username : str 
    password : str 


class AccessToken(BaseModel):
    token : bytes 
    token_type : str 