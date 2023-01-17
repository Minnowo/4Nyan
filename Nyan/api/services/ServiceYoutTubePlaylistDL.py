import base64
import re
import threading

try:
    import yt_dlp

    YT_DL_OK = True

except ImportError:

    YT_DL_OK = False

    logging.warning("No module yt_dlp found")

from fastapi import Request, HTTPException, status
from urllib.parse import urlparse, parse_qs
from .. import APIFastAPI, APIExceptions, APIConstants, APIPaths
from ...core import NyanController, NyanData, NyanLogging as logging, NyanExceptions, NyanGlobals


class YT_DLP_Logger:
    def __init__(self) -> None:

        self.warning = logging.warning

        self.last_err = ""

    def get_clear_last_err(self):

        if self.last_err:

            e = self.last_err

            self.last_err = ""

            return e

        return ""

    def error(self, msg):

        logging.error(msg)

        self.last_err = msg

    def debug(self, msg):

        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith("[debug] "):
            logging.debug(msg[8:])
        else:
            logging.debug(msg)


class Youtube_Playlist_DL_Service(APIFastAPI.Nyan_Router):
    def __init__(self, controller: NyanController.Nyan_Controller):
        APIFastAPI.Nyan_Router.__init__(self, "Youtube Playlist Service", controller)

        self.yt_dlp_logger = YT_DLP_Logger()

        self.add_api_route("/svc/get-yt-playlist", self.route_get_playlist_entries, methods=["GET"])

        self.results_cache = NyanData.Expiring_Data_Cache(controller, self.name + ": Playlist Result Cache", 60)

    def decode_b64(self, value: str):

        try:
            return base64.b64decode(value.encode()).decode()

        except base64.binascii.Error:
            return ""

        except Exception as e:
            logging.debug(f"Failed to decode base64: {value}", e)
            return ""

    @APIFastAPI.Nyan_Router.die_if_shutdown_endpoint_wrapper_async
    async def route_get_playlist_entries(self, request: Request):

        PLAYLIST_FORMAT = "https://www.youtube.com/playlist?list={}"
        playlists = []

        queries = request.query_params

        playlist_url = queries.getlist("playlist_url")
        playlist_id = queries.getlist("playlist_id")
        is_base64 = queries.get("b64", False)

        if playlist_url is None and playlist_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="playlist_url and playlist_id query param was Null"
            )

        if is_base64 and isinstance(is_base64, str):

            # if [0] is not f, 0, n
            is_base64 = not (is_base64[0].lower() in ("f", "0", "n"))

        if playlist_url:

            for playlist in playlist_url:

                if is_base64:
                    playlist = self.decode_b64(playlist)

                url_parsed = urlparse(playlist)
                url_params = parse_qs(url_parsed.query)

                url_playlist_id = url_params.get("list", None)

                if url_playlist_id:

                    playlists.extend(PLAYLIST_FORMAT.format(i) for i in url_playlist_id)

        if playlist_id:

            for playlist in playlist_id:

                if is_base64:
                    playlist = self.decode_b64(playlist)

                if playlist:

                    playlists.append(PLAYLIST_FORMAT.format(playlist))

        return self.get_playlist_urls_wrapped(playlists)

    def run_job(self):

        if not YT_DL_OK:
            logging.warning(f"[{self.name}] yt_dlp module is not installed, this job requires it!")
            return

    def yt_dlp_progress_hook(self, arg):
        pass

    @APIFastAPI.Nyan_Router.die_if_shutdown_wrapper
    def get_playlist_urls_wrapped(self, playlist_url: list[str]):

        result = {}

        for url in set(playlist_url):

            if self.results_cache.has_non_expired_data(url):

                result[url] = self.results_cache.get_data(url)

                playlist_url = list(filter(url.__ne__, playlist_url))

                logging.debug(f"Cache hit for key {url}")

        try:
            new_results = self.get_playlist_urls(playlist_url)

            # dump our new values into the cache, expires in 60 seconds
            for key, value in new_results.items():

                self.results_cache.add_data(key, value, replace=True)

            result.update(new_results)

            return result

        except Exception as e:

            logging.error("Error getting playlist ids with yt-dlp", e, exc_info=True)

            raise APIExceptions.API_500_NOT_IMPLEMENTED

    @APIFastAPI.Nyan_Router.die_if_shutdown_wrapper
    def get_playlist_urls(self, playlist_url: list[str]):

        if not YT_DL_OK:
            logging.warning(f"[{self.name}] yt_dlp module is not installed, this job requires it!")
            return {}

        result = {}

        if not playlist_url:
            return result

        # much easier to work with actual cli arguments
        parser, opts, all_urls, ydl_opts = yt_dlp.parse_options(
            ["--no-colors", "--flat-playlist", "--get-url", "--quiet", playlist_url[0]]
        )

        ydl_opts["logger"] = self.yt_dlp_logger
        ydl_opts["progress_hooks"] = [self.yt_dlp_progress_hook]
        ydl_opts["external_downloader_args"] = ["-loglevel", "panic"]

        self.die_if_shutdown()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            for url in playlist_url:

                data = ydl.extract_info(url, download=False)

                self.die_if_shutdown()

                if self.yt_dlp_logger.last_err or not data:

                    result[url] = [self.yt_dlp_logger.get_clear_last_err()]
                    continue

                if isinstance(data, dict) and "entries" in data:

                    result[url] = list(set(i.get("url") for i in data.get("entries")))

                else:
                    result[url] = []

            return result
