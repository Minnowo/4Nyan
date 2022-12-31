import time
import sys
import os

# this is a useless commit to test gpg key

START_TIME = time.time()

BRAND = "aNyan"


RUNNING_FROM_FROZEN_BUILD = getattr(sys, "frozen", False)

if RUNNING_FROM_FROZEN_BUILD:

    real_exe_path = os.path.realpath(sys.executable)

    BASE_DIR = os.path.dirname(real_exe_path)

else:

    try:

        hc_realpath_dir = os.path.dirname(os.path.realpath(__file__))

        HYDRUS_MODULE_DIR = os.path.split(hc_realpath_dir)[0]

        BASE_DIR = os.path.split(HYDRUS_MODULE_DIR)[0]

    except NameError:  # if __file__ is not defined due to some weird OS

        BASE_DIR = os.path.realpath(sys.path[0])

    if BASE_DIR == "":

        BASE_DIR = os.getcwd()


muh_platform = sys.platform.lower()

PLATFORM_WINDOWS = muh_platform == "win32"
PLATFORM_MACOS = muh_platform == "darwin"
PLATFORM_LINUX = muh_platform == "linux"
PLATFORM_HAIKU = muh_platform == "haiku1"

RUNNING_FROM_SOURCE = sys.argv[0].endswith(".py") or sys.argv[0].endswith(".pyw")
RUNNING_FROM_MACOS_APP = os.path.exists(os.path.join(BASE_DIR, "running_from_app"))

BIN_DIR = os.path.join(BASE_DIR, "bin")
HELP_DIR = os.path.join(BASE_DIR, "help")
INCLUDE_DIR = os.path.join(BASE_DIR, "include")
STATIC_DIR = os.path.join(BASE_DIR, "static")


NULL_CHARACTER = "\x00"
UNICODE_REPLACEMENT_CHARACTER = "\ufffd"

MAINTENANCE_IDLE = 0
MAINTENANCE_SHUTDOWN = 1
MAINTENANCE_FORCED = 2
MAINTENANCE_ACTIVE = 3


# ---- Mime type enums here ----
APPLICATION_UNKNOWN = 0

UNDETERMINED_VIDEO = 50
UNDETERMINED_VIDEO_MP4 = 51
UNDETERMINED_VIDEO_WM = 52
UNDETERMINED_PNG = 53

APPLICATION_PDF = 60
APPLICATION_PSD = 61
APPLICATION_CLIP = 62
APPLICATION_FLASH = 63
APPLICATION_ZIP = 64
APPLICATION_RAR = 65
APPLICATION_7Z = 66
APPLICATION_YAML = 67
APPLICATION_JSON = 68
APPLICATION_CBOR = 69

TEXT_HTML = 80
TEXT_PLAIN = 81

# image
IMAGE_JPEG = 100
IMAGE_PNG = 101
IMAGE_GIF = 102
IMAGE_BMP = 103
IMAGE_ICON = 104
IMAGE_WEBP = 105
IMAGE_TIFF = 106
IMAGE_APNG = 107

# video
VIDEO_FLV = 201
VIDEO_MP4 = 202
VIDEO_WMV = 203
VIDEO_MKV = 204
VIDEO_WEBM = 205
VIDEO_MPEG = 206
VIDEO_MOV = 207
VIDEO_AVI = 208
VIDEO_OGV = 209
VIDEO_REALMEDIA = 210

# audio
AUDIO_MP3 = 301
AUDIO_OGG = 302
AUDIO_FLAC = 303
AUDIO_WMA = 304
AUDIO_M4A = 305
AUDIO_TRUEAUDIO = 306
AUDIO_WAVE = 307
AUDIO_MKV = 308
AUDIO_MP4 = 309
AUDIO_REALMEDIA = 310

GENERAL_AUDIO = 400
GENERAL_IMAGE = 401
GENERAL_VIDEO = 402
GENERAL_APPLICATION = 403
GENERAL_ANIMATION = 404

ANIMATIONS = {IMAGE_GIF, IMAGE_APNG}

APPLICATIONS = {
    APPLICATION_FLASH,
    APPLICATION_PSD,
    APPLICATION_CLIP,
    APPLICATION_PDF,
    APPLICATION_ZIP,
    APPLICATION_RAR,
    APPLICATION_7Z,
}

IMAGE_MIMES = {IMAGE_JPEG, IMAGE_PNG, IMAGE_GIF, IMAGE_BMP, IMAGE_ICON, IMAGE_WEBP, IMAGE_TIFF}

AUDIO_MIMES = {
    AUDIO_MP3,
    AUDIO_OGG,
    AUDIO_FLAC,
    AUDIO_WMA,
    AUDIO_M4A,
    AUDIO_WAVE,
    AUDIO_MKV,
    AUDIO_MP4,
    AUDIO_REALMEDIA,
}

VIDEO_MIMES = {
    VIDEO_REALMEDIA,
    VIDEO_FLV,
    VIDEO_MP4,
    VIDEO_WMV,
    VIDEO_MKV,
    VIDEO_WEBM,
    VIDEO_MPEG,
    VIDEO_MOV,
    VIDEO_AVI,
    VIDEO_OGV,
}

IMAGE_MIME_RANGE = (min(IMAGE_MIMES), max(IMAGE_MIMES))
VIDEO_MIME_RANGE = (min(VIDEO_MIMES), max(VIDEO_MIMES))
AUDIO_MIME_RANGE = (min(AUDIO_MIMES), max(AUDIO_MIMES))


MIME_STR_LOOKUP = {
    IMAGE_JPEG: "jpeg",
    IMAGE_PNG: "png",
    IMAGE_APNG: "apng",
    IMAGE_GIF: "gif",
    IMAGE_BMP: "bmp",
    IMAGE_WEBP: "webp",
    IMAGE_TIFF: "tiff",
    IMAGE_ICON: "icon",
    APPLICATION_FLASH: "flash",
    APPLICATION_YAML: "yaml",
    APPLICATION_JSON: "json",
    APPLICATION_CBOR: "cbor",
    APPLICATION_PDF: "pdf",
    APPLICATION_PSD: "photoshop psd",
    APPLICATION_CLIP: "clip",
    APPLICATION_ZIP: "zip",
    APPLICATION_RAR: "rar",
    APPLICATION_7Z: "7z",
    AUDIO_M4A: "m4a",
    AUDIO_MP3: "mp3",
    AUDIO_OGG: "ogg",
    AUDIO_FLAC: "flac",
    AUDIO_MKV: "matroska audio",
    AUDIO_MP4: "mp4 audio",
    AUDIO_WAVE: "wave",
    AUDIO_REALMEDIA: "realaudio",
    AUDIO_TRUEAUDIO: "tta",
    AUDIO_WMA: "wma",
    TEXT_HTML: "html",
    TEXT_PLAIN: "plaintext",
    VIDEO_AVI: "avi",
    VIDEO_FLV: "flv",
    VIDEO_MOV: "quicktime",
    VIDEO_MP4: "mp4",
    VIDEO_MPEG: "mpeg",
    VIDEO_WMV: "wmv",
    VIDEO_MKV: "matroska",
    VIDEO_OGV: "ogv",
    VIDEO_REALMEDIA: "realvideo",
    VIDEO_WEBM: "webm",
    UNDETERMINED_VIDEO_WM: "wma or wmv",
    UNDETERMINED_VIDEO_MP4: "mp4 with or without audio",
    UNDETERMINED_PNG: "png or apng",
    APPLICATION_UNKNOWN: "unknown filetype",
    GENERAL_APPLICATION: "application",
    GENERAL_AUDIO: "audio",
    GENERAL_IMAGE: "image",
    GENERAL_VIDEO: "video",
    GENERAL_ANIMATION: "animation",
}

MIME_ENUM_LOOKUP = {
    "image/jpe": IMAGE_JPEG,
    "image/jpeg": IMAGE_JPEG,
    "image/jpg": IMAGE_JPEG,
    "image/x-png": IMAGE_PNG,
    "image/png": IMAGE_PNG,
    "image/apng": IMAGE_APNG,
    "image/gif": IMAGE_GIF,
    "image/bmp": IMAGE_BMP,
    "image/webp": IMAGE_WEBP,
    "image/tiff": IMAGE_TIFF,
    "image/x-icon": IMAGE_ICON,
    "image/vnd.microsoft.icon": IMAGE_ICON,
    "image": IMAGE_MIMES,
    "application/x-shockwave-flash": APPLICATION_FLASH,
    "application/x-photoshop": APPLICATION_PSD,
    "image/vnd.adobe.photoshop": APPLICATION_PSD,
    "application/clip": APPLICATION_CLIP,
    "application/x-yaml": APPLICATION_YAML,
    "PDF document": APPLICATION_PDF,
    "application/pdf": APPLICATION_PDF,
    "application/zip": APPLICATION_ZIP,
    "application/vnd.rar": APPLICATION_RAR,
    "application/x-7z-compressed": APPLICATION_7Z,
    "application/json": APPLICATION_JSON,
    "application/cbor": APPLICATION_CBOR,
    "application": APPLICATIONS,
    "audio/mp4": AUDIO_M4A,
    "audio/mp3": AUDIO_MP3,
    "audio/ogg": AUDIO_OGG,
    "audio/vnd.rn-realaudio": AUDIO_REALMEDIA,
    "audio/x-tta": AUDIO_TRUEAUDIO,
    "audio/flac": AUDIO_FLAC,
    "audio/x-wav": AUDIO_WAVE,
    "audio/wav": AUDIO_WAVE,
    "audio/wave": AUDIO_WAVE,
    "audio/x-ms-wma": AUDIO_WMA,
    "text/html": TEXT_HTML,
    "text/plain": TEXT_PLAIN,
    "video/x-msvideo": VIDEO_AVI,
    "video/x-flv": VIDEO_FLV,
    "video/quicktime": VIDEO_MOV,
    "video/mp4": VIDEO_MP4,
    "video/mpeg": VIDEO_MPEG,
    "video/x-ms-wmv": VIDEO_WMV,
    "video/x-matroska": VIDEO_MKV,
    "video/ogg": VIDEO_OGV,
    "video/vnd.rn-realvideo": VIDEO_REALMEDIA,
    "application/vnd.rn-realmedia": VIDEO_REALMEDIA,
    "video/webm": VIDEO_WEBM,
    "video": VIDEO_MIMES,
    "unknown filetype": APPLICATION_UNKNOWN,
}

MIME_MIMETYPE_STRING_LOOKUP = {
    IMAGE_JPEG: "image/jpeg",
    IMAGE_PNG: "image/png",
    IMAGE_APNG: "image/apng",
    IMAGE_GIF: "image/gif",
    IMAGE_BMP: "image/bmp",
    IMAGE_WEBP: "image/webp",
    IMAGE_TIFF: "image/tiff",
    IMAGE_ICON: "image/x-icon",
    APPLICATION_FLASH: "application/x-shockwave-flash",
    APPLICATION_YAML: "application/x-yaml",
    APPLICATION_JSON: "application/json",
    APPLICATION_CBOR: "application/cbor",
    APPLICATION_PDF: "application/pdf",
    APPLICATION_PSD: "application/x-photoshop",
    APPLICATION_CLIP: "application/clip",
    APPLICATION_ZIP: "application/zip",
    APPLICATION_RAR: "application/vnd.rar",
    APPLICATION_7Z: "application/x-7z-compressed",
    AUDIO_M4A: "audio/mp4",
    AUDIO_MP3: "audio/mp3",
    AUDIO_OGG: "audio/ogg",
    AUDIO_FLAC: "audio/flac",
    AUDIO_MKV: "audio/x-matroska",
    AUDIO_MP4: "audio/mp4",
    AUDIO_WAVE: "audio/x-wav",
    AUDIO_REALMEDIA: "audio/vnd.rn-realaudio",
    AUDIO_TRUEAUDIO: "audio/x-tta",
    AUDIO_WMA: "audio/x-ms-wma",
    TEXT_HTML: "text/html",
    TEXT_PLAIN: "text/plain",
    VIDEO_AVI: "video/x-msvideo",
    VIDEO_FLV: "video/x-flv",
    VIDEO_MOV: "video/quicktime",
    VIDEO_MP4: "video/mp4",
    VIDEO_MPEG: "video/mpeg",
    VIDEO_WMV: "video/x-ms-wmv",
    VIDEO_MKV: "video/x-matroska",
    VIDEO_OGV: "video/ogg",
    VIDEO_REALMEDIA: "video/vnd.rn-realvideo",
    VIDEO_WEBM: "video/webm",
    APPLICATION_UNKNOWN: "unknown filetype",
    GENERAL_APPLICATION: "application",
    GENERAL_AUDIO: "audio",
    GENERAL_IMAGE: "image",
    GENERAL_VIDEO: "video",
    GENERAL_ANIMATION: "animation",
}


MIME_EXT_LOOKUP = {
    IMAGE_JPEG: ".jpg",
    IMAGE_PNG: ".png",
    IMAGE_APNG: ".png",
    IMAGE_GIF: ".gif",
    IMAGE_BMP: ".bmp",
    IMAGE_WEBP: ".webp",
    IMAGE_TIFF: ".tiff",
    IMAGE_ICON: ".ico",
    APPLICATION_FLASH: ".swf",
    APPLICATION_YAML: ".yaml",
    APPLICATION_JSON: ".json",
    APPLICATION_PDF: ".pdf",
    APPLICATION_PSD: ".psd",
    APPLICATION_CLIP: ".clip",
    APPLICATION_ZIP: ".zip",
    APPLICATION_RAR: ".rar",
    APPLICATION_7Z: ".7z",
    AUDIO_M4A: ".m4a",
    AUDIO_MP3: ".mp3",
    AUDIO_MKV: ".mkv",
    AUDIO_MP4: ".mp4",
    AUDIO_OGG: ".ogg",
    AUDIO_REALMEDIA: ".ra",
    AUDIO_FLAC: ".flac",
    AUDIO_WAVE: ".wav",
    AUDIO_TRUEAUDIO: ".tta",
    AUDIO_WMA: ".wma",
    TEXT_HTML: ".html",
    TEXT_PLAIN: ".txt",
    VIDEO_AVI: ".avi",
    VIDEO_FLV: ".flv",
    VIDEO_MOV: ".mov",
    VIDEO_MP4: ".mp4",
    VIDEO_MPEG: ".mpeg",
    VIDEO_WMV: ".wmv",
    VIDEO_MKV: ".mkv",
    VIDEO_OGV: ".ogv",
    VIDEO_REALMEDIA: ".rm",
    VIDEO_WEBM: ".webm",
    APPLICATION_UNKNOWN: "",
}

EXT_MIME_LOOKUP = {value: key for (key, value) in MIME_EXT_LOOKUP.items()}


IMAGE_GIF_HEADERS = (
    (0, b"GIF87a"),
    (0, b"GIF89a"),
)

IMAGE_TIFF_HEADERS = (
    (0, b"II*\x00"),  # little endian
    (0, b"MM\x00*"),  # big endian
)

IMAGE_ICO_HEADERS = ((0, b"\x00\x00\x01\x00"), (0, b"\x00\x00\x02\x00"))

IMAGE_BMP_HEADER = ((0, b"BM"),)
IMAGE_WEBP_HEADER = ((8, b"WEBP"),)
IMAGE_PNG_HEADER = ((0, b"\x89PNG\r\n\x1a\n"),)
IMAGE_JPEG_HEADERS = ((0, b"\xFF\xD8\xFF"),)
IMAGE_UNDETERMINED_PNG_HEADERS = ((0, b"\x89PNG"),)  # apng or png


UNDETERMINED_VIDEO_MP4_HEADERS = (
    (4, b"ftypmp4"),
    (4, b"ftypisom"),
    (4, b"ftypM4V"),
    (4, b"ftypMSNV"),
    (4, b"ftypavc1"),
    (4, b"ftypFACE"),
    (4, b"ftypdash"),
)

VIDEO_FLV_HEADER = ((0, b"FLV"),)
VIDEO_MOV_HEADERS = ((4, b"ftypqt"),)
VIDEO_AVI_HEADERS = ((8, b"AVI "),)
VIDEO_MKV_HEADERS = ((0, b"\x1aE\xdf\xa3"),)

UNDETERMINED_VIDEO_WM_HEADERS = ((0, b"\x30\x26\xB2\x75\x8E\x66\xCF\x11\xA6\xD9\x00\xAA\x00\x62\xCE\x6C"),)

AUDIO_FLAC_HEADERS = ((0, b"fLaC"),)
AUDIO_WAVE_HEADERS = (
    (0, b"RIFF"),
    (8, b"WAVE"),
)


PDF_HEADER = ((0, b"%PDF"),)

ALL_DETERMINED_FILE_HEADERS = list(
    IMAGE_JPEG_HEADERS
    + IMAGE_PNG_HEADER
    + IMAGE_WEBP_HEADER
    + IMAGE_GIF_HEADERS
    + UNDETERMINED_VIDEO_MP4_HEADERS
    + VIDEO_MKV_HEADERS
    + VIDEO_MOV_HEADERS
    + IMAGE_TIFF_HEADERS
    + PDF_HEADER
    + AUDIO_FLAC_HEADERS
    + AUDIO_WAVE_HEADERS
    + VIDEO_AVI_HEADERS
    + IMAGE_ICO_HEADERS
    + IMAGE_BMP_HEADER
    + VIDEO_FLV_HEADER
    + UNDETERMINED_VIDEO_WM_HEADERS
)
