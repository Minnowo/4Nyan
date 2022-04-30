



# enums here (idk if the numbers are random, 
# i took this from https://github.com/hydrusnetwork/hydrus/blob/b927c938914a7c71a7fa693e7e640039b324e971/hydrus/core/HydrusConstants.py#L496)

APPLICATION_UNKNOWN = 0

# image 
IMAGE_JPEG = 1
IMAGE_PNG = 2
IMAGE_GIF = 3
IMAGE_BMP = 4
IMAGE_ICON = 7
IMAGE_WEBP = 33
IMAGE_TIFF = 34

# audio
AUDIO_MP3 = 13
AUDIO_OGG = 15
AUDIO_FLAC = 16
AUDIO_WMA = 17
AUDIO_M4A = 36
AUDIO_TRUEAUDIO = 39
AUDIO_WAVE = 46
AUDIO_MKV = 48
AUDIO_MP4 = 49

# video
VIDEO_FLV = 9
VIDEO_MP4 = 14
VIDEO_WMV = 18
VIDEO_MKV = 20
VIDEO_WEBM = 21
VIDEO_MPEG = 25
VIDEO_MOV = 26
VIDEO_AVI = 27
VIDEO_OGV = 47

APPLICATION_PDF = 48

UNDETERMINED_VIDEO = 50
UNDETERMINED_VIDEO_MP4 = 51
UNDETERMINED_VIDEO_WM = 52

IMAGE_MIMES = sorted([ IMAGE_JPEG, IMAGE_PNG, IMAGE_GIF , IMAGE_BMP, IMAGE_ICON, IMAGE_WEBP, IMAGE_TIFF ])
AUDIO_MIMES = sorted([ AUDIO_MP3 , AUDIO_OGG, AUDIO_FLAC, AUDIO_WMA, AUDIO_M4A , AUDIO_WAVE, AUDIO_MKV, AUDIO_MP4 ])
VIDEO_MIMES = sorted([ VIDEO_FLV , VIDEO_MP4, VIDEO_WMV , VIDEO_MKV, VIDEO_WEBM, VIDEO_MPEG, VIDEO_MOV, VIDEO_AVI, VIDEO_OGV ])
