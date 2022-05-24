
import io
import warnings
import os.path 

from typing import Tuple

import numpy
from PIL import Image as PIL_Image
from PIL import ImageCms as PIL_Image_Cms

import image_size_reader as isr

from .. import exceptions
from .. import bn_logging
from .. import constants_ as C

LOGGER = bn_logging.get_logger(C.BNYAN_IMAGE_HANDLING[0], C.BNYAN_IMAGE_HANDLING[1])

try:

    import cv2

    # allows alpha channel
    CV_IMREAD_FLAGS_PNG = cv2.IMREAD_UNCHANGED
    # this preserves colour info but does EXIF reorientation and flipping
    CV_IMREAD_FLAGS_JPEG = cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR
    # this seems to allow weirdass tiffs to load as non greyscale,
    # although the LAB conversion 'whitepoint' or whatever can be wrong
    CV_IMREAD_FLAGS_WEIRD = CV_IMREAD_FLAGS_PNG

    CV_JPEG_THUMBNAIL_ENCODE_PARAMS = [cv2.IMWRITE_JPEG_QUALITY, 90]
    CV_PNG_THUMBNAIL_ENCODE_PARAMS = [cv2.IMWRITE_PNG_COMPRESSION, 9]

    OPENCV_OK = True

except ImportError:

    OPENCV_OK = False

    LOGGER.warning("Failed to import opencv-python (cv2), OPENCV_OK = False")



THUMBNAIL_SCALE_DOWN_ONLY   = 1
THUMBNAIL_SCALE_TO_FIT      = 2
THUMBNAIL_SCALE_TO_FILL     = 3

JPEG_QUALITY  = 90

PIL_ONLY_MIMETYPES = { C.IMAGE_GIF, C.IMAGE_ICON }
PIL_SRGB_PROFILE = PIL_Image_Cms.createProfile( 'sRGB' )

if not hasattr(PIL_Image, 'DecompressionBombError'):
    # super old versions don't have this, so let's just make a stub, wew

    class DBE_stub(Exception):
        pass

    PIL_Image.DecompressionBombError = DBE_stub

if not hasattr(PIL_Image, 'DecompressionBombWarning'):
    # super old versions don't have this, so let's just make a stub, wew

    class DBW_stub(Exception):
        pass

    PIL_Image.DecompressionBombWarning = DBW_stub

warnings.simplefilter('ignore', PIL_Image.DecompressionBombWarning)
warnings.simplefilter('ignore', PIL_Image.DecompressionBombError)


def get_resolution_numpy(numpy_image : numpy.array) -> Tuple[int, int]:

    """
    gets the width and height of a numpy image

    :param numpy_image: the numpy image -> numpy.array

    :return: the width and height -> tuple[int, int]
    """

    (image_height, image_width, depth) = numpy_image.shape

    return image_width, image_height


def get_ICC_profile_bytes(pil_image : PIL_Image.Image) -> bytes:

    """
    gets the iCC profile bytes from the given PIL image

    :raises exceptions.Data_Missing: data missing exception if the image does not contain an ICC profile

    :param pil_image: the image -> PIL.Image.Image

    :return: the ICC bytes -> bytes
    """

    if has_ICC_profile(pil_image):
        return pil_image.info['icc_profile']

    raise exceptions.Data_Missing("This image has no ICC profile")


def has_ICC_profile(pil_image : PIL_Image.Image) -> bool:

    """
    checks if the given PIL image has an ICC profile

    :param pil_image: the PIL image -> PIL.Image.Image

    :return: True if the image has an ICC profile, otherwise False
    """

    if 'icc_profile' in pil_image.info:

        icc_profile = pil_image.info['icc_profile']

        if isinstance(icc_profile, bytes) and len(icc_profile) > 0:
            return True

    return False


def make_clip_rect_fit(image_res : Tuple[int, int],
                       clip_rect : Tuple[int, int, int, int]):

    """
    makes the given clip rect fit the bounds of the given image size

    :param image_res: the image resolution -> tuple[int, int]

    :param clip_rect: the clip / crop area -> tuple[int, int, int, int]

    :return: a clip / crop area -> tuple[int, int, int, int]
    """

    (im_width, im_height) = image_res
    (x, y, clip_width, clip_height) = clip_rect

    x = max(0, x)
    y = max(0, y)

    clip_width = min(clip_width, im_width)
    clip_height = min(clip_height, im_height)

    if x + clip_width > im_width:
        x = im_width - clip_width

    if y + clip_height > im_height:
        y = im_height - clip_height

    return x, y, clip_width, clip_height


def clip_numpy_image(numpy_image: numpy.array, clip_rect):

    if len(numpy_image.shape) == 3:

        (im_height, im_width, depth) = numpy_image.shape

    else:

        (im_height, im_width) = numpy_image.shape

    (x, y, clip_width, clip_height) = make_clip_rect_fit((im_width, im_height), clip_rect)

    return numpy_image[y: y + clip_height, x: x + clip_width]


def clip_PIL_image(pil_image: PIL_Image.Image, clip_rect):
    (x, y, clip_width, clip_height) = make_clip_rect_fit(pil_image.size, clip_rect)

    return pil_image.crop(box=(x, y, x + clip_width, y + clip_height))


def rotate_EXIF_PIL_image(pil_image : PIL_Image.Image):

    if not pil_image.format == "JPEG" or not hasattr(pil_image, "_getexif"):
        return pil_image

    try:

        exif_dict = pil_image.getexif()

    except:

        return pil_image

    EXIF_ORIENTATION = 274

    if EXIF_ORIENTATION not in exif_dict:

        return pil_image

    orientation = exif_dict[EXIF_ORIENTATION]

    if orientation == 1:

        return pil_image  # normal

    if orientation == 2:

        # mirrored horizontal
        return pil_image.transpose(PIL_Image.FLIP_LEFT_RIGHT)

    if orientation == 3:

        # 180
        return pil_image.transpose(PIL_Image.ROTATE_180)

    if orientation == 4:

        # mirrored vertical
        return pil_image.transpose(PIL_Image.FLIP_TOP_BOTTOM)

    if orientation == 5:

        # seems like these 90 degree rotations are wrong,
        # but fliping them works for my posh example images, so I guess the PIL constants are odd
        # mirrored horizontal, then 90 CCW
        return pil_image.transpose(PIL_Image.FLIP_LEFT_RIGHT).transpose(PIL_Image.ROTATE_90)

    if orientation == 6:

        # 90 CW
        return pil_image.transpose(PIL_Image.ROTATE_270)

    if orientation == 7:

        # mirrored horizontal, then 90 CCW
        return pil_image.transpose(PIL_Image.FLIP_LEFT_RIGHT).transpose(PIL_Image.ROTATE_270)

    if orientation == 8:

        # 90 CCW
        return pil_image.transpose(PIL_Image.ROTATE_90)

    return pil_image


def PIL_image_has_alpha(pil_image: PIL_Image.Image):
    """ determines if a PIL image has alpha """

    return pil_image.mode in ('LA', 'RGBA') or \
          (pil_image.mode == 'P' and 'transparency' in pil_image.info)


def numpy_image_has_opaque_alpha_channel(numpy_image: numpy.array):
    """ determines if a numpy image has no transparent pixels """

    shape = numpy_image.shape

    if len(shape) == 2:
        return False

    if shape[2] != 4:
        return False

    # RGBA image
    # if the alpha channel is all opaque, there is no use storing that info in our pixel hash
    # opaque means 255
    alpha_channel = numpy_image[:, :, 3]

    return (alpha_channel == numpy.full((shape[0], shape[1]), 255, dtype='uint8')).all()


def normalise_PIL_image_to_RGB(pil_image: PIL_Image.Image):

    if PIL_image_has_alpha(pil_image):

        desired_mode = 'RGBA'

    else:

        desired_mode = 'RGB'

    if pil_image.mode != desired_mode:

        if pil_image.mode == 'LAB':

            pil_image = PIL_Image_Cms.profileToProfile(pil_image,
                                                       PIL_Image_Cms.createProfile('LAB'),
                                                       PIL_SRGB_PROFILE,
                                                       outputMode='RGB')

        else:

            pil_image = pil_image.convert(desired_mode)

    return pil_image


def normalise_ICC_profile_PIL_image_to_SRGB(pil_image : PIL_Image.Image):

    try:

        icc_profile_bytes = get_ICC_profile_bytes(pil_image)

    except exceptions.Data_Missing:

        return pil_image

    try:

        f = io.BytesIO(icc_profile_bytes)

        src_profile = PIL_Image_Cms.ImageCmsProfile(f)

        if pil_image.mode in ('L', 'LA'):

            # had a bunch of LA pngs that turned pure white on RGBA ICC conversion
            # but seem to work fine if keep colourspace the same for now
            # it is a mystery, I guess a PIL bug, but presumably L and LA are technically sRGB so it is still ok to this

            outputMode = pil_image.mode

        else:

            if PIL_image_has_alpha(pil_image):

                outputMode = 'RGBA'

            else:

                outputMode = 'RGB'

        pil_image = PIL_Image_Cms.profileToProfile(pil_image, src_profile, PIL_SRGB_PROFILE, outputMode=outputMode)

    except (PIL_Image_Cms.PyCMSError, OSError):

        # 'cannot build transform' and presumably some other fun errors
        # way more advanced than we can deal with, so we'll just no-op

        # OSError is due to a "OSError: cannot open profile from string" a user got
        # no idea, but that seems to be an ImageCms issue doing byte handling and ending up with an odd OSError?
        # or maybe somehow my PIL reader or bytesIO sending string for some reason?
        # in any case, nuke it for now

        pass

    pil_image = normalise_PIL_image_to_RGB(pil_image)

    return pil_image


def invert_numpy_image(numpy_image : numpy.array):

    numpy_image[:, :, 0:3] = 255 - numpy_image[:, :, 0:3]


def resize_numpy_image(numpy_image: numpy.array, target_resolution) -> numpy.array:

    (target_width, target_height) = target_resolution
    (image_width, image_height) = get_resolution_numpy(numpy_image)

    if target_width == image_width and target_height == target_width:

        return numpy_image

    elif target_width > image_height or target_height > image_width:

        interpolation = cv2.INTER_LANCZOS4

    else:

        interpolation = cv2.INTER_AREA

    return cv2.resize(numpy_image, (target_width, target_height), interpolation=interpolation)



def dequantize_PIL_image(pil_image :PIL_Image.Image) -> PIL_Image.Image:

    if has_ICC_profile(pil_image):

        try:

            pil_image = normalise_ICC_profile_PIL_image_to_SRGB(pil_image)

        except Exception as e:

            print('Failed to normalise image ICC profile.', e)

    pil_image = normalise_PIL_image_to_RGB(pil_image)

    return pil_image


def dequantize_numpy_image(numpy_image : numpy.array) -> numpy.array:

    # OpenCV loads images in BGR, and we want to normalise to RGB in general

    if numpy_image.dtype == 'uint16':
        numpy_image = numpy.array(numpy_image // 256, dtype='uint8')

    shape = numpy_image.shape

    if len(shape) == 2:

        # monochrome image

        convert = cv2.COLOR_GRAY2RGB

    else:

        (im_y, im_x, depth) = shape

        if depth == 4:

            convert = cv2.COLOR_BGRA2RGBA

        else:

            convert = cv2.COLOR_BGR2RGB

    numpy_image = cv2.cvtColor(numpy_image, convert)

    return numpy_image



def generate_PIL_image(path : str, dequantize : bool = True) -> PIL_Image.Image:

    """
    generates a PIL image from the given file path.

    :param path: the file path -> str

    :param dequantize: should the image be dequantanized -> bool

    :returns: a PIL image -> PIL.Image.Image
    """

    pil_image = raw_open_pil_image(path)

    if pil_image is None:
        raise Exception('The file at {} could not be rendered!'.format(path))

    rotate_EXIF_PIL_image(pil_image)

    if dequantize:
        # note this destroys animated gifs atm, it collapses down to one frame
        pil_image = dequantize_PIL_image(pil_image)

    return pil_image


def generate_numpy_image(path : str,
                         mime : int,
                         force_pil : bool = False) -> numpy.array:

    """
    generates a numpy image from the given file path.

    :param path: the file path -> str

    :param mime: the image mime type -> int

    :param force_pil: should PIL be used -> bool

    :return: a numpy image -> numpy.array
    """

    if not OPENCV_OK:
        force_pil = True

    pil_image = None

    if not force_pil:

        try:

            pil_image = raw_open_pil_image(path)

            try:

                # we must re-open the image if we want to decode it
                # after using this function
                pil_image.verify()

            except:

                raise Exception("unsupported file")

            # I and F are some sort of 32-bit monochrome or whatever,
            # doesn't seem to work in PIL well, with or without ICC
            if pil_image.mode not in ('I', 'F'):

                force_pil = pil_image.mode == "LAB" or has_ICC_profile(pil_image)

        except Exception as exxx:

            print(exxx)
            # pil had trouble, let's cross our fingers cv can do it
            pass

    if mime in PIL_ONLY_MIMETYPES or force_pil:

        if pil_image is not None:

            del pil_image

        pil_image = generate_PIL_image(path)

        numpy_image = generate_numpy_image_from_PIL_image(pil_image)
    else:

        if mime in (C.IMAGE_JPEG, C.IMAGE_TIFF):

            flags = CV_IMREAD_FLAGS_JPEG

        elif mime == C.IMAGE_PNG:

            flags = CV_IMREAD_FLAGS_PNG

        else:

            flags = CV_IMREAD_FLAGS_WEIRD

        numpy_image = cv2.imread(path, flags=flags)

        if numpy_image is None:  # doesn't support some random stuff

            pil_image = generate_PIL_image(path)

            numpy_image = generate_numpy_image_from_PIL_image(pil_image)

        else:

            numpy_image = dequantize_numpy_image(numpy_image)

    if numpy_image_has_opaque_alpha_channel(numpy_image):
        convert = cv2.COLOR_RGBA2RGB

        numpy_image = cv2.cvtColor(numpy_image, convert)

    return numpy_image


def generate_numpy_image_from_PIL_image(pil_image: PIL_Image.Image) -> numpy.array:

    (w, h) = pil_image.size

    try:

        s = pil_image.tobytes()

    except OSError as e:  # e.g. OSError: unrecognized data stream contents when reading image file

        raise exceptions.Unsupported_File_Exception(str(e))

    depth = len(s) // (w * h)

    return numpy.frombuffer(s, dtype='uint8').reshape((h, w, depth))
    # return numpy.fromstring(s, dtype='uint8').reshape((h, w, depth))




def generate_thumbnail_bytes_numpy(numpy_image : numpy.array) -> bytes:

    """
    generate thumbnail bytes from a numpy image.

    :param numpy_image: the image -> numpy.array

    :returns: the thumbnail bytes -> bytes
    """

    (im_height, im_width, depth) = numpy_image.shape

    if depth != 4:

        convert = cv2.COLOR_RGB2BGR

    elif numpy_image_has_opaque_alpha_channel(numpy_image):

        convert = cv2.COLOR_RGBA2BGR

    else:

        convert = cv2.COLOR_RGBA2BGRA

    numpy_image = cv2.cvtColor(numpy_image, convert)

    (im_height, im_width, depth) = numpy_image.shape

    if depth == 4:

        ext = '.png'

        params = CV_PNG_THUMBNAIL_ENCODE_PARAMS

    else:

        ext = '.jpg'

        params = CV_JPEG_THUMBNAIL_ENCODE_PARAMS

    (result_success, result_byte_array) = cv2.imencode(ext, numpy_image, params)

    if result_success:

        thumbnail_bytes = result_byte_array.tobytes()

        return thumbnail_bytes

    raise exceptions.Failed_To_Render_With_OpenCV_Exception("thumb failed to encode")


def generate_thumbnail_bytes_PIL(pil_image : PIL_Image.Image, mime : int) -> bytes:

    """
    generates thumbnail bytes from a PIL image.

    :param pil_image: the image -> PIL_Image.Image

    :param mime: the image mime type to write -> int

    :return: the thumbnail bytes -> bytes
    """

    f = io.BytesIO()

    if mime == C.IMAGE_PNG or pil_image.mode == 'RGBA':

        pil_image.save(f, 'PNG')

    else:

        pil_image.save(f, 'JPEG', quality=C.JPEG_QUALITY)

    f.seek(0)

    thumbnail_bytes = f.read()

    f.close()

    return thumbnail_bytes


def generate_thumbnail_bytes_from_static_image_path(path       : str,
                                                    target_res : Tuple[int, int],
                                                    mime       : int,
                                                    clip_rect  : Tuple[int, int, int, int] = None) -> bytes:

    """
    generates the raw bytes of a thumbnail image for the given image file.

    :param path: the path to the file -> str

    :param target_res: the target thumbnail size -> tuple[int, int]

    :param mime: the mime type to save the thumbnail -> int

    :param clip_rect: the clip rectangle -> tuple[int, int, int, int]

    :returns: the bytes of the thumbnail -> bytes

    """

    if OPENCV_OK:

        numpy_image = generate_numpy_image(path, mime)

        if clip_rect is not None:

            numpy_image = clip_numpy_image(numpy_image, clip_rect)

        thumbnail_numpy_image = resize_numpy_image(numpy_image, target_res)

        try:

            thumbnail_bytes = generate_thumbnail_bytes_numpy(thumbnail_numpy_image)

            return thumbnail_bytes

        except exceptions.Failed_To_Render_With_OpenCV_Exception:
            pass  # fallback to PIL

    pil_image = generate_PIL_image(path)

    if clip_rect is not None:

        pil_image = clip_PIL_image(pil_image, clip_rect)


    thumbnail_pil_image = pil_image.resize(target_res, PIL_Image.ANTIALIAS)

    thumbnail_bytes = generate_thumbnail_bytes_PIL(thumbnail_pil_image, mime)

    return thumbnail_bytes




def raw_open_pil_image(path : str) -> PIL_Image.Image:
    """
    opens the given image using PIL_Image

    :param path: the path to the file

    :returns: PIL_Image.Image
    """

    try:

        pil_image = PIL_Image.open(path)

    except Exception as e:

        print(e)

        raise Exception('Could not load the image--it was likely malformed!')

    return pil_image



def get_thumbnail_resolution_and_clip_region(image_resolution     : Tuple[int, int],
                                             bounding_dimensions  : Tuple[int, int],
                                             thumbnail_scale_type : int):
    """
    Gets the proper thumbnail size and clip region to generate a thumbnail.

    :param image_resolution: the width and height of the image -> tuple[int, int]

    :param bounding_dimensions: the max width and height the thumbnail can be -> tuple[int, int]

    :param thumbnail_scale_type: the scale type of the thumbnail -> int

    :returns: tuple[tuple[int, int], tuple[int, int]]
    """

    (im_width, im_height) = image_resolution
    (bounding_width, bounding_height) = bounding_dimensions

    if thumbnail_scale_type == THUMBNAIL_SCALE_DOWN_ONLY:

        if bounding_width >= im_width and bounding_height >= im_height:

            return None, (im_width, im_height)

    width_ratio  = im_width / bounding_width
    height_ratio = im_height / bounding_height

    thumbnail_width  = bounding_width
    thumbnail_height = bounding_height

    if thumbnail_scale_type in (THUMBNAIL_SCALE_DOWN_ONLY, THUMBNAIL_SCALE_TO_FIT):

        if width_ratio > height_ratio:

            thumbnail_height = im_height / width_ratio

        elif height_ratio > width_ratio:

            thumbnail_width = im_width / height_ratio

        return None, (max(int(thumbnail_width), 1),
                      max(int(thumbnail_height), 1))

    if thumbnail_scale_type != THUMBNAIL_SCALE_TO_FILL:

        return None, (max(int(thumbnail_width), 1),
                      max(int(thumbnail_height), 1))

    if width_ratio == height_ratio:

        # we have something that fits bounding region perfectly, no clip region required
        return None, (max(int(thumbnail_width), 1),
                      max(int(thumbnail_height), 1))

    clip_x = 0
    clip_y = 0
    clip_width = im_width
    clip_height = im_height

    if width_ratio > height_ratio:

        clip_width = max(int(im_width * height_ratio / width_ratio), 1)
        clip_x = (im_width - clip_width) // 2

    elif height_ratio > width_ratio:

        clip_height = max(int(im_height * width_ratio / height_ratio), 1)
        clip_y = (im_height - clip_height) // 2

    clip_rect = (clip_x, clip_y, clip_width, clip_height)

    return clip_rect, (max(int(thumbnail_width), 1),
                       max(int(thumbnail_height), 1))


def generate_save_image_thumbnail(source_path : str,
                                  dest_path : str,
                                  mime : int,
                                  thumbnail_size : Tuple[int, int],
                                  thumbnail_scale_type : int) -> bool:

    """
    generates and saves an image thumbnail

    :param source_path: the source path of the image -> str

    :param dest_path: the destination path for the thumbnail -> str

    :param mime: the mime type of the given image -> int

    :param thumbnail_size: the max size of the thumbnail -> tuple[int, int]

    :param thumbnail_scale_type: the scale type of the thumbnail -> int

    :returns: True if the thumbnail was created and saved, otherwise False
    """

    if not os.path.isfile(source_path):
        return False

    image_size = isr.get_image_size(source_path)

    LOGGER.info("Generating thumbnail for {}".format(source_path))

    if image_size == (0, 0):

        LOGGER.warning("Image-Size-Reader could not get image size for {}. Falling back to PIL/cv2".format(source_path))

        # we're gonna have to load the image and see if we can get the size that way
        if OPENCV_OK and mime not in PIL_ONLY_MIMETYPES:

            numpy_image = generate_numpy_image(source_path, mime)

            (width, height) = get_resolution_numpy(numpy_image)

            del numpy_image

        else:

            pil_image = generate_PIL_image(source_path, dequantize=False)

            (width, height) = pil_image.size

            del pil_image

        # assume the size cannot be gotten, we tried
        if width <= 0 or height <= 0:
            LOGGER.warning("Could not get image size using PIL/cv2 for {}. Thumbnail will not be made".format(source_path))
            return False

        image_size = (width, height)


    (clip_rect, target_resolution) = get_thumbnail_resolution_and_clip_region(image_size,
                                                                              thumbnail_size,
                                                                              thumbnail_scale_type)

    LOGGER.info("Determined image size: {}. Target thumb resoltuion: {} for {}".format(image_size, target_resolution, source_path))

    try:

        b = generate_thumbnail_bytes_from_static_image_path(source_path, target_resolution, mime, clip_rect)

        with open(dest_path, "wb") as writer:
            writer.write(b)

        return True

    except Exception as e:

        LOGGER.error("Could not generate thumbnail -> {}".format(e))

        return False
