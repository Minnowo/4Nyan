from re import compile
from constants import RESTRICT_MAP

# matches any invalid path characters for the given system 
INVALID_PATH_CHAR = compile(f"[{RESTRICT_MAP['auto']}]")

# matches \..\ in path names 
UP_DIRECTORY_LEVEL = compile(r"[/\\]\.\.[/\\]")

# forces a-z A-Z and '-' for singup names 
REMOVE_INVALID_SIGNUP_NAME = compile(r"[^\-a-zA-Z]")

RANGE_HEADER = compile(r"bytes=([0-9]+)\-")

DIGIT = compile(r"([0-9]+)")