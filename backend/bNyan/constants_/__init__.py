import os 

from .file_headers import *
from .mime_types import *
from . import status_codes # why do i need to put this here to use constants_.status_codes


BYTE = 1
KILOBYTE = BYTE     * 1024
MEGABYTE = KILOBYTE * 1024
GIGABYTE = MEGABYTE * 1024

VIDEO_STREAM_CHUNK_SIZE = MEGABYTE * 8
IMAGE_UPLOAD_CHUNK_SIZE = KILOBYTE * 500

# in seconds 
TS_FILE_DURATION        = 10

######## Pathing and API ########

MAX_IMG_PATH_LENGTH = 100
MIN_IMG_PATH_LENGTH = 3


STATIC_IMAGE_PATH = os.path.join("static", "i")
STATIC_VIDEO_PATH = os.path.join("static", "v")
STATIC_M3U8_PATH  = os.path.join("static", "m3u8")
STATIC_TEMP_PATH  = os.path.join("static", "tmp")
STATIC_AUDIO_PATH = os.path.join("static", "a")
STATIC_LOG_PATH = os.path.join("static", "logs")

DATABASE_FOLDER = os.path.join("db")
DATABASE_PATH = os.path.join(DATABASE_FOLDER, "master.data.db")

BIN_FOLDER = os.path.join("bin")

FFMPEG_PATH  = os.path.join(BIN_FOLDER, "ffmpeg.exe")
FFPROBE_PATH = os.path.join(BIN_FOLDER, "ffprobe.exe")


APP_ROOT = "./"


NULL_CHARACTER = '\x00'
UNICODE_REPLACEMENT_CHARACTER = u'\ufffd'

######## Loggers ########

BNYAN_MAIN    = ("BNMain"   , os.path.join("static", "logs", "BNMain.log"))
BNYAN_METHODS = ("BNMethods", os.path.join("static", "logs", "BNMethods.log"))


######## Datebase ########

DB_USER = "minno"
DB_KEY = "strongpassword"
DB_PORT = "720"
DB_DB = "4Nyan-DB"
DB_URL = "postgresql://{}:{}@localhost:{}/{}".format(DB_USER, DB_KEY, DB_PORT, DB_DB)

DB_URL = "sqlite:///{}".format(DATABASE_PATH)


######## Passwords / User ########

MAX_USERNAME_LENGTH = 32 
MIN_USERNAME_LEGNTH = 4

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




mime_ext_lookup = {
    APPLICATION_UNKNOWN : "unknown",

    APPLICATION_PDF : ".pdf",

    IMAGE_JPEG : '.jpg',
    IMAGE_PNG  : '.png',
    IMAGE_GIF  : '.gif',
    IMAGE_BMP  : '.bmp',
    IMAGE_WEBP : '.webp',
    IMAGE_TIFF : '.tiff',
    IMAGE_ICON : '.ico',

    AUDIO_M4A  : '.m4a',
    AUDIO_MP3  : '.mp3',
    AUDIO_MKV  : '.mkv',
    AUDIO_MP4  : '.mp4',
    AUDIO_OGG  : '.ogg',
    AUDIO_FLAC : '.flac',
    AUDIO_WAVE : '.wav',
    AUDIO_WMA  : '.wma',

    VIDEO_AVI  : '.avi',
    VIDEO_FLV  : '.flv',
    VIDEO_MOV  : '.mov',
    VIDEO_MP4  : '.mp4',
    VIDEO_MPEG : '.mpeg',
    VIDEO_WMV  : '.wmv',
    VIDEO_MKV  : '.mkv',
    VIDEO_OGV  : '.ogv',
    VIDEO_WEBM : '.webm',
}

# mime_header_lookup = {
#     IMAGE_JPEG : JPEG_HEADER,
#     IMAGE_PNG  : PNG_HEADER,
#     IMAGE_GIF  : GIF_HEADER,
#     IMAGE_BMP  : BMP_HEADER,
#     IMAGE_WEBP : WEBP_HEADER,
#     IMAGE_TIFF : TIFF_HEADER,

#     # AUDIO_M4A : '.m4a',
#     # AUDIO_MP3 : '.mp3',
#     # AUDIO_MKV : '.mkv',
#     # AUDIO_MP4 : '.mp4',
#     # AUDIO_OGG : '.ogg',
#     # AUDIO_FLAC : '.flac',
#     # AUDIO_WAVE : '.wav',
#     # AUDIO_WMA : '.wma',

#     # VIDEO_AVI : '.avi',
#     # VIDEO_FLV : '.flv',
#     # VIDEO_MOV : '.mov',
#     # VIDEO_MP4 : '.mp4',
#     # VIDEO_MPEG : '.mpeg',
#     # VIDEO_WMV : '.wmv',
#     # VIDEO_MKV : '.mkv',
#     # VIDEO_OGV : '.ogv',
#     # VIDEO_WEBM : '.webm',
# }


headers_and_mime = [
    ( IMAGE_JPEG_HEADERS, IMAGE_JPEG       ),
    ( IMAGE_PNG_HEADER  , IMAGE_PNG        ),
    ( IMAGE_GIF_HEADERS , IMAGE_GIF        ),
    ( IMAGE_WEBP_HEADER , IMAGE_WEBP       ),
    ( UNDETERMINED_VIDEO_MP4_HEADERS , UNDETERMINED_MP4 ),
    ( VIDEO_MKV_HEADERS , VIDEO_MKV        ),
    ( VIDEO_MOV_HEADERS , VIDEO_MOV        ),

    ( PDF_HEADER        , APPLICATION_PDF  ),

    ( IMAGE_TIFF_HEADERS, IMAGE_TIFF       ),
    ( IMAGE_ICO_HEADERS , IMAGE_ICON       ),

    ( AUDIO_FLAC_HEADERS, AUDIO_FLAC       ),
    ( AUDIO_WAVE_HEADERS, AUDIO_WAVE       ),

    ( IMAGE_BMP_HEADER  , IMAGE_BMP        ),

    ( VIDEO_FLV_HEADER  , VIDEO_FLV        ),
    ( VIDEO_AVI_HEADERS , VIDEO_AVI        ),

    ( UNDETERMINED_VIDEO_WM_HEADERS , UNDETERMINED_VIDEO_WM ),
] 