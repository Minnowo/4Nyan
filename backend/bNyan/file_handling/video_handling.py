
from distutils import extension
from .. import exceptions
from .. import util 

from .. import constants_ as C

from ..constants_ import mime_types as MT 

from ..text import non_failing_unicode_decode


from .audio_handling import parse_ffmpeg_audio

from re import search, match
 
import subprocess
import os.path 

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

    vinfo = {
        "mime" : get_video_mime_from_ffmpeg_lines( lines ),

        "has_video" : has_video,
        "video_format" : video_format,

        "has_audio" : has_audio,
        "audio_format" : audio_format,

        "width" : width ,
        "height" : height 
    }

    return vinfo




# def split_video(video_path : str, output_directory : str, segment_size : int = 6) -> str:
#     """ process the given video creating an m3u8 files ready for hls, returns the m3u8 path"""

#     ff_args = [C.FFMPEG_PATH, '-y', '-v', 'error',
#                 '-i', video_path, 
#                 '-c:v', 'libx264',
#                 '-c:a','aac', '-ac', '2',
#                 '-preset','veryfast',
#                 '-f', 'hls', '-hls_time', str(segment_size),
#                 '-hls_playlist_type','event', # unsure what i want this to be https://www.rfc-editor.org/rfc/rfc8216#section-4.3.1.1
#                                               # ctrl + f EXT-X-PLAYLIST-TYPE
#                 '-hls_list_size', '0',
#                 os.path.join(output_directory, '0')]


#     process = subprocess.Popen( ff_args, bufsize = 10**5, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    
#     ( stdout, stderr ) = util.subprocess_communicate( process )
    
#     data_bytes = stderr
    
#     if len( data_bytes ) != 0:
        
#         raise exceptions.FFMPEG_Exception( non_failing_unicode_decode( data_bytes, 'utf-8' ) )
        
    
#     del process
    
#     return os.path.join(output_directory, '0')



def split_video(video_path : str, output_directory : str, segment_size : int, ts_url : str, vtt_url : str, m3u8_url : str) -> str:
    """ 
    process the given video creating an m3u8 files ready for hls, returns the m3u8 path 
    
    video_path : the source video path -> str
    output_directory : the output directory of all the files (assumes empty) -> str
    segment_size : the size of each ts file in seconds -> int
    ts_url : the url for ts files, it should include a format template so ts_url.format(ts_filename) adds the path in the correct spot -> str
    vtt_url : the url for vtt files, it should include a format template so vtt_url.format(vtt_filename) adds the path in the correct spot-> str
    m3u8_url : the url for m3u8 files, it should include a format template so m3u8_url.format(m3u8_filename) adds the path in the correct spot -> str
    """

    ff_args = [C.FFMPEG_PATH, '-y', '-v', 'error',

                '-i', video_path, 

                '-c:v', 'libx264',
                '-c:a','aac', 
                '-c:s', 'webvtt',
                '-ac', '2',

                '-keyint_min', '48',

                # '-preset','superfast',   # this seems to break the segment size
                # '-threads', '1',         # reduce cpu but greatly increase time 
                '-crf', '34',              # unsure what I want for this, likely will be based on file size 

                '-f', 'hls', 
                '-hls_time', str(segment_size),
                '-hls_playlist_type','vod', 
                '-hls_flags', 'independent_segments',
                '-hls_segment_type', 'mpegts',
                                              
                '-hls_segment_filename', os.path.join(output_directory, '%02d.ts'),

                '-master_pl_name', 'master.m3u8',

                 os.path.join(output_directory, 'index.m3u8')]


    process = subprocess.Popen( ff_args, bufsize = 10**5, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    
    ( stdout, stderr ) = util.subprocess_communicate( process )
    
    data_bytes = stderr
    
    if len( data_bytes ) != 0:
        
        raise exceptions.FFMPEG_Exception( non_failing_unicode_decode( data_bytes, 'utf-8' ) )
        
    del process

    subs_vtt   = os.path.join(output_directory, "index_vtt.m3u8")
    index_m3u8 = os.path.join(output_directory, "index.m3u8")
    master     = os.path.join(output_directory, "master.m3u8")

    subs_exist = os.path.isfile(subs_vtt)

    # if the video had subtitles, this will exist,
    # so rename them and fix the file 
    if subs_exist:
        
        lines    = []
        new_name = 0
        with open(subs_vtt, "r") as reader:

            for line in reader:

                if not line.endswith('.vtt\n'):
                    lines.append(line)
                    continue 

                o_name = os.path.join(output_directory, line.rstrip())
                n_name = "{0:02d}.vtt".format(new_name)

                util.rename_file(o_name, os.path.join(output_directory, n_name), replace=True)

                # assume good input, it's the callers fault if this cannot happen
                lines.append(vtt_url.format(n_name) + "\n")

                new_name += 1

        with open(subs_vtt, "w") as writer:

            writer.writelines(lines)
    

    # apply required changes to the index.m3u8 file 
    lines = []
    with open(index_m3u8, "r") as reader:

        for line in reader:

            if not line.endswith('.ts\n'):
                lines.append(line)
                continue 

            lines.append(ts_url.format(line.rstrip()) + "\n")
            
    with open(index_m3u8, "w") as writer:

        writer.writelines(lines)

    # template for subtitles in m3u8 file
    m3u8_sub_template = '#EXT-X-MEDIA:TYPE=SUBTITLES,URI="{}",GROUP-ID="{}",LANGUAGE="{}",NAME="{}",AUTOSELECT=YES\n'

    # apply required changes to master.m3u8
    lines = []
    with open(master, "r") as reader:

        for line in reader:
            
            if subs_exist and line.startswith("#EXT-X-STREAM-INF:"):
                lines.append(m3u8_sub_template.format(m3u8_url.format('index_vtt.m3u8'), "subs", "en", "subtitle track 1"))
                lines.append(line.rstrip() + ',SUBTITLES="subs"\n')
                continue 

            if not line.endswith('.m3u8\n'):
                lines.append(line)
                continue
            
            lines.append(m3u8_url.format(line.rstrip()) + "\n")
                
    with open(master, "w") as writer:

        writer.writelines(lines)


    result = [
        master,
        index_m3u8
        ]

    if subs_exist:
        
        result.append(subs_vtt)

    return result 

