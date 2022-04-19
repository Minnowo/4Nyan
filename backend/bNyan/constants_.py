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
SALT_ROUNDS = 14
SALT_PREFIX = b"2b" # needs to be 2b or 2a 

SECRET = "9ffd8b7c514f2009eaf299f3df6dcc76a788c9518941db4dd077656b92996bf3"


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



# enums here (idk if the numbers are random, 
# i took this from https://github.com/hydrusnetwork/hydrus/blob/b927c938914a7c71a7fa693e7e640039b324e971/hydrus/core/HydrusConstants.py#L496)

# image 
IMAGE_JPEG = 1
IMAGE_PNG = 2
IMAGE_GIF = 3
IMAGE_BMP = 4
IMAGE_ICON = 7
IMAGE_APNG = 23
IMAGE_WEBP = 33
IMAGE_TIFF = 34

# audio
AUDIO_MP3 = 13
AUDIO_OGG = 15
AUDIO_FLAC = 16
AUDIO_WMA = 17
AUDIO_M4A = 36
AUDIO_WAVE = 46
AUDIO_MKV = 48
AUDIO_MP4 = 49

# video
VIDEO_FLV = 9
VIDEO_MP4 = 14
VIDEO_WMV = 18
VIDEO_MKV = 20
VIDEO_WEBM = 21
VIDEO_MPEG = 25
VIDEO_MOV = 26
VIDEO_AVI = 27
VIDEO_OGV = 47

mime_ext_lookup = {
    IMAGE_JPEG : '.jpg',
    IMAGE_PNG : '.png',
    IMAGE_APNG : '.png',
    IMAGE_GIF : '.gif',
    IMAGE_BMP : '.bmp',
    IMAGE_WEBP : '.webp',
    IMAGE_TIFF : '.tiff',
    IMAGE_ICON : '.ico',

    AUDIO_M4A : '.m4a',
    AUDIO_MP3 : '.mp3',
    AUDIO_MKV : '.mkv',
    AUDIO_MP4 : '.mp4',
    AUDIO_OGG : '.ogg',
    AUDIO_FLAC : '.flac',
    AUDIO_WAVE : '.wav',
    AUDIO_WMA : '.wma',

    VIDEO_AVI : '.avi',
    VIDEO_FLV : '.flv',
    VIDEO_MOV : '.mov',
    VIDEO_MP4 : '.mp4',
    VIDEO_MPEG : '.mpeg',
    VIDEO_WMV : '.wmv',
    VIDEO_MKV : '.mkv',
    VIDEO_OGV : '.ogv',
    VIDEO_WEBM : '.webm',
}