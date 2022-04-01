import os 

IS_WINDOWS = (os.name == "nt")

MAX_IMG_PATH_LENGTH = 100
MIN_IMG_PATH_LENGTH = 3

FFMPEG_PATH = ""
FFPROBE_PATH = ""

STATIC_IMAGES_PATH = "/static/images/"
APP_ROOT = "./"

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