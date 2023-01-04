import os
import hashlib
import io
import logging
import re

from fastapi.responses import FileResponse
from fastapi import Response, UploadFile, HTTPException, Request

from typing import Union

from . import APIConstants
from . import APIExceptions


# used to match the range header in requests, only grabs the starting bytes value
RANGE_HEADER = re.compile(r"bytes=(?P<min>[0-9]+)\-(?P<max>[0-9]+)?", flags=re.IGNORECASE)

HAS_VALID_CHARACTERS = re.compile(r"^[a-zA-Z0-9\-\_\.\(\)\[\]\,]+", flags=re.IGNORECASE)

CONTAINS_TRICKY_PATHING = re.compile(r"[\\\/]\.\.[\\\/]")


def die_if_bad_path(path: str):

    if not HAS_VALID_CHARACTERS.match(path):

        raise APIExceptions.API_400_BAD_REQUEST_EXCEPTION


def get_clean_valid_path_or_die(path: str, in_folder: str = None):

    die_if_bad_path(path)

    if in_folder is not None:

        path = os.path.join(in_folder, path)

    logging.debug(f"checking path: {path}")

    if not os.path.isfile(path):

        raise APIExceptions.API_400_BAD_REQUEST_EXCEPTION

    return path


def get_image(request: Request, image_name: str, in_folder: str = APIConstants.STATIC_IMAGE_PATH) -> FileResponse:

    image_name = get_clean_valid_path_or_die(image_name, in_folder)

    headers = {
        "accept-range": "bytes",
        "content-type": "image/jpeg",
        "filename": os.path.basename(image_name),
    }

    if request.method == "HEAD":
        return headers

    return FileResponse(image_name, headers=headers, media_type="image")


def get_thumbnail(request: Request, image_name: str) -> FileResponse:

    return get_image(request, image_name, APIConstants.STATIC_THUMBNAIL_PATH)


def stream_video(request: Request, video_name: str) -> Response:

    video_name = get_clean_valid_path_or_die(video_name, APIConstants.STATIC_VIDEO_PATH)

    # get start byte range from header, default to 0
    _range = RANGE_HEADER.search(request.headers.get("range", "bytes=0-"))

    if not _range:
        raise APIExceptions.API_400_BAD_REQUEST_EXCEPTION

    file_size = os.stat(video_name).st_size

    seek_to = int(_range.group("min"))
    read_to = min(
        int(_range.group("max") or seek_to + APIConstants.VIDEO_STREAM_CHUNK_SIZE),
        file_size,
    )

    bytes_to_read = read_to - seek_to

    if bytes_to_read <= 0:
        raise APIExceptions.API_400_BAD_REQUEST_EXCEPTION

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Range": f"bytes {seek_to}-{read_to}/{file_size}",
        "Content-Type": "video/mp4",
    }

    if request.method == "HEAD":
        return headers

    with open(video_name, "rb") as reader:

        reader.seek(seek_to)

        data = reader.read(bytes_to_read)

        return Response(data, status_code=APIConstants.STATUS_202_PARTIAL_RESPONSE, headers=headers)


# def _get_video(video_name: tuple, request: Request):
#     """Returns a full video with a 200 request, this is used to transer .ts video files for hls"""

#     name_check(video_name)

#     (dire, file) = video_name

#     video_path = get_clean_name(os.path.join(dire, file), APIConstants.STATIC_VIDEO_PATH)

#     total_response_size = os.stat(video_path).st_size

#     headers = {
#         "Accept-Ranges": "bytes",
#         "Content-Range": f"bytes {0}-{total_response_size}/{total_response_size}",
#         "Content-Type": "video/ts",
#         "Content-Disposition": 'attachment; filename="{}"'.format(file),
#     }

#     if request.method == "HEAD":
#         return headers

#     with open(video_path, "rb") as reader:

#         data = reader.read(total_response_size)

#         return Response(data, status_code=APIConstants.STATUS_200_OK, headers=headers)
