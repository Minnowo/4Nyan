


from . import Session
from .tables_postgres import *

from .. import models

from .. import exceptions
from .. import auth
from .. import constants_
from ..reg import HAS_INVALID_PASSWORD_CHARACTERS, HAS_INVALID_USERNAME_CHARACTERS

from datetime import datetime 


# User ---------------------------------------------------


def create_user(user : models.UserIn) -> dict:
    """ creates a user in the database, returns a dict with the user info """

    username_length = len(user.username)
    password_length = len(user.password)

    if username_length < constants_.MIN_USERNAME_LEGNTH or \
       username_length > constants_.MAX_USERNAME_LENGTH or \
       HAS_INVALID_USERNAME_CHARACTERS.search(user.username):
        raise exceptions.API_406_USERNAME_EXCEPTION

    if password_length < constants_.MIN_PASSWORD_LENGTH or \
       password_length > constants_.MAX_PASSWORD_LENGTH or \
       HAS_INVALID_PASSWORD_CHARACTERS.search(user.password):
        raise exceptions.API_406_PASSWORD_EXCEPTION
    
    # pain. this makes intelisense break even tho it's the same as the Session class 
    with Session.begin() as session:
       
        result = session.query(TBL_Users).filter_by(username = user.username).first()
        
        if (result):
            raise exceptions.API_409_USERNAME_CONFLICT_EXCEPTION
        

        new_user = TBL_Users(
                             username        = user.username,
                             hashed_password = auth.get_password_hash(user.password, auth.get_salt()),
                             
                             # doing this here because database will scream if it's not 'astimezone'
                             # so not gonna trust myself later to pass the correct class
                             created_at      = datetime.now().astimezone()
                        ) 

        session.add(new_user)

        # not sure why i can't remove this and have the return outside the with statement
        # i'm guessing it destroys the new_user object above, that or it was a scope issue last i tried
        # but this commits to the database so good enough
        session.flush()        
        
        return {
            "user_id"    : new_user.user_id,
            "username"   : new_user.username,
            "created_at" : new_user.created_at
        }


def get_user(username : str) -> models.UserAuthIn:
    """ gets a user from the database, returns a UserAuthIn or None """

    with Session.begin() as session:

        result = session.query(TBL_Users).filter_by(username = username).first()

        if not result:
            return None 

        return models.UserAuthIn(
                user_id         = result.user_id,
                username        = result.username,
                create_at       = result.created_at,
                hashed_password = result.hashed_password
            )


def get_file_by_hash(hash : bytes) ->models.File:

    with Session.begin() as session:

        result = session.query(TBL_Hash).filter_by(hash = hash).first()

        if not result:
            return None 

        return models.File(
                hash_id   = result.hash_id,
                hash      = result.hash,
                size      = result.size,
                mime      = result.mime,
                width     = result.width,
                height    = result.height,
                duration  = result.duration,
                num_words = result.num_words,
                has_audio = result.has_audio
            )

def get_file_by_id(hash_id : int) -> models.File:

    with Session.begin() as session:

        result = session.query(TBL_Hash).filter_by(hash_id = hash_id).first()

        if not result:
            return None 

        return models.File(
                hash_id   = result.hash_id,
                hash      = result.hash,
                size      = result.size,
                mime      = result.mime,
                width     = result.width,
                height    = result.height,
                duration  = result.duration,
                num_words = result.num_words,
                has_audio = result.has_audio
            )


def add_file(file : models.File):

    # pain. this makes intelisense break even tho it's the same as the Session class 
    with Session.begin() as session:
       
        result = session.query(TBL_Hash).filter_by(hash = file.hash).first()
        
        if (result):
            raise exceptions.API_500_FILE_EXISTS_EXCEPTION 
        
        new_file = TBL_Hash(
                            hash      = file.hash,
                            size      = file.size,
                            mime      = file.mime,
                            width     = file.width,
                            height    = file.height,
                            duration  = file.duration,
                            num_words = file.num_words,
                            has_audio = file.has_audio
                        ) 
        
        session.add(new_file)
        
        # not sure why i can't remove this and have the return outside the with statement
        # i'm guessing it destroys the new_user object above, that or it was a scope issue last i tried
        # but this commits to the database so good enough
        session.flush()        
        
        return {
            "hash_id"   : new_file.hash_id,
            "hash"      : new_file.hash,
            "size"      : new_file.size,
            "mime"      : new_file.mime,
            "width"     : new_file.width,
            "height"    : new_file.height,
            "duration"  : new_file.duration,
            "num_words" : new_file.num_words,
            "has_audio" : new_file.has_audio
        }