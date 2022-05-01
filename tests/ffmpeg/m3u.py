



import subprocess

import os 
fmpeg = "..\\..\\backend\\bnyan\\bin\\ffmpeg.exe"


def subprocess_communicate( process: subprocess.Popen, timeout : int = 10) -> tuple:
    """ returns process.communicate with the given timeout """

    while True:
        
        try:
            
            return process.communicate( timeout = timeout )
            
        except subprocess.TimeoutExpired:
            
            pass    



def split_video(video_path : str, output_directory : str, segment_size : int = 6) -> str:
    """ process the given video creating an m3u8 files ready for hls, returns the m3u8 path"""

    ff_args = [fmpeg, '-y', '-v', 'error',
                '-i', video_path, 
                '-c:v', 'libx264',
                '-c:a','aac', '-ac', '2',
                '-preset','veryfast',
                '-f', 'hls', '-hls_time', str(segment_size),
                '-hls_playlist_type','event', 
                '-hls_list_size', '0',
                os.path.join(output_directory, '0')]


    process = subprocess.Popen( ff_args, bufsize = 10**5, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    
    ( stdout, stderr ) = subprocess_communicate( process )
    
    data_bytes = stderr
    
    if len( data_bytes ) != 0:
        
        # raise Exception( non_failing_unicode_decode( data_bytes, 'utf-8' ) )
        raise Exception( data_bytes )
        
    
    del process
    
    return os.path.join(output_directory, '0.m3u8')


video_path   = "D:\\uwu.mp4"
output_dir   = "output"
segment_size = 6

split_video(video_path,output_dir,segment_size)