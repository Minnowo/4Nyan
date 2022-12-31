import subprocess
import time
import os
from contextlib import contextmanager

FFMPEG_PATH = "..\\..\\backend\\bnyan\\bin\\ffmpeg.exe"


@contextmanager
def read_write_file(path, lines, is_bytes=False):
    """
    reads a file and yields the file object,

    then overwrites the file with the given lines array after the 'with' clause

    this is used to read a file one line at a time, and if the line matches a matches a condition append a modified string to the lines array, otherwise just append the line
    """

    with open(path, "r" + "b" * is_bytes) as file:

        yield file

    with open(path, "w" + "b" * is_bytes) as writer:

        writer.writelines(lines)


def subprocess_communicate(process: subprocess.Popen, timeout: int = 10) -> tuple:
    """returns process.communicate with the given timeout"""

    while True:

        try:

            return process.communicate(timeout=timeout)

        except subprocess.TimeoutExpired:

            pass


def remove_file(path: str) -> bool:
    """Deletes the given file."""
    try:
        os.unlink(path)
    except OSError:
        pass
    return not os.path.exists(path)


def rename_file(filename: str, new_filename: str, *, replace: bool = False) -> bool:
    """
    Renames the given file with the new filename

    replace : bool - should any existing files be deleted/replaced by the given file

    returns True if the file was renamed otherwise False

    TODO: make this temp delete the replace file so that if the rename fails after it can be restored
    """

    if not new_filename:
        return False

    try:
        if os.path.isfile(new_filename):

            if not replace:
                return False

            if not remove_file(new_filename):
                return False

        os.rename(filename, new_filename)
        return True

    except OSError as e:
        return False


def run_ffmpeg_standard(ff_args):

    if not ff_args:
        raise Exception("argments empty")

    process = subprocess.Popen(ff_args, bufsize=10**5, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # LOGGER.info("Running FFMPEG with args: {}".format(ff_args))
    start_time = time.perf_counter()

    (stdout, stderr) = subprocess_communicate(process)

    data_bytes = stderr

    # LOGGER.info("FFMPEG finished after {} seconds".format(time.perf_counter() - start_time))

    if len(data_bytes) != 0:

        raise Exception(data_bytes)

        LOGGER.info("FFMPEG failed with exit: {}".format(non_failing_unicode_decode(data_bytes, "utf-8")))

        raise exceptions.FFMPEG_Exception(non_failing_unicode_decode(data_bytes, "utf-8"))

    del process


def encode_video_standard(video_path: str, output_path: str):

    # https://superuser.com/questions/859010/what-ffmpeg-command-line-produces-video-more-compatible-across-all-devices

    ff_args = [
        FFMPEG_PATH,
        "-y",
        "-v",
        "error",
        "-i",
        video_path,
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-ac",
        "2",
        "-c:s",
        "mov_text",
        "-r",
        "23.976",
        "-g",
        "48",
        "-keyint_min",
        "48",
        "-profile:v",
        "baseline",
        "-level",
        "3.0",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "faststart",
        # '-threads', '1',         # reduce cpu but greatly increase time
        "-crf",
        "28",
        "-f",
        "mp4",
        output_path,
    ]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    run_ffmpeg_standard(ff_args)


def split_encoded_video(video_path: str, output_directory: str, segment_size: int):

    os.makedirs(output_directory, exist_ok=True)

    ff_args = [
        FFMPEG_PATH,
        "-y",
        "-v",
        "error",
        "-i",
        video_path,
        "-c",
        "copy",
        "-sn",
        "-f",
        "hls",
        "-hls_time",
        str(segment_size),
        "-hls_playlist_type",
        "vod",
        "-hls_flags",
        "independent_segments",
        "-hls_segment_type",
        "mpegts",
        "-hls_segment_filename",
        os.path.join(output_directory, "%02d.ts"),
        "-master_pl_name",
        "master.m3u8",
        os.path.join(output_directory, "index.m3u8"),
    ]

    run_ffmpeg_standard(ff_args)

    subs_vtt = os.path.join(output_directory, "index_vtt.m3u8")
    index_m3u8 = os.path.join(output_directory, "index.m3u8")
    master = os.path.join(output_directory, "master.m3u8")

    subs_exist = os.path.isfile(subs_vtt)

    # if the video had subtitles, this will exist,
    # so rename them and fix the file
    lines = []
    if subs_exist:

        new_name = 0

        with read_write_file(subs_vtt, lines) as raw:

            for line in raw:

                if not line.endswith(".vtt\n"):
                    lines.append(line)
                    continue

                o_name = os.path.join(output_directory, line.rstrip())
                n_name = "{0:02d}.vtt".format(new_name)

                rename_file(o_name, os.path.join(output_directory, n_name), replace=True)

                # creating a template file, this file will get formatted when the m3u8 is requested
                # {URL}00.vtt -> http://...00.vtt
                lines.append("{URL}" + n_name + "\n")

                new_name += 1

    # apply required changes to the index.m3u8 file
    lines *= 0  # lines = []
    with read_write_file(index_m3u8, lines) as raw:

        for line in raw:

            if not line.endswith(".ts\n"):
                lines.append(line)
                continue

            lines.append("{URL}" + line.rstrip() + "\n")

    # template for subtitles in m3u8 file
    m3u8_sub_template = '#EXT-X-MEDIA:TYPE=SUBTITLES,URI="{}",GROUP-ID="{}",LANGUAGE="{}",NAME="{}",AUTOSELECT=YES\n'

    # apply required changes to master.m3u8
    lines *= 0  # lines = []
    with read_write_file(master, lines) as raw:

        for line in raw:

            if subs_exist and line.startswith("#EXT-X-STREAM-INF:"):
                lines.append(m3u8_sub_template.format("{SUB_URL}index_vtt.m3u8", "subs", "en", "subtitle track 1"))
                lines.append(line.rstrip() + ',SUBTITLES="subs"\n')
                continue

            if not line.endswith(".m3u8\n"):
                lines.append(line)
                continue

            lines.append("{URL}" + line.rstrip() + "\n")

    result = [master, index_m3u8]

    if subs_exist:

        result.append(subs_vtt)

    return result


video_path = ".\\video-test\\short-with-subs.mkv"
output_dir = ".\\video-test\\output\\"
segment_size = 6

# encode_video_standard(video_path, output_dir + "encoded.mp4")
split_encoded_video(output_dir + "encoded.mp4", output_dir + "uwu\\", 4)
