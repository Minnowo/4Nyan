import os 

IS_WINDOWS = (os.name == "nt")

MAX_IMG_PATH_LENGTH = 100
MIN_IMG_PATH_LENGTH = 3

FFMPEG_PATH = ""
FFPROBE_PATH = ""

STATIC_IMAGES_PATH = "/static/images/"
APP_ROOT = "./"

DB_USER = "postgres"
DB_KEY = "strongpassword"
DB_SERVER = ""
DB_PORT = "8888"
DB_DB = "fast-stack"
DB_URL = "postgresql://{}:{}@localhost:{}/{}".format(DB_USER, DB_KEY, DB_PORT, DB_DB)

RESTRICT_MAP = {
    "auto" : "\\\\|/<>:\"?*" if IS_WINDOWS else "/",
    "unix" : "/",
    "windows" : "\\\\|/<>:\"?*",
    "ascii" : "^0-9A-Za-z_."
}

SECRET_KEY = "oHWeO+y4pT9LO/4e7a1GBzBfG9Qa1A20J22zB4cB4KFxF6UFJWldjwRW16jbTzOCDbyiLAwM57ufcw4h/eTXwQ"

# TODO once docker is installed, run this command:
# docker run --name fast-stack-db -e POSTGRES_PASSWORD=strongpassword -p 8888:5432 --user postgres -d postgres
# then in docker desktop, open a terminal type in "psql", then " CREATE DATABASE fast-stack; "
# then run "  CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; "