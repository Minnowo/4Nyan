import os

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


STATIC_IMAGE_PATH = "."
STATIC_THUMBNAIL_PATH = "."
STATIC_VIDEO_PATH = "."

SERVER_PORT = 721
SERVER_IP = "127.0.0.1"
SERVER_ADDRESS = f"http://{SERVER_IP}:{SERVER_PORT}/"