


#################################### Image 
from backend.bNyan.constants_.mime_types import UNDETERMINED_MP4


IMAGE_GIF_HEADERS = ( 
    ( 0, b"GIF87a" ), 
    ( 0, b"GIF89a" ),
)

IMAGE_TIFF_HEADERS = ( 
    ( 0, b"II*\x00" ), # little endian
    ( 0, b"MM\x00*" ), # big endian 
) 

IMAGE_ICO_HEADERS = ( 
    ( 0, b"\x00\x00\x01\x00" ),
    ( 0, b"\x00\x00\x02\x00" )
)

IMAGE_BMP_HEADER               = ( ( 0, b"BM" ), )
IMAGE_WEBP_HEADER              = ( ( 8, b"WEBP" ), )
IMAGE_PNG_HEADER               = ( ( 0, b"\x89PNG\r\n\x1a\n"), )
IMAGE_JPEG_HEADERS             = ( ( 0, b"\xFF\xD8\xFF" ), )
IMAGE_UNDETERMINED_PNG_HEADERS = ( ( 0, b"\x89PNG" ), ) # apng or png 
####################################  
#################################### Video 


UNDETERMINED_VIDEO_MP4_HEADERS = ( 
    ( 4, b"ftypmp4" ), 
    ( 4, b"ftypisom" ), 
    ( 4, b"ftypM4V" ), 
    ( 4, b"ftypMSNV" ), 
    ( 4, b"ftypavc1" ), 
    ( 4, b"ftypFACE" ), 
    ( 4, b"ftypdash" ) 
)
    
VIDEO_FLV_HEADER  = ( ( 0, b"FLV" ), )
VIDEO_MOV_HEADERS = ( ( 4, b"ftypqt" ), )
VIDEO_AVI_HEADERS = ( ( 8, b"AVI " ), )
VIDEO_MKV_HEADERS = ( ( 0, b"\x1aE\xdf\xa3"), )

UNDETERMINED_VIDEO_WM_HEADERS  = ( ( 0, b'\x30\x26\xB2\x75\x8E\x66\xCF\x11\xA6\xD9\x00\xAA\x00\x62\xCE\x6C' ), )

####################################  
#################################### Audio

AUDIO_FLAC_HEADERS = ( ( 0, b"fLaC" ), )
AUDIO_WAVE_HEADERS = ( 
    ( 0, b"RIFF" ), 
    ( 8, b"WAVE" ),
)

####################################  
#################################### Other 

PDF_HEADER = ( ( 0, b"%PDF" ), )

ALL_DETERMINED_FILE_HEADERS = list(

    IMAGE_JPEG_HEADERS + IMAGE_PNG_HEADER +
    IMAGE_WEBP_HEADER  + IMAGE_GIF_HEADERS +
    UNDETERMINED_VIDEO_MP4_HEADERS + VIDEO_MKV_HEADERS + 
    VIDEO_MOV_HEADERS + IMAGE_TIFF_HEADERS +
    PDF_HEADER + 
    AUDIO_FLAC_HEADERS + AUDIO_WAVE_HEADERS + 
    VIDEO_AVI_HEADERS  + IMAGE_ICO_HEADERS  + 
    IMAGE_BMP_HEADER   + VIDEO_FLV_HEADER +   
    UNDETERMINED_VIDEO_WM_HEADERS
)


