import logging
import os 
from subprocess import run, PIPE

from .. import util
from .. import constants

from . import exceptions

logger = logging.getLogger(__name__)

# https://github.com/cambackup/m3u8-generator
class PlaylistGenerator(object):

    @classmethod
    def generate_from_directory(cls, directory, segment_size):

        template = []

        for file in sorted(os.listdir(directory), key=util.natural_sort_key):

            template.append({
                "name" : file,
                "duration" : segment_size
            })

        _instance = cls(template)

        return _instance.generate()

    def __init__(self, playlist_entries=None, version=3):
        if playlist_entries == None:
            raise Exception

        self.end_playlist = True
        self.playlist_entries = playlist_entries
        self.version = version
        self.sequence = 0
        self.duration = self.duration()

    def _generate_playlist(self):
        playlist = "{}\n{}".format(self._m3u8_header_template(), self._generate_playlist_entries())

        return playlist

    def _generate_playlist_entries(self):
        playlist = ""
        for entry in self.playlist_entries:
            playlist += "#EXTINF:{duration}\n{media}\n".format(duration=float(entry['duration']), media=(entry['name']))

        return playlist.replace(" ", "")


    def _generate(self):
        return self._generate_playlist()

    def _m3u8_header_template(self):
        header = "#EXTM3U\n#EXT-X-VERSION:{version}\n#EXT-X-MEDIA-SEQUENCE:{sequence}\n#EXT-X-TARGETDURATION:{duration}".format(version=self.version, sequence=self.sequence, duration=self.duration).strip()

        if self.end_playlist:
            return "{}\n#EXT-X-ENDLIST".format(header)
        else:
            return header

    def duration(self):
        duration_total = 0
        for entry in self.playlist_entries:
            if 'duration' in entry:
                try:
                    duration_total += float(entry['duration'])
                except Exception as e:
                    logger.exception(e)

        return duration_total

    def generate(self):
        """ This is a proxy for _generate makes it
        difficult to edit the real method for future."""
        return self._generate()


class VideoSplitter():
    
    FFMPEG_PATH  = constants.FFMPEG_PATH
    FFPROBE_PATH = constants.FFPROBE_PATH

    def __init__(self, ffmpeg=FFMPEG_PATH, ffmprobe=FFPROBE_PATH) -> None:
        
        self.ffmpeg = ffmpeg
        self.ffprobe = ffmprobe


    def split_video(self, video_path, output_directory, segment_size):
        
        if not os.path.isfile(self.ffmpeg):
            raise Exception("The FFMPEG path: '{}' does not exist.".format(self.ffmpeg))

        if not os.path.isfile(video_path):
            raise Exception("The Video path: '{}' does not exist.".format(video_path))

        util.create_directory(output_directory)

        ff_args = [self.ffmpeg, '-y', '-v', 'error',
                   '-i', video_path, '-c', 'copy', '-map', '0', 
                   '-segment_time', str(segment_size), '-f', 'segment', 
                   os.path.join(output_directory, '%03d.ts')]
        
        ff_proc = run(ff_args, stderr=PIPE)

        _error  = ff_proc.stderr.decode()

        if _error:
            raise exceptions.FFMPEG_Exception(_error)

        

if __name__ == "__main__":
    playlist_entries = [
                            {
                            'name':  "Awesomevideo_001.mp4",
                            'duration' : '10.04',
                            }
            ]

    playlist = PlaylistGenerator(playlist_entries).generate()

    splitter = VideoSplitter("X:\\ffmpeg\\ffmpeg.exe", "X:\\ffmpeg\\ffprobe.exe")
    splitter.split_video("..\\..\\static\\v\\fall2.mp4", 10, "..\\..\\static\\v\\split\\")

    print(playlist)