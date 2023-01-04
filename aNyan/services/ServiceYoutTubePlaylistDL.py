import logging

try:
    import yt_dlp

    YT_DL_OK = True

except ImportError:

    YT_DL_OK = False

    logging.warning("No module yt_dlp found")


from . import ServiceBase


class YT_DLP_Logger:
    def __init__(self) -> None:

        self.info = logging.info
        self.warning = logging.warning
        self.error = logging.error

    def debug(self, msg):

        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith("[debug] "):
            logging.debug(msg[8:])
        else:
            self.info(msg)


class Youtube_Playlist_DL(ServiceBase.Service):
    def __init__(self) -> None:
        ServiceBase.Service.__init__("Youtube Playlist Service")

        self.yt_dlp_logger = YT_DLP_Logger()

    def run_job(self):

        if not YT_DL_OK:
            logging.warning(f"[{self.name}] yt_dlp module is not installed, this job requires it!")
            return

    def yt_dlp_progress_hook(self, arg):
        pass

    def get_playlist_urls(self, playlist_url: str):

        # much easier to work with actual cli arguments
        parser, opts, all_urls, ydl_opts = yt_dlp.parse_options(["--flat-playlist", "--get-url", "--quiet", playlist_url])

        ydl_opts["logger"] = self.yt_dlp_logger
        ydl_opts["progress_hooks"] = [self.yt_dlp_progress_hook]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            data = ydl.extract_info(playlist_url, download=False)

            return set(i.get("url") for i in data.get("entries"))
