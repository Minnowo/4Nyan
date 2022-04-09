


# this file is used for the definition of the database tables
# as well as all database related functions (likely will make a folder for all of this in the future) 



from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime 

from . import exceptions 
from . import auth
from . import models
from . import constants
from reg import HAS_INVALID_PASSWORD_CHARACTERS


engine = create_engine(constants.DB_URL, echo=False)

# you have no idea how long it took me to get here,
# wtf is up with the sqlalchemy docs, i'm just bad at reading ig but holy frick
Session = sessionmaker(engine)

Base = declarative_base(bind=engine)

# really glad it's like this now, why? because it works with sessions (so far)
# this is actually really annoying compared to what it was before but this is what 
# you're supposed to do now 
class TBL_Users(Base):
    __tablename__ = "tbl_users"

    user_id         = Column(Integer, primary_key=True)
    username        = Column(String(32))
    hashed_password = Column(String(60))
    created_at      = Column(TIMESTAMP(timezone=True))
    is_admin        = Column(Boolean, default=False)
    disabled        = Column(Boolean, default=False)
    nsfw_allow      = Column(Boolean, default=False)


# User ---------------------------------------------------


def create_user(user : models.UserIn) -> dict:
    """ creates a user in the database, returns a dict with the user info """

    username_length = len(user.username)
    password_length = len(user.password)

    if username_length < constants.MIN_USERNAME_LEGNTH or \
       username_length > constants.MAX_USERNAME_LENGTH:
        raise exceptions.API_406_USERNAME_EXCEPTION

    if password_length < constants.MIN_PASSWORD_LENGTH or \
       password_length > constants.MAX_PASSWORD_LENGTH or \
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










if __name__ == "__main__":

    # fuck relative imports not working when running directly 
    import exceptions 
    import auth
    import models
    import constants

    Base.metadata.create_all()

    u_in = models.UserIn(username="some_user_uwu", password="password123")
    

    create_user(u_in)
    # get_user("mfgfginnowo")
