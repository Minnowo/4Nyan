import os

from fastapi import Request, Response

from .. import APIFastAPI, APIExceptions, APIConstants, APIPaths
from ...core import NyanController


class File_Service(APIFastAPI.Nyan_Router):
    def __init__(self, controller: NyanController.Nyan_Controller):

        APIFastAPI.Nyan_Router.__init__(self, "File Service", controller)

        self.add_api_route("/svc/{category}/{path}", self.staticv1, methods=["HEAD", "GET"])
        # self.add_api_route("/favicon.ico", self.favicon, methods=["HEAD", "GET"])

        self.staticv1_function_map = {
            "v": self.stream_video,
            # "i": APIFiles.get_image,
            # "t": APIFiles.get_thumbnail,
        }

    @APIFastAPI.Nyan_Router.die_if_shutdown_endpoint_wrapper_async
    async def staticv1(self, request: Request, category: str, path: str):

        callback = self.staticv1_function_map.get(category, None)

        if callback:

            return await callback(request, path)

        raise APIExceptions.API_404_NOT_FOUND_EXCEPTION

    @APIFastAPI.Nyan_Router.die_if_shutdown_wrapper_async
    async def stream_video(self, request: Request, path: str):

        video_name = APIPaths.get_valid_path_or_die((APIConstants.STATIC_VIDEO_PATH, path))

        # get start byte range from header, default to 0
        _range = APIConstants.RANGE_HEADER.search(request.headers.get("range", "bytes=0-"))

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
