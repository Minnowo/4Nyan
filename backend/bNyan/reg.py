from re import compile, IGNORECASE
from . import constants_

# matches any invalid path characters for the given system 
INVALID_PATH_CHAR        = compile(r"[\\|/<>:\"?*]")
INVALID_PATH_WITHOUT_SEP = compile(f"[{constants_.RESTRICT_MAP_NO_SEP['auto']}]")

# matches \..\ in path names 
UP_DIRECTORY_LEVEL = compile(r"[/\\]?\.\.[/\\]")

# forces a-z A-Z and '-' for singup names 
REMOVE_INVALID_SIGNUP_NAME = compile(r"[^\-a-zA-Z]")

# used to match the range header in requests, only grabs the starting bytes value
RANGE_HEADER = compile(r"bytes=(?P<min>[0-9]+)\-(?P<max>[0-9]+)?", flags=IGNORECASE)

DIGIT = compile(r"([0-9]+)")

# searches for anything that is not a-z A-Z 0-9 -_!@#$%^&*()+=.,/\
HAS_INVALID_PASSWORD_CHARACTERS = compile(r"[^a-zA-Z0-9\-\_\!\@\#\$\%\^\&\*\(\)\+\=\.\,\/\\)]")

# searches for anything that is not a-z A-Z 0-9 - _ .
HAS_INVALID_USERNAME_CHARACTERS = compile(r"[^a-zA-Z0-9\-\_\.]")

IS_HEXADECIMAL = compile(r"^(?:0[x])?(?P<hex>[a-f0-9]+)$", flags=IGNORECASE)
IS_RAW_HEXADECIMAL = compile(r"^([a-f0-9]+)$", flags=IGNORECASE)

IS_TS_FILENAME = compile(r"^\d+\.ts")

TAG = compile(r"^(?:(?P<namespace>.+):)?(?P<tag>.+)$")

SUBTITLE_FILE = compile(r"^sub-\d+\.((vtt)|(ass)|(srt))$", flags=IGNORECASE)
