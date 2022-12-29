from .. import exceptions
from .. import constants_ as C
from ..constants_ import mime_types as MT

from . import video_handling
from . import audio_handling
from . import image_handling

import os.path

# very big thanks to https://github.com/hydrusnetwork/hydrus
#
# the 'get_mime' function was taken directly from hydrus.Core.HydrusFileHandling


def get_mime(path: str) -> int:
    """gets a file's mime type"""

    size = os.path.getsize(path)

    if size == 0:

        raise exceptions.ZeroSizeFileException("File is of zero length!")

    with open(path, "rb") as f:

        bit_to_check = f.read(256)

    for (offsets_and_headers, mime) in C.HEADERS_AND_MIME:

        it_passes = False not in (bit_to_check[offset:].startswith(header) for (offset, header) in offsets_and_headers)

        if it_passes:

            if mime in (MT.UNDETERMINED_VIDEO_WM, MT.UNDETERMINED_VIDEO_MP4):

                return video_handling.get_video_mime(path)

            # # i don't really care for animated png, but i'm leaving this here if i need it later
            # if mime == C.UNDETERMINED_PNG:

            #     if IsPNGAnimated( bit_to_check ):

            #         return C.IMAGE_APNG

            #     else:

            #         return C.IMAGE_PNG

            # else:

            return mime

    try:

        mime = video_handling.get_video_mime(path)

        if mime != MT.APPLICATION_UNKNOWN:

            return mime

    except Exception as e:

        print("FFMPEG had trouble with: " + path)
        print(e)

    # if HydrusText.LooksLikeHTML( bit_to_check ):

    #     return C.TEXT_HTML

    return MT.APPLICATION_UNKNOWN


def get_mime_from_bytes(bit_to_check: bytes) -> int:

    for (offsets_and_headers, mime) in C.HEADERS_AND_MIME:

        if any(bit_to_check[offset:].startswith(header) for (offset, header) in offsets_and_headers):

            if mime in (MT.UNDETERMINED_VIDEO_WM, MT.UNDETERMINED_VIDEO_MP4):

                raise exceptions.FFMPEG_Required_Exception(
                    "the given bytes belong to an unknown video format, ffmpeg will be needed to determine the format."
                )

            return mime

    return MT.APPLICATION_UNKNOWN
