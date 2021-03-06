

from .. import bn_logging
from .. import exceptions
from .. import util 

from .. import constants_ as C

from ..constants_ import mime_types as MT 

from ..text import non_failing_unicode_decode


from .audio_handling import parse_ffmpeg_audio
from .image_handling import generate_save_image_thumbnail, THUMBNAIL_SCALE_DOWN_ONLY
from re import search, match
 
import subprocess
import os.path 
import time 

# very big thanks to https://github.com/hydrusnetwork/hydrus
# 
# the 'parse_ffmpeg_video_line' function was taken directly from hydrus.Core.HydrusVideoHandling
# the 'parse_ffmpeg_video_format' function was taken directly from hydrus.Core.HydrusVideoHandling
# the 'parse_ffmpeg_has_video' function was taken directly from hydrus.Core.HydrusVideoHandling
# the 'parse_ffmpeg_mime_text' function was taken directly from hydrus.Core.HydrusVideoHandling
# the 'check_ffmpeg_error' function was taken directly from hydrus.Core.HydrusVideoHandling
# the 'parse_ffmpeg_metadata_container' function was taken directly from hydrus.Core.HydrusVideoHandling
# the 'get_ffmpeg_info_lines' function was taken directly from hydrus.Core.HydrusVideoHandling
# the 'get_video_mime' function was taken directly from hydrus.Core.HydrusVideoHandling

LOGGER = bn_logging.get_logger(C.BNYAN_VIDEO_HANDLING[0], C.BNYAN_VIDEO_HANDLING[1])

def parse_ffmpeg_video_line( lines, png_ok = False ):
    """ finds the video line from ffmpeg lines """

    if png_ok:

        bad_video_formats = ['Video: jpg']

    else:

        bad_video_formats = ['Video: jpg', 'Video: png']
        
    
    # get the output line that speaks about video
    # the ^\sStream is to exclude the 'title' line, when it exists, includes the string 'Video: ', ha ha
    # mp3 says it has a 'png' video stream
    lines_video = [ 
        
        l for l in lines 
        
            if search(r'^\s*Stream', l)
            
            and 
            
            'Video: ' in l 
            
            and 
            
            True not in (bvf in l for bvf in bad_video_formats) 
            
        ]

    if len( lines_video ) == 0:
        
        raise exceptions.Damaged_Or_Unusual_File_Exception( 'Could not find video information!' )
        
    
    return lines_video[0]


def parse_ffmpeg_video_dimensions( lines) -> tuple:
    """ returns the width and height of found video stream otherwise (-1, -1)"""
    
    try:
        
        line = parse_ffmpeg_video_line( lines) 

    except exceptions.Unsupported_File_Exception:

        return (-1, -1)

#  Stream #0:0(und): Video: h264 (Constrained Baseline) (avc1 / 0x31637661), yuv420p, 480x360 [SAR 1:1 DAR 4:3], 260 kb/s, 30 fps, 30 tbr, 15360 tbn, 60 tbc (default)

    match = search(r",\s([1-9]\d+)[xX]([1-9]\d+)", line)

    if not match:

        return (-1, -1)

    return (int(match.group(1)), int(match.group(2)))



def parse_ffmpeg_video_format( lines ) -> tuple:
    """ returns a tuple with a bool indicating if there's a video line, and the video line """

    try:
        
        line = parse_ffmpeg_video_line( lines )
        
    except exceptions.Unsupported_File_Exception:
        
        return ( False, 'unknown' )

    match = search( r"(?<=Video:\s).+?(?=,)", line )

    if not match:
        return (True, 'unknown')

    return ( True, match.group() )
    


 
def parse_ffmpeg_has_video( lines ) -> bool:
    """ returns true if ffmpeg has a video line, else false """
    try:
        
        parse_ffmpeg_video_line( lines )
        
    except exceptions.Unsupported_File_Exception:
        
        return False
        
    
    return True
    



def parse_ffmpeg_mime_text( lines ):
    
    try:
        
        ( input_line, ) = [ l for l in lines if l.startswith( 'Input #0' ) ]
        
        # Input #0, matroska, webm, from 'm.mkv':
        
        text = input_line[10:]
        
        mime_text = text.split( ', from' )[0]
        
        return mime_text
        
    except:
        
        raise exceptions.Damaged_Or_Unusual_File_Exception( 'Error reading file type!' )
    




def check_ffmpeg_error( lines ):
    
    if len( lines ) == 0:
        
        raise exceptions.Damaged_Or_Unusual_File_Exception( 'Could not parse that file--no FFMPEG output given.' )
        
    
    if "No such file or directory" in lines[-1]:
        
        raise IOError( "File not found!" )
        
    
    if 'Invalid data' in lines[-1]:
        
        raise exceptions.Damaged_Or_Unusual_File_Exception( 'FFMPEG could not parse.' )
        
   
def parse_ffmpeg_duration( lines ):
    
    # get duration (in seconds)
    #   Duration: 00:00:02.46, start: 0.033000, bitrate: 1069 kb/s
    try:
        
        # had a vid with 'Duration:' in title, ha ha, so now a regex
        line = [ l for l in lines if search( r'^\s*Duration:', l ) is not None ][0]
        
        if 'Duration: N/A' in line:
            
            return ( None, None )
            
        
        if 'start:' in line:
            
            m = search( r'(start: )-?[0-9]+\.[0-9]*', line )
            
            start_offset = float( line[ m.start() + 7 : m.end() ] )
            
        else:
            
            start_offset = 0
            
        
        match = search("[0-9]+:[0-9][0-9]:[0-9][0-9].[0-9][0-9]", line)
        hms = [ float( float_string ) for float_string in line[match.start():match.end()].split(':') ]
        
        duration = 0
        
        l = len( hms )

        if l == 1:
            
            duration = hms[0]
            
        elif l == 2:
            
            duration = 60 * hms[0] + hms[1]
            
        elif l == 3:
            
            duration = 3600 * hms[0] + 60 * hms[1] + hms[2]
            
        
        if duration == 0:
            
            return ( None, None )
            
        
        if start_offset > 0.85 * duration:
            
            # as an example, Duration: 127:57:31.25, start: 460633.291000 lmao
            
            return ( None, None )
            
        
        # we'll keep this for now I think
        if start_offset > 1:
            
            start_offset = 0
            
        
        file_duration = duration + start_offset
        stream_duration = duration
        
        return ( file_duration, stream_duration )
        
    except:
        
        raise exceptions.Damaged_Or_Unusual_File_Exception( 'Error reading duration!' )
        


def parse_ffmpeg_metadata_container( lines ) -> str:
    
    #  Metadata:
    #    major_brand     : isom
    
    metadata_line_index = -1
    
    for ( i, line ) in enumerate( lines ):
        
        if match( r"\s*Metadata:\s*", line ):
            
            metadata_line_index = i
            
            break
            
    
    if metadata_line_index == -1:
        return ''
        
    
    for line in lines[ metadata_line_index : ]:
        
        if match( r"\s*major_brand\s*:.+", line ):
            
            container = line.split( ':', 1 )[1].strip()
            
            return container
    
    return ''
    



# bits of this were originally cribbed from moviepy
def get_ffmpeg_info_lines( path, count_frames_manually = False, only_first_second = False ):
    
    # open the file in a pipe, provoke an error, read output
    
    cmd = [ C.FFMPEG_PATH, "-i", path ]
    
    if only_first_second:

        cmd += ['-t', '1']
        
    
    if count_frames_manually:
        
        # added -an here to remove audio component, which was sometimes causing convert fails on single-frame music webms
        
        if C.IS_WINDOWS:
            
            cmd += [ "-vf", "scale=-2:120", "-an", "-f", "null", "NUL" ]
            
        else:
            
            cmd += [ "-vf", "scale=-2:120", "-an", "-f", "null", "/dev/null" ]
            
        
    #  see hydrus.core.HydrusData.py for this 
    # sbp_kwargs = HydrusData.GetSubprocessKWArgs()
    
    # process = subprocess.Popen( cmd, bufsize = 10**5, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, **sbp_kwargs )
    
    process = subprocess.Popen( cmd, bufsize = 10**5, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    
    ( stdout, stderr ) = util.subprocess_communicate( process )
    
    data_bytes = stderr
    
    if len( data_bytes ) == 0:
        
        raise exceptions.Data_Missing( 'Cannot interact with video because FFMPEG did not return any content.' )
        
    
    del process
    
    ( text, encoding ) = non_failing_unicode_decode( data_bytes, 'utf-8' )
    
    lines = text.splitlines()
    
    check_ffmpeg_error( lines )
    
    return lines
    


def get_video_mime_from_ffmpeg_lines( lines ):

    try:
        
        mime_text = parse_ffmpeg_mime_text( lines )
        
    except Exception:
        
        return MT.APPLICATION_UNKNOWN
        
    
    ( has_video, video_format ) = parse_ffmpeg_video_format( lines )
    ( has_audio, audio_format ) = parse_ffmpeg_audio( lines )
    
    if 'matroska' in mime_text or 'webm' in mime_text:
        
        # a webm has at least vp8/vp9 video and optionally vorbis audio
        
        has_webm_video = False
        
        if has_video:
            
            webm_video_formats = ( 'vp8', 'vp9' )
            
            has_webm_video = any( webm_video_format in video_format for webm_video_format in webm_video_formats )
            
        
        if has_audio:
            
            webm_audio_formats = ( 'vorbis', 'opus' )
            
            has_webm_audio = any( webm_audio_format in audio_format for webm_audio_format in webm_audio_formats )
            
        else:
            
            # no audio at all is not a vote against webm
            has_webm_audio = True
            
        
        if has_webm_video and has_webm_audio:
            
            return MT.VIDEO_WEBM
            
            
        if has_video:
            
            return MT.VIDEO_MKV
            
        if has_audio:
            
            return MT.AUDIO_MKV
                
            
        
    if mime_text in ( 'mpeg', 'mpegvideo', 'mpegts' ):
        
        return MT.VIDEO_MPEG
        
    if mime_text == 'flac':
        
        return MT.AUDIO_FLAC
        
    if mime_text == 'wav':
        
        return MT.AUDIO_WAVE
        
    if mime_text == 'mp3':
        
        return MT.AUDIO_MP3
        
    if mime_text == 'tta':
        
        return MT.AUDIO_TRUEAUDIO
        
    if 'mp4' in mime_text:
        
        container = parse_ffmpeg_metadata_container( lines )
        
        if container == 'M4A':
            
            return MT.AUDIO_M4A
            
        if container == 'qt':
            
            return MT.VIDEO_MOV
            
        if container in ( 'isom', 'mp42' ): # mp42 is version 2 of mp4 standard
            
            if has_video:
                
                return MT.VIDEO_MP4
                
            if has_audio:
                
                return MT.AUDIO_MP4
                
            
        
        if has_audio and 'mjpeg' in video_format:
            
            return MT.AUDIO_M4A
            
        if has_video:
            
            return MT.VIDEO_MP4
            
        if has_audio:
            
            return MT.AUDIO_MP4
            
        
    if mime_text == 'ogg':
        
        if has_video:
            
            return MT.VIDEO_OGV
            
        else:
            
            return MT.AUDIO_OGG
            
        
    if 'rm' in mime_text:
        
        if parse_ffmpeg_has_video( lines ):
            
            return MT.VIDEO_REALMEDIA
            
        return MT.AUDIO_REALMEDIA
            
        
    if mime_text == 'asf':
        
        if parse_ffmpeg_has_video( lines ):
            
            return MT.VIDEO_WMV
            
        return MT.AUDIO_WMA
            
    
    return MT.APPLICATION_UNKNOWN
    



def get_video_mime( path ):
    
    lines = get_ffmpeg_info_lines( path )

    return get_video_mime_from_ffmpeg_lines( lines )
    


    
def get_video_information_from_ffmpeg_lines( lines ):

    has_video, video_format = parse_ffmpeg_video_format( lines )
    has_audio, audio_format = parse_ffmpeg_audio( lines )

    width, height = parse_ffmpeg_video_dimensions( lines )

    file_duration, stream_duration = parse_ffmpeg_duration( lines )

    vinfo = {
        "mime" : get_video_mime_from_ffmpeg_lines( lines ),

        "has_video" : has_video,
        "video_format" : video_format,

        "has_audio" : has_audio,
        "audio_format" : audio_format,

        "width" : width ,
        "height" : height ,

        "duration" : file_duration or 0,
        "stream_duration" : stream_duration or 0 
    }

    return vinfo



def run_ffmpeg_standard(ff_args):

    if not ff_args:
        raise exceptions.FFMPEG_Exception("ffmpeg arguments are empty or null")

    process = subprocess.Popen( ff_args, bufsize = 10**5, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    
    LOGGER.info("Running FFMPEG with args: {}".format(ff_args))
    start_time = time.perf_counter()

    ( stdout, stderr ) = util.subprocess_communicate( process )
    
    data_bytes = stderr

    LOGGER.info("FFMPEG finished after {} seconds".format(time.perf_counter() - start_time))
    
    if len( data_bytes ) != 0:

        LOGGER.info("FFMPEG failed with exit: {}".format(non_failing_unicode_decode( data_bytes, 'utf-8' )))
        
        raise exceptions.FFMPEG_Exception( non_failing_unicode_decode( data_bytes, 'utf-8' ) )
        
    del process




def generate_thumbnail(source_path, dest_path, thumbsize):

    util.create_directory_from_file_name(dest_path)

    dest_jpg = dest_path + ".jpg" # ffmpeg really doesn't like .thumb as an extension

    # looking for png/jpeg video streams from embeded thumbnails 
    # if we cannot find them we will make our own thumbnail 
    ff_args = [
        C.FFMPEG_PATH, '-y', '-v', 'error',
        '-i', str(source_path),
        '-c', 'copy',
        '-map', '0:v',
        '-map', '-0:V',
        '-vframes', '1',
        dest_jpg 
    ]

    process = subprocess.Popen( ff_args, bufsize = 10**5, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    
    LOGGER.info("Generating video thumbnail for: {}".format(source_path))
    LOGGER.info("Running FFMPEG with args: {}".format(ff_args))

    start_time = time.perf_counter()

    ( stdout, stderr ) = util.subprocess_communicate( process )
    
    data_bytes = stderr
    
    fallback = False 

    LOGGER.info("FFMPEG finished after {} seconds".format(time.perf_counter() - start_time))

    if len( data_bytes ) != 0:
        

        fallback = data_bytes == b'Output file #0 does not contain any stream\r\n'

        if not fallback:

            LOGGER.info("FFMPEG failed with exit: {}".format(non_failing_unicode_decode( data_bytes, 'utf-8' )))

            raise exceptions.FFMPEG_Exception(non_failing_unicode_decode( data_bytes, 'utf-8' ) )
        
    del process


    if not fallback:

        try:
        
            return generate_save_image_thumbnail(dest_jpg, dest_path, C.IMAGE_JPEG, thumbsize, THUMBNAIL_SCALE_DOWN_ONLY)
        
        finally:
            util.remove_file(dest_jpg)

    LOGGER.info("Could not extract existing thumbnail. Generating new thumbnail...")

    # just using the standard method for getting thumbnails with ffmpeg, don't really care that much what it spits out
    ff_args = [
        C.FFMPEG_PATH, '-y', '-v', 'error',
        '-i', str(source_path), 
        '-vf',  'thumbnail',
        '-frames:v', '1', 
        dest_jpg # ffmpeg really doesn't like .thumb as an extension
    ]

    process = subprocess.Popen( ff_args, bufsize = 10**5, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    
    LOGGER.info("Running FFMPEG with args: {}".format(ff_args))

    start_time = time.perf_counter()


    ( stdout, stderr ) = util.subprocess_communicate( process )
    
    data_bytes = stderr
    
    LOGGER.info("FFMPEG finished after {} seconds".format(time.perf_counter() - start_time))
    
    if len( data_bytes ) != 0:
        
        LOGGER.info("FFMPEG failed with exit: {}".format(non_failing_unicode_decode( data_bytes, 'utf-8' )))

        raise exceptions.FFMPEG_Exception(non_failing_unicode_decode( data_bytes, 'utf-8' ) )
        
    del process

    try:
        
        return generate_save_image_thumbnail(dest_jpg, dest_path, C.IMAGE_JPEG, thumbsize, THUMBNAIL_SCALE_DOWN_ONLY)
    
    finally:
        util.remove_file(dest_jpg)




def extract_subs(video_path, output_folder):

    util.create_directory(output_folder)

    # ffprobe arguments to get a csv output of the stream index, codec type and language
    # this will get us all the subtitle streams to extract 
    ffp_args = [ 
        C.FFPROBE_PATH,
        '-loglevel', 'error',
        '-select_streams', 's',
        '-show_entries', 'stream=index:stream=codec_type:stream_tags=language', 
        '-of', 'csv=p=0', 
        video_path
    ]

    process = subprocess.Popen( ffp_args, bufsize = 10**5, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    
    LOGGER.info("Extracting subtitles from: {}".format(video_path))
    LOGGER.info("Running FFPROBE with args: {}".format(ffp_args))
    start_time = time.perf_counter()

    ( stdout, stderr ) = util.subprocess_communicate( process )
    
    err_data_bytes = stderr
    std_data_bytes = stdout 

    LOGGER.info("FFPROBE finished after {} seconds".format(time.perf_counter() - start_time))

    if len( err_data_bytes ) != 0:
        
        LOGGER.info("FFPROBE failed with exit: {}".format(non_failing_unicode_decode( err_data_bytes, 'utf-8' )))

        raise exceptions.FFPROBE_Exception( non_failing_unicode_decode( err_data_bytes, 'utf-8' ) )
        
    
    del process


    ff_args = [ 
        C.FFMPEG_PATH, '-y', '-v', 'error',
        '-i', str(video_path),
    ]

    output_map = []

    sub_count = 0

    # split ffprobes output by line
    for line in std_data_bytes.split():

        try:
            # read the csv format 
            (index, stream, name) = line.split(b',')

        except ValueError:
            continue 

        if stream != b'subtitle':
            continue 
        
        sub_count += 1
        
        # decode the index and name
        index = util.parse_int(index.decode(errors="replace"), None)

        if index is None:
            continue 

        name  = name.decode('utf-8', errors="replace")

        # changed .vtt to .srt because kodi won't play subs unless they're srt 
        oname = os.path.join(output_folder, 'sub-{}.srt'.format(sub_count))

        # extend ffmpeg arguments 
        ff_args.extend(['-map', '0:{}'.format(index), oname ])

        # output mapping 
        output_map.append((index, oname, name))


    # no subs, ignore
    if sub_count == 0:
        LOGGER.info("Could not find any subtitles")
        return output_map

    LOGGER.info("Found {} subtitles".format(sub_count))
    
    process = subprocess.Popen( ff_args, bufsize = 10**5, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    
    LOGGER.info("Running FFMPEG with args: {}".format(ff_args))
    start_time = time.perf_counter()

    ( stdout, stderr ) = util.subprocess_communicate( process )
    
    err_data_bytes = stderr

    LOGGER.info("FFMPEG finished after {} seconds".format(time.perf_counter() - start_time))

    if len( err_data_bytes ) != 0:

        LOGGER.info("FFMPEG failed with exit: {}".format(non_failing_unicode_decode( err_data_bytes, 'utf-8' )))
        
        raise exceptions.FFMPEG_Exception( non_failing_unicode_decode( err_data_bytes, 'utf-8' ) )
        
    del process

    return output_map



def encode_video_standard(video_path : str, output_path : str):
    
    # https://superuser.com/questions/859010/what-ffmpeg-command-line-produces-video-more-compatible-across-all-devices
    
    ff_args = [
        C.FFMPEG_PATH, '-y', '-v', 'error',

        '-i', video_path, 

        '-c:v', 'libx264',
        
        '-c:a','aac', 
        '-ac' , '2',

        '-c:s', 'mov_text', # only sub format mp4 container supports 

        '-r', '23.976',
        '-g', '48',
        '-keyint_min', '48',

        '-profile:v', 'baseline', 
        '-level', '3.0', 
        '-pix_fmt', 'yuv420p',
        '-movflags', 'faststart',

        # '-threads', '1',         # reduce cpu but greatly increase time 

        '-crf', '28',

        '-f', 'mp4', 

        output_path
    ]

    util.create_directory_from_file_name(output_path)

    run_ffmpeg_standard(ff_args)




def split_encoded_video(video_path : str, output_directory : str, segment_size : int, ts_url, m3u8_url):
    """
    splits the given video and copies audio and video codecs removing subtitles

    ts_url and m3u8_url should contain {} to allow the use of str.format(x)
    """

    util.create_directory(output_directory)

    ff_args = [
        C.FFMPEG_PATH, '-y', '-v', 'error',

        '-i', video_path, 

        '-c', 'copy',

        '-sn', # remove subs 

        '-f', 'hls', 
        '-hls_time', str(segment_size),
        '-hls_playlist_type', 'vod', 
        '-hls_flags', 'independent_segments',
        '-hls_segment_type', 'mpegts',
                                        
        '-hls_segment_filename', os.path.join(output_directory, '%02d.ts'),

        '-master_pl_name', 'master.m3u8',

        os.path.join(output_directory, 'index.m3u8')
    ] 

    run_ffmpeg_standard(ff_args)

    # subs_vtt   = os.path.join(output_directory, "index_vtt.m3u8")
    index_m3u8 = os.path.join(output_directory, "index.m3u8")
    master     = os.path.join(output_directory, "master.m3u8")

    # subs_exist = os.path.isfile(subs_vtt)

    # if the video had subtitles, this will exist,
    # so rename them and fix the file 
    # lines    = []
    # if subs_exist:
        
    #     new_name = 0

    #     with util.read_write_file(subs_vtt, lines) as raw:

    #         for line in raw:

    #             if not line.endswith('.vtt\n'):
    #                 lines.append(line)
    #                 continue 

    #             o_name = os.path.join(output_directory, line.rstrip())
    #             n_name = "{0:02d}.vtt".format(new_name)

    #             util.rename_file(o_name, os.path.join(output_directory, n_name), replace=True)

    #             # creating a template file, this file will get formatted when the m3u8 is requested 
    #             # {URL}00.vtt -> http://...00.vtt
    #             lines.append("{URL}" + n_name + "\n")

    #             new_name += 1
    

    # apply required changes to the index.m3u8 file 
    lines = []
    with util.read_write_file(index_m3u8, lines) as raw:

        for line in raw:

            if not line.endswith('.ts\n'):
                lines.append(line)
                continue 

            lines.append("{ADD}" + ts_url.format(line.rstrip()) + "\n")


    # template for subtitles in m3u8 file
    # m3u8_sub_template = '#EXT-X-MEDIA:TYPE=SUBTITLES,URI="{}",GROUP-ID="{}",LANGUAGE="{}",NAME="{}",AUTOSELECT=YES\n'

    # apply required changes to master.m3u8
    lines *= 0 # lines = []
    with util.read_write_file(master, lines) as raw:

        for line in raw:
            
            # if subs_exist and line.startswith("#EXT-X-STREAM-INF:"):
            #     lines.append(m3u8_sub_template.format('{SUB_URL}index_vtt.m3u8', "subs", "en", "subtitle track 1"))
            #     lines.append(line.rstrip() + ',SUBTITLES="subs"\n')
            #     continue 

            if not line.endswith('.m3u8\n'):
                lines.append(line)
                continue
            
            lines.append("{ADD}" + m3u8_url.format(line.rstrip()) + "\n")
                
    result = [
        master,
        index_m3u8
    ]

    # if subs_exist:
        
    #     result.append(subs_vtt)

    return result 

