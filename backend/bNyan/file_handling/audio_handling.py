

from re import search


# very big thanks to https://github.com/hydrusnetwork/hydrus
# 
# the 'parse_ffmpeg_audio' function was taken directly from hydrus.Core.HydrusAudioHandling

def parse_ffmpeg_audio( lines ):
    
    # the ^\sStream is to exclude the 'title' line, when it exists, includes the string 'Audio: ', ha ha
    lines_audio = [ l for l in lines if search( r'^\s*Stream', l ) is not None and 'Audio: ' in l ]

    if not lines_audio:
        return (False, None)
        
    line = lines_audio[0]
    
    match = search( r"(?<=Audio\:\s).+?(?=,)", line )

    if not match:
        return ( True, 'unknown' )

    return ( True, match.group() )
