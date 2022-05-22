

from base64 import decode
import os
from re import sub 
import subprocess


FFMPEG = "..\\..\\backend\\bnyan\\bin\\ffmpeg.exe"



def subprocess_communicate( process: subprocess.Popen, timeout : int = 10) -> tuple:
    """ returns process.communicate with the given timeout """

    while True:
        
        try:
            
            return process.communicate( timeout = timeout )
            
        except subprocess.TimeoutExpired:
            
            pass    


def generate_thumbnail(source_path, dest_path):

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    # # looking for png/jpeg video streams from embeded thumbnails 
    # # if we cannot find them we will make our own thumbnail 
    # ff_args = [
    #     FFMPEG, '-y', '-v', 'error',
    #     '-i', str(source_path),
    #     '-c', 'copy',
    #     '-map', '0:v',
    #     '-map', '-0:V',
    #     '-vframes', '1',
    #     dest_path
    # ]

    # process = subprocess.Popen( ff_args, bufsize = 10**5, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    
    # ( stdout, stderr ) = subprocess_communicate( process )
    
    # data_bytes = stderr
    
    # if len( data_bytes ) != 0:
        
    #     fallback = data_bytes == b'Output file #0 does not contain any stream\r\n'

    #     if not fallback:

    #         raise Exception(data_bytes.decode('utf-8'))
    #         # raise exceptions.FFMPEG_Exception(decode( data_bytes, 'utf-8' ) )
        
    # del process


    # if not fallback:
    #     return

    # just using the standard method for getting thumbnails with ffmpeg, don't really care that much what it spits out
    ff_args = [
        FFMPEG, '-y', '-v', 'error',
        '-i', str(source_path), 
        '-vf',  'thumbnail',
        '-frames:v', '1', 
        # '-f', 'singlejpeg',
        dest_path + ".jpg"
    ]

    process = subprocess.Popen( ff_args, bufsize = 10**5, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    
    ( stdout, stderr ) = subprocess_communicate( process )
    
    data_bytes = stderr
    
    if len( data_bytes ) != 0:
        
        raise Exception(data_bytes.decode('utf-8'))
            # raise exceptions.FFMPEG_Exception(decode( data_bytes, 'utf-8' ) )
        
    del process

    return 

path = "D:\\0_VIDEO\\SELF\\WrestlingTimerGuide.mp4"
output_dir = ".\\output\\uwu2.png"

generate_thumbnail(path, output_dir)

