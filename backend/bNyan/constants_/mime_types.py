



# enums here (idk if the numbers are random, 
# i took this from https://github.com/hydrusnetwork/hydrus/blob/b927c938914a7c71a7fa693e7e640039b324e971/hydrus/core/HydrusConstants.py#L496)

APPLICATION_UNKNOWN = 0


# this range should be big enough for each category that they won't ever need to change
IMAGE_MIME_RANGE = (100, 199) 
VIDEO_MIME_RANGE = (200, 299)
AUDIO_MIME_RANGE = (300, 399)

# image 
IMAGE_JPEG = 100
IMAGE_PNG  = 101
IMAGE_GIF  = 102
IMAGE_BMP  = 103
IMAGE_ICON = 104
IMAGE_WEBP = 105
IMAGE_TIFF = 106

# video
VIDEO_FLV   = 201
VIDEO_MP4   = 202
VIDEO_WMV   = 203
VIDEO_MKV   = 204
VIDEO_WEBM  = 205
VIDEO_MPEG  = 206
VIDEO_MOV   = 207
VIDEO_AVI   = 208
VIDEO_OGV   = 209

# audio
AUDIO_MP3       = 301
AUDIO_OGG       = 302
AUDIO_FLAC      = 303
AUDIO_WMA       = 304
AUDIO_M4A       = 305
AUDIO_TRUEAUDIO = 306
AUDIO_WAVE      = 307
AUDIO_MKV       = 308
AUDIO_MP4       = 309

APPLICATION_PDF = 60

UNDETERMINED_VIDEO = 50
UNDETERMINED_VIDEO_MP4 = 51
UNDETERMINED_VIDEO_WM = 52

IMAGE_MIMES = sorted([ IMAGE_JPEG, IMAGE_PNG, IMAGE_GIF , IMAGE_BMP, IMAGE_ICON, IMAGE_WEBP, IMAGE_TIFF ])
AUDIO_MIMES = sorted([ AUDIO_MP3 , AUDIO_OGG, AUDIO_FLAC, AUDIO_WMA, AUDIO_M4A , AUDIO_WAVE, AUDIO_MKV , AUDIO_MP4 ])
VIDEO_MIMES = sorted([ VIDEO_FLV , VIDEO_MP4, VIDEO_WMV , VIDEO_MKV, VIDEO_WEBM, VIDEO_MPEG, VIDEO_MOV , VIDEO_AVI, VIDEO_OGV ])
