

# this is where sqlalchemy table classes are defined for sqlite, i'm like pretty sure this is the same as postgres, which is kinda nice

from . import Base 
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, LargeBinary, BigInteger, VARCHAR, ForeignKey


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


