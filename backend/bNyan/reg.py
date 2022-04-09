from re import compile
from constants import RESTRICT_MAP, RESTRICT_MAP_NO_SEP

# matches any invalid path characters for the given system 
INVALID_PATH_CHAR        = compile(f"[{RESTRICT_MAP['auto']}]")
INVALID_PATH_WITHOUT_SEP = compile(f"[{RESTRICT_MAP_NO_SEP['auto']}]")

# matches \..\ in path names 
UP_DIRECTORY_LEVEL = compile(r"[/\\]?\.\.[/\\]")

# forces a-z A-Z and '-' for singup names 
REMOVE_INVALID_SIGNUP_NAME = compile(r"[^\-a-zA-Z]")

# used to match the range header in requests, only grabs the starting bytes value
RANGE_HEADER = compile(r"bytes=([0-9]+)\-")

DIGIT = compile(r"([0-9]+)")

# searches for anything that is not a-z A-Z 0-9 -_!@#$%^&*()+=.,/\
HAS_INVALID_PASSWORD_CHARACTERS = compile(r"[^a-zA-Z0-9\-\_\!\@\#\$\%\^\&\*\(\)\+\=\.\,\/\\)]")

