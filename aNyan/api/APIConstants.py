import os

from ..core import aNyanData

env: dict = aNyanData.get_envvars()

MAX_USERNAME_LENGTH = 32
MIN_USERNAME_LEGNTH = 4

MAX_PASSWORD_LENGTH = 96
MIN_PASSWORD_LENGTH = 10

PEPPER = "UEZ5V_HewsMowePwdLenthUWU__ooZqe"
SALT_ROUNDS = 14
SALT_PREFIX = b"2b"  # needs to be 2b or 2a

SECRET = os.urandom(128).hex()

BYTE = 1
KILOBYTE = BYTE * 1024
MEGABYTE = KILOBYTE * 1024
GIGABYTE = MEGABYTE * 1024


STATUS_202_PARTIAL_RESPONSE = 202
STATUS_200_OK = 200


VIDEO_STREAM_CHUNK_SIZE = MEGABYTE * 8
IMAGE_UPLOAD_CHUNK_SIZE = KILOBYTE * 500


STATIC_IMAGE_PATH = env.get("image_path", ".")
STATIC_THUMBNAIL_PATH = env.get("thumb_path", ".")
STATIC_VIDEO_PATH = env.get("video_path", ".")

SERVER_PORT = 721
SERVER_IP = env.get("server_ip", "0.0.0.0")
SERVER_ADDRESS = f"http://{SERVER_IP}:{SERVER_PORT}/"


import re

# used to match the range header in requests, only grabs the starting bytes value
RANGE_HEADER = re.compile(r"bytes=(?P<min>[0-9]+)\-(?P<max>[0-9]+)?", flags=re.IGNORECASE)
