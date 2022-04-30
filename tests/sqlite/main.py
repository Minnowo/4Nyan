

from email.mime import base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, LargeBinary, BigInteger, VARCHAR, ForeignKey


Engine = create_engine("sqlite:///sample.db", echo=False)

Session = sessionmaker(Engine)

Base = declarative_base(bind=Engine)

class TBL_Users(Base):
    __tablename__ = "tbl_users"

    user_id         = Column(Integer, primary_key=True)
    username        = Column(String(32))
    hashed_password = Column(String(60))
    created_at      = Column(TIMESTAMP(timezone=True))
    is_admin        = Column(Boolean, default=False)
    disabled        = Column(Boolean, default=False)
    nsfw_allow      = Column(Boolean, default=False)


class TBL_Hash(Base):
    __tablename__ = "tbl_hash"

    hash_id = Column(Integer, primary_key=True)
    hash    = Column(LargeBinary(32), unique=True)
    size      = Column(BigInteger)
    mime      = Column(Integer)
    width     = Column(Integer)
    height    = Column(Integer)
    duration  = Column(Integer)
    num_words = Column(Integer)
    has_audio = Column(Boolean)


class TBL_Tags(Base):
    __tablename__ = "tbl_tags"

    tag_id         = Column(Integer, unique=True)
    namespace_id   = Column(Integer, ForeignKey('tbl_namespace.namespace_id'), primary_key=True)
    subtag_id      = Column(Integer, ForeignKey('tbl_subtag.subtag_id'), primary_key=True)

    
class TBL_Tag_Map(Base):
    __tablename__ = "tbl_tag_map"

    hash_id = Column(Integer, ForeignKey('tbl_hash.hash_id'), primary_key=True)
    tag_id  = Column(Integer, ForeignKey('tbl_tags.tag_id'), primary_key=True)


class TBL_Namespace(Base):
    __tablename__ = "tbl_namespace"

    namespace_id   = Column(Integer, primary_key=True)
    namespace   = Column(VARCHAR(32))


class TBL_Subtag(Base):
    __tablename__ = "tbl_subtag"
    
    subtag_id = Column(Integer, primary_key=True)
    subtag    = Column(VARCHAR(32))


class TBL_Group(Base):
    __tablename__ = "tbl_group"

    group_id    = Column(Integer, primary_key=True)
    name        = Column(VARCHAR(64))
    description = Column(VARCHAR(1024))
    

class TBL_Group_Map(Base):
    __tablename__ = "tbl_group_map"

    group_id   = Column(Integer, ForeignKey('tbl_group.group_id'), primary_key=True)
    hash_id    = Column(Integer, ForeignKey('tbl_hash.hash_id'), primary_key=True)
    item_index = Column(Integer)


class TBL_Rating(Base):
    __tablename__ = "tbl_rating"

    rating_id   = Column(Integer, primary_key=True)
    rating   = Column(VARCHAR(32))


class TBL_Watched(Base):
    __tablename__ = "tbl_watched"

    hash_id     = Column(Integer, ForeignKey('tbl_hash.hash_id'), primary_key=True)
    user_id     = Column(Integer, ForeignKey('tbl_users.user_id'), primary_key=True)
    rating_id   = Column(Integer, ForeignKey('tbl_rating.rating_id'))
    watch_time  = Column(Integer)
    watch_count = Column(Integer)



Base.metadata.create_all()





from pydantic import BaseModel

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


import hashlib

sha = hashlib.sha256()

with open("sample.txt", "rb") as reader:
    sha.update(reader.read())

import os.path
fil = File(hash=sha.digest(), size=os.path.getsize("sample.txt"),mime=0,width=0,height=0,duration=0,num_words=0,has_audio=False)

def add_file(file):

    with Session.begin() as session:
        
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


add_file(fil)