
import hashlib
import bcrypt
import base64
import os 

from fastapi_login import LoginManager


from .constants_ import SALT_ROUNDS, SALT_PREFIX, PEPPER, SECRET
from . import database
from . import models

manager = LoginManager(SECRET, token_url='/auth/token')


def verify_password(password : str, hashed_password : str, *, pepper : str = PEPPER) -> bool:
    """ validates if the given password is a match for the given hash, returns bool """
    if isinstance(password, str):
        password = password.encode()

    if isinstance(pepper, str):
        pepper = pepper.encode()

    password = password + pepper

    return bcrypt.checkpw(
                base64.b64encode(
                    hashlib.sha256(
                        password).digest()), 
                hashed_password.encode())


def get_password_hash(password : str, salt : str, *, pepper : str = PEPPER) -> str:
    """ returns a hashed password as a str """

    if isinstance(password, str):
        password = password.encode()

    if isinstance(pepper, str):
        pepper = pepper.encode()

    if isinstance(salt, str):
        salt = salt.encode()

    password = password + pepper

    return bcrypt.hashpw(
                # work around for 72 character length limit
                base64.b64encode(
                    hashlib.sha256(
                        password).digest()),

                salt
                ).decode()


def get_salt(*, rounds : int = SALT_ROUNDS, prefix : bytes = SALT_PREFIX) -> bytes:
    """ generates a salt with the given rounds and prefix, returns bytes """
    
    return bcrypt.gensalt(rounds, prefix)


@manager.user_loader()
def load_user(username : str)  -> models.UserAuthIn:

    user = database.Methods.get_user(username)

    if not user:
        return None

    return user 

def authenticate_user(username : str, password : str) -> models.UserAuthIn:
    """ authenticates if the given login is a valid user """

    user = database.Methods.get_user(username)

    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None

    return user



if __name__ == "__main__":

    password = "hello world"
    salt = get_salt()

    hash = get_password_hash(password, salt)

    print(password)
    print(hash)