

import subprocess

import os 
FFMPEG = "..\\..\\backend\\bnyan\\bin\\ffmpeg.exe"
FFPROBE = "..\\..\\backend\\bnyan\\bin\\ffprobe.exe"
SHAKA_PAKCER = "..\\..\\backend\\bnyan\\bin\\shaka_packager.exe"

def subprocess_communicate( process: subprocess.Popen, timeout : int = 10) -> tuple:
    """ returns process.communicate with the given timeout """

    while True:
        
        try:
            
            return process.communicate( timeout = timeout )
            
        except subprocess.TimeoutExpired:
            
            pass    

def extract_subs(video_path, output_folder):

    # ffprobe arguments to get a csv output of the stream index, codec type and language
    # this will get us all the subtitle streams to extract 
    ffp_args = [ 
        FFPROBE,
        '-loglevel', 'error',
        '-select_streams', 's',
        '-show_entries', 'stream=index:stream=codec_type:stream_tags=language', 
        '-of', 'csv=p=0', 
        video_path
    ]

    process = subprocess.Popen( ffp_args, bufsize = 10**5, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    
    ( stdout, stderr ) = subprocess_communicate( process )
    
    err_data_bytes = stderr
    std_data_bytes = stdout 

    if len( err_data_bytes ) != 0:
        
        # raise Exception( non_failing_unicode_decode( data_bytes, 'utf-8' ) )
        raise Exception( err_data_bytes )
        
    
    del process


    ff_args = [ 
        FFMPEG, '-y', '-v', 'error',
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
        index = int(index.decode())
        name  = name.decode('utf-8', errors="replace")
        oname = os.path.join(output_folder, 'sub-{}.vtt'.format(sub_count))

        # extend ffmpeg arguments 
        ff_args.extend(['-map', '0:{}'.format(index), oname ])

        # output mapping 
        output_map.append((index, oname, name))


    # no subs, ignore
    if sub_count == 0:

        return output_map

    process = subprocess.Popen( ff_args, bufsize = 10**5, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    
    ( stdout, stderr ) = subprocess_communicate( process )
    
    std_data_bytes = stdout 

    if len( err_data_bytes ) != 0:
        
        # raise Exception( non_failing_unicode_decode( data_bytes, 'utf-8' ) )
        raise Exception( err_data_bytes )
        
    del process

    return output_map



def prep_video(video_path, output):

    ff_args = [ FFMPEG, '-y', '-v', 'error',
        '-i', str(video_path),

        '-c:a','aac', '-ac', '2',
        '-c:v', 'libx264',
        '-x264opts', 'keyint=24:min-keyint=24:no-scenecut',
        output 
    ]

    process = subprocess.Popen( ff_args, bufsize = 10**5, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    
    ( stdout, stderr ) = subprocess_communicate( process )
    
    data_bytes = stderr
    
    if len( data_bytes ) != 0:
        
        # raise Exception( non_failing_unicode_decode( data_bytes, 'utf-8' ) )
        raise Exception( data_bytes )
        
    
    del process


def dash(video_path):

    s_args = [ 
        SHAKA_PAKCER,
        'input={},stream=audio,output=audio.mp4'.format(video_path),
        'input={},stream=video,output=video.mp4'.format(video_path),
        '--profile', 'on-demand',
        '--min_buffer_time', '3',
        '--segment_duration', '3'
        '--mpd_output', 'sample-manifest.mpd',
    ]

    process = subprocess.Popen( s_args, bufsize = 10**5, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    
    ( stdout, stderr ) = subprocess_communicate( process )
    
    if stdout != b'Packaging completed successfully.\r\n':
        # raise Exception( non_failing_unicode_decode( data_bytes, 'utf-8' ) )
        raise Exception( stderr )

    del process

path = "D:\\0_VIDEO\\MUSIC_VIDEOS\\test\\uwu.mp4"
outp = ".\\test.mp4"
# prep_video(path, outp)
# dash(outp)


path = ".\\video-test\\video1.mkv" 
extract_subs(path, 'video-test')