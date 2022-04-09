from pydantic import BaseModel
from datetime import datetime

######## Auth ########


class Token(BaseModel):
    access_token: str
    token_type  : str


class TokenData(BaseModel):
    username: str = None





######## User ########

class User(BaseModel):
    user_id   : int = None
    username  : str
    create_at : datetime = None


class UserIn(User):
    password: str


class UserAuthIn(User):
    hashed_password: str
