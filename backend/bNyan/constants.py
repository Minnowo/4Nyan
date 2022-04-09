import os 


######## Pathing and API ########

MAX_IMG_PATH_LENGTH = 100
MIN_IMG_PATH_LENGTH = 3

FFMPEG_PATH = ""
FFPROBE_PATH = ""

STATIC_IMAGES_PATH = "/static/images/"
APP_ROOT = "./"




######## Datebase ########

DB_USER = "minno"
DB_KEY = "strongpassword"
DB_PORT = "720"
DB_DB = "4Nyan-DB"
DB_URL = "postgresql://{}:{}@localhost:{}/{}".format(DB_USER, DB_KEY, DB_PORT, DB_DB)


######## Passwords / User ########

MAX_USERNAME_LENGTH = 32 
MIN_USERNAME_LEGNTH = 3

MAX_PASSWORD_LENGTH = 96
MIN_PASSWORD_LENGTH = 10

PEPPER = "UEZ5V_HewsMowePwdLenthUWU__ooZqe"
SALT_ROUNDS = 15
SALT_PREFIX = b"2b" # needs to be 2b or 2a 



######## Other ########

IS_WINDOWS = (os.name == "nt")


RESTRICT_MAP = {
    "auto" : "\\\\|/<>:\"?*" if IS_WINDOWS else "/",
    "unix" : "/",
    "windows" : "\\\\|/<>:\"?*",
    "ascii" : "^0-9A-Za-z_."
}

RESTRICT_MAP_NO_SEP = {
    "auto" : "|<>:\"?*" if IS_WINDOWS else "",
    "unix" : "",
    "windows" : "|<>:\"?*",
    "ascii" : "^0-9A-Za-z_."
}