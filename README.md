

## 4Nyan
A LAN site meant to stream video, audio, text, and images from a local server over LAN.


*This is very early in development and currently very unusable (unless you want to only stream video using mpv)*

### Current Features

- HLS (http live streaming) of video using m3u8 files
- Image serving endpoint
- Basic database layout
- Very bare bones frontend used to test the HLS

### Plans for the future

- Youtube-like UI for video streaming
- Danbooru-like gallery of randomly tagged images 
- nHentai-like manga / book reader 
- Serving books as PDF or HTML
- Audio *eventually*

## Frontend 
The frontend is built using [Reactjs](https://reactjs.org/), with [Bootstrap](https://getbootstrap.com/docs/5.1/getting-started/download/) for css. 

## Backend
The backend is built using [FastAPI](https://fastapi.tiangolo.com/), using Python [3.7.6](https://www.python.org/downloads/release/python-376/) (I'm assuming anything 3.7+ will work just fine).

## Database
I plan to make it easy to swap databases because I have yet to choose any specific one. I am using the [sqlalchemy](https://github.com/sqlalchemy/sqlalchemy) ORM to handle database connections and management, so hopefully it will be easy to design in a way that it is almost hot-swapable. I am currently using [Postgres](https://www.postgresql.org) but this may change to [SQLite](https://sqlite.org/index.html) or [MySQL](https://www.mysql.com/).

### Postgres Setup 

I'm using the portable installation from [postgresql.org](https://www.postgresql.org/download/) -> [zip archive](https://www.enterprisedb.com/download-postgresql-binaries). Extract the subfolders from **pgsql** into **backend/postgres/**. Then run [init_db.bat](setup/init_db.bat) which should set the data directory to **backend/postgres/bin/data**, after this run [start_postgres_server.bat](setup/start_postgres_server.bat) to begin running the server.

Then run pgadmin, and create a new server called **4Nyan-DB**. Set the hostname to localhost, the port to the same port as the value in **backend/postgres/bin/data/postgresql.conf** (change it if you want). I had to set the username to my windows username / the same value used in [constants.py](backend/bNyan/constants.py).

After making the server in pgadmin, create a new database called **4Nyan-DB** (same as server name). Since i'm using windows, I had to set the encoding to WIN1252.

After that the database is pretty much setup unless I forgot something.

(I need to make the setup scripts handle making the server and stuff because PGAdmin is really really terrible and I hate using it)






