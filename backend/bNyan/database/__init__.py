


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import event

from ..constants_ import DB_URL, DATABASE_FOLDER
from ..util import create_directory


def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('pragma foreign_keys=ON')


create_directory(DATABASE_FOLDER)
Engine = create_engine(DB_URL, echo=False)

event.listen(Engine, 'connect', _fk_pragma_on_connect)

Session = sessionmaker(Engine)

Base = declarative_base(bind=Engine)

# if you wanna swap databases, make a new file and import the tables like this, let sqlalchemy handle it 
# the reason i'm making it easy to swap databases is becauce i really hate pgadmin and am likely to swap to sqlite later
# if the new database needs different methods in the methods.py, i guess you'd have to edit that or make a new file

# from . import tables_postgres
from . import tables_sqlite
from . import methods

# Tables = tables_postgres
Tables = tables_sqlite
Methods = methods

