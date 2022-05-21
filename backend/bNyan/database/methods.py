


from . import Session
# from .tables_postgres import *
from .tables_sqlite import *

from .. import models
from .. import exceptions
from .. import auth
from .. import constants_
from .. import bn_logging
from ..reg import HAS_INVALID_PASSWORD_CHARACTERS, HAS_INVALID_USERNAME_CHARACTERS, TAG

from datetime import datetime 

from sqlalchemy import select, and_, or_
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
import sqlite3 
# https://docs.sqlalchemy.org/en/14/orm/session_basics.html


# because auto increment issues with tag because it's not a primary key 
class auto_inc_cache():
    
    __tag_id_cache = 1 


namespace_map = {
    "category" : -1
}


LOGGER = bn_logging.get_logger(constants_.BNYAN_DB_METHODS[0], constants_.BNYAN_DB_METHODS[1])

# User ---------------------------------------------------

def add_defaults():

    with Session.begin() as session:

        result1 = session.query(TBL_Namespace).filter_by(namespace_id = 1).first()
        result2 = session.query(TBL_Namespace).filter_by(namespace = "category").first()
        
        if not result1:
            session.add(TBL_Namespace(namespace_id=1, namespace = ""))
            session.flush()

        if not result2:
            result2 = TBL_Namespace(namespace = "category")

            session.add(result2)
            session.flush()

        namespace_map["category"] = result2.namespace_id
        
        result3 = session.query(session.query(func.max(TBL_Tags.tag_id)).scalar()).first()

        # since TBL_Tags.tag_id is not a primary key idk how to auto increment it, so we're caching here
        # and we will use this value when adding to the db 
        if result3:
            
            if result3[0] is None:

                auto_inc_cache.__tag_id_cache = 1

            else:

                auto_inc_cache.__tag_id_cache = result3[0] + 1

        



def create_user(user : models.UserIn) -> models.User:
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
        
        return models.User(
                user_id         = new_user.user_id,
                username        = new_user.username,
                create_at       = new_user.created_at
            )


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

def file_hash_exists(hash : bytes) -> bool:

    with Session.begin() as session:

        result = session.query(TBL_Hash).filter_by(hash = hash).first()

        if not result:
            return False 

        return True 

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
                has_audio = result.has_audio,
                date_added = result.date_added
            )

def get_file_by_id(hash_id : int) -> models.File:

    with Session.begin() as session:

        result = session.query(TBL_Hash).filter_by(hash_id = hash_id).first()

        if not result:
            return None 

        return models.File(
                hash_id    = result.hash_id,
                hash       = result.hash,
                size       = result.size,
                mime       = result.mime,
                width      = result.width,
                height     = result.height,
                duration   = result.duration,
                has_audio  = result.has_audio,
                date_added = result.date_added
            )


def create_tag(tag_ : str):

    t = TAG.match(tag_)

    if not t:
        raise exceptions.API_400_BAD_REQUEST_EXCEPTION

    namespace_ = t.group("namespace") or ""
    tag        = t.group("tag")

    with Session.begin() as session:

        flag1 = True 

        result1 = session.query(TBL_Subtag).filter_by(subtag = tag).first()
        
        if not result1:
            
            result1 = TBL_Subtag(subtag = tag) 
            session.add(result1)
            session.flush()
            
            flag1 = False 

            
        flag2 = True  

        result2 = session.query(TBL_Namespace).filter_by(namespace = namespace_).first()
        
        if not result2:

            result2 = TBL_Namespace(namespace = namespace_)
            session.add(result2)
            session.flush()

            flag2 = False  

        # avoid getting an error trying to add a tag 
        # if both the subtag and namespace already exist, just search for a tag
        if flag1 and flag2:

            result3 = session.query(TBL_Tags) \
                .filter_by(subtag_id = result1.subtag_id) \
                .filter_by(namespace_id = result2.namespace_id).first()

            if result3:
                return models.Tag(
                    tag_id       = result3.tag_id,
                    subtag_id    = result3.subtag_id,
                    namespace_id = result3.namespace_id,
                    tag          = tag,
                    namespace    = namespace_
                    )


        new_tag = TBL_Tags(
            tag_id       = auto_inc_cache.__tag_id_cache,
            subtag_id    = result1.subtag_id,
            namespace_id = result2.namespace_id,
        )

        try:
            session.add(new_tag)
            session.flush()
            
            auto_inc_cache.__tag_id_cache += 1

        except (IntegrityError, sqlite3.IntegrityError) as e:
            
            LOGGER.warning(e)
            raise exceptions.API_409_TAG_CREATION_EXCEPTION

        return models.Tag(
            tag_id       = new_tag.tag_id,
            subtag_id    = new_tag.subtag_id,
            namespace_id = new_tag.namespace_id,
            tag          = tag,
            namespace    = namespace_
            )


def get_categories():

    with Session.begin() as session:

        cat_id = namespace_map["category"]

        if cat_id == -1:

            result1 = session.query(TBL_Namespace).filter_by(namespace = "category").first()
        
            if not result1:
            
                result1 = TBL_Namespace(namespace = "category") 

                session.add(result1)

                namespace_map["category"] = result1.namespace_id

            
            cat_id = result1.namespace_id

        
        result = session.query(TBL_Tags, TBL_Subtag, TBL_Namespace) \
            .join(TBL_Namespace) \
            .join(TBL_Subtag) \
            .filter(TBL_Tags.namespace_id == cat_id)

        for r in result.all():
            
            tag = r[0]
            sub = r[1]
            nam = r[2]

            yield models.Tag(
                tag_id       = tag.tag_id,
                namespace_id = nam.namespace_id,
                subtag_id    = sub.subtag_id,
                namespace    = nam.namespace,
                tag          = sub.subtag
            )
            



def get_file_tags_from_hash(hash : bytes):

    raise exceptions.API_500_NOT_IMPLEMENTED

def get_file_tags_from_id(file_id : int ):

    with Session.begin() as session:

        result = session.query(TBL_Tags, TBL_Subtag, TBL_Namespace) \
            .join(TBL_Tag_Map) \
            .filter_by(hash_id = file_id) \
            .join(TBL_Subtag) \
            .join(TBL_Namespace) 

        for r in result.all():

            tag = r[0]
            sub = r[1]
            nam = r[2]

            yield models.Tag(
                tag_id = tag.tag_id,
                namespace_id = nam.namespace_id,
                subtag_id = sub.subtag_id,
                namespace = nam.namespace,
                tag = sub.subtag
            )



def remove_file(hash : bytes):
    """ removes the file from the database, returns True if the file is not found or removed """
    with Session.begin() as session:

        result = session.query(TBL_Hash).filter_by(hash = hash).first()
        
        if not result:
            return True 

        session.delete(result)
        session.commit()

        return True 


def add_file(file : models.File) -> None:
    """ adds a file to the database and sets the hash_id in the given file object """

    # pain. this makes intelisense break even tho it's the same as the Session class 
    with Session.begin() as session:
       
        result = session.query(TBL_Hash).filter_by(hash = file.hash).first()
        
        if result:
            raise exceptions.API_409_FILE_EXISTS_EXCEPTION 
        
        new_file = TBL_Hash(
                            hash       = file.hash,
                            size       = file.size,
                            mime       = file.mime,
                            width      = file.width,
                            height     = file.height,
                            duration   = file.duration,
                            has_audio  = file.has_audio,
                            date_added = datetime.now().astimezone()
                        ) 
        
        session.add(new_file)
        
        # not sure why i can't remove this and have the return outside the with statement
        # i'm guessing it destroys the new_user object above, that or it was a scope issue last i tried
        # but this commits to the database so good enough
        session.flush()        
        
        file.hash_id = new_file.hash_id



def add_tag_to_file(ftmap : models.Tag_File):

    with Session.begin() as session:
       
        new_map = TBL_Tag_Map(
            hash_id = ftmap.file_id,
            tag_id = ftmap.tag_id
        )

        try:
            session.add(new_map)
            session.flush()

        except IntegrityError as e:

            LOGGER.warning(e)
            raise exceptions.API_409_TAG_CREATION_EXCEPTION

        except Exception as e:
            LOGGER.error(type(e))
            LOGGER.error(e)



sort_by_map = [ 
    TBL_Hash.hash_id,
    TBL_Hash.hash,
    TBL_Hash.size,
    TBL_Hash.mime,
    TBL_Hash.date_added,
    TBL_Hash.width,
    TBL_Hash.height,
    TBL_Hash.duration
]

def search_files(search : models.FileSearch):
    """ searches the database with the given params """

    with Session.begin() as session:
       
        result = session.query(TBL_Hash)#.join(TBL_Tags)

        if search.hash_ids:

            result = result.filter(TBL_Hash.hash_id.in_(search.hash_ids))

        if search.hashes:

            result = result.filter(TBL_Hash.hash.in_(search.hashes))

        if search.tag_ids:

            result = result.join(TBL_Tag_Map).filter(TBL_Tag_Map.tag_id.in_(search.tag_ids))

        if search.sort_asc:

            # % prevents index err
            order = sort_by_map[search.sort_type % len(sort_by_map)].asc()
        
        else:

            order = sort_by_map[search.sort_type % len(sort_by_map)].desc()

        for r in result.order_by(order).all():

            yield models.File_Response(
                hash_id    = r.hash_id,
                hash       = r.hash,
                size       = r.size,
                mime       = r.mime,
                width      = r.width,
                height     = r.height,
                duration   = r.duration,
                has_audio  = r.has_audio,
                date_added = r.date_added
            )