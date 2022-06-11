import os 
import hashlib
import subprocess
import shutil
from contextlib import contextmanager

from . import constants_
from .models import File
from .reg import INVALID_PATH_CHAR, DIGIT

def natural_sort_key(s, _nsre=DIGIT):
    """    Provides a natural sort when used with sort(list, key=natural_sort_key) or sorted(list, key=natural_sort_key) """
    return [int(text) if text.isdigit() else text.lower() for text in _nsre.split(s)]


def get_static_route_from_mime(mime : int):
    """ returns the static route where a file should be accessed via the static url from the given mime type """
    
    if in_range(mime, constants_.mime_types.IMAGE_MIME_RANGE):
        return constants_.STATIC_IMAGE_ROUTE

    if in_range(mime, constants_.mime_types.VIDEO_MIME_RANGE):
        return constants_.STATIC_VIDEO_ROUTE

    if in_range(mime, constants_.mime_types.AUDIO_MIME_RANGE):
        return constants_.STATIC_AUDIO_ROUTE

    # if mime in MT.IMAGE_MIMES:
    #     return constants_.STATIC_IMAGE_ROUTE

    # if mime in MT.VIDEO_MIMES:
    #     return constants_.STATIC_VIDEO_ROUTE

    # if mime in  MT.AUDIO_MIMES:
    #     return constants_.STATIC_VIDEO_ROUTE

    return "None" 

def get_static_path_from_mime(mime : int):
    """ returns the static path where a file should be stored based of the given mime type """

    if in_range(mime, constants_.mime_types.IMAGE_MIME_RANGE):
        return constants_.STATIC_IMAGE_PATH

    if in_range(mime, constants_.mime_types.VIDEO_MIME_RANGE):
        return constants_.STATIC_VIDEO_PATH
        
    if in_range(mime, constants_.mime_types.AUDIO_MIME_RANGE):
        return constants_.STATIC_AUDIO_PATH

    # if mime in MT.IMAGE_MIMES:
    #     return constants_.STATIC_IMAGE_PATH

    # if mime in MT.VIDEO_MIMES:
    #     return constants_.STATIC_VIDEO_PATH

    # if mime in  MT.AUDIO_MIMES:
    #     return constants_.STATIC_AUDIO_PATH

    return constants_.STATIC_TEMP_PATH


def strip_invalid_path(path : str) -> str:
    """    Removes invalid path characters    """
    return INVALID_PATH_CHAR.sub("", path)



def create_directory_from_file_name(path : str) -> bool:
    """    Creates a directory from the file path.    """
    return create_directory(os.path.dirname(path))



def create_directory(path : str) -> bool:
    """    Creates the given directory.    """
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass
    return os.path.isdir(path)


def remove_file_db(file : File):
    """ Deletes the given file """

    sha256_hex = file.hash.hex()

    file_ext = constants_.MIME_EXT_LOOKUP.get(file.mime, "")

    base = os.path.join(get_static_path_from_mime(file.mime), sha256_hex[0:2], sha256_hex)

    filename = base + file_ext

    if in_range(file.mime, constants_.mime_types.IMAGE_MIME_RANGE):
        return remove_file(filename)
 
    return remove_file(filename) and \
           remove_directory(base) and \
           remove_directory(os.path.join(constants_.STATIC_M3U8_PATH, sha256_hex[0:2], sha256_hex))


def remove_file(path : str) -> bool:
    """    Deletes the given file.    """
    try:
        os.unlink(path)
        return True 
    except OSError:
        pass
    return False 



def remove_directory(path : str) -> bool:
    """    Deletes the given directory.    """
    try:
        shutil.rmtree(path, ignore_errors=False)
        return True 
    except OSError:
        pass 
    return False 



def parse_int(value : str, default = None):
    """    Convert 'value' to int    """

    if not value:
        return default
    
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def rename_file(filename : str, new_filename : str, *, replace : bool = False) -> bool:
    """ 
    Renames the given file with the new filename 

    replace : bool - should any existing files be deleted/replaced by the given file

    returns True if the file was renamed otherwise False 

    TODO: make this temp delete the replace file so that if the rename fails after it can be restored 
    """

    if not new_filename:
        return False 

    try:
        if os.path.isfile(new_filename):

            if not replace:
                return False 
            
            if not remove_file(new_filename):
                return False 

        os.rename(filename, new_filename)
        return True 

    except OSError as e:
        return False 


def combine_dict(a, b):
    """Recursively combine the contents of 'b' into 'a'"""

    for key, value in b.items():

        if key in a and isinstance(value, dict) and isinstance(a[key], dict):
            combine_dict(a[key], value)
            
        else:
            a[key] = value

    return a


def iter_file(file, chunk_size : int = 262144): # 256kb 
    """    takes a file handle and yields it in blocks    """

    next_block = file.read(chunk_size)
    
    while len( next_block ) > 0:
        
        yield next_block
        
        next_block = file.read(chunk_size)



async def iter_file_async(file, chunk_size : int = 262144): # 256kb 
    """    takes a file handle and yields it in blocks    """

    next_block = await file.read(chunk_size)
    
    while len( next_block ) > 0:
        
        yield next_block
        
        next_block = await file.read(chunk_size)
              

  
def get_extra_file_hash(path : str) -> tuple:
    """    returns a tuple of hashes as bytes in the order ( md5, sha1, sha512 )    """  
    h_md5    = hashlib.md5()
    h_sha1   = hashlib.sha1()
    h_sha512 = hashlib.sha512()
    
    with open(path, 'rb') as file:
        
        for block in iter_file(file):
            
            h_md5.update( block )
            h_sha1.update( block )
            h_sha512.update( block )
            
    return ( h_md5.digest(), 
             h_sha1.digest(), 
             h_sha512.digest() )
    


def get_temp_file_in_path(path : str, ext='.tmp'):
    """ returns a path in the given folder that does not exist """

    filename = os.path.join(path, os.urandom(32).hex() + ext)

    while os.path.isfile(filename):
        filename = os.path.join(path, os.urandom(32).hex() + ext)

    return filename




def subprocess_communicate( process: subprocess.Popen, timeout : int = 10) -> tuple:
    """ returns process.communicate with the given timeout """

    while True:
        
        try:
            
            return process.communicate( timeout = timeout )
            
        except subprocess.TimeoutExpired:
            
            pass    



def in_range(item, range : tuple):

    """ 
    checks if the given number is in the range of the given min and max (inclusive) 
    
    item : the number to check

    range : the min and max range as a tuple
    """

    (min, max) = range 

    return item >= min and item <= max 



@contextmanager
def read_write_file(path, lines, is_bytes = False):
    """ 
    reads a file and yields the file object,

    then overwrites the file with the given lines array after the 'with' clause 

    this is used to read a file one line at a time, and if the line matches a matches a condition append a modified string to the lines array, otherwise just append the line 
    """
    
    with open(path, 'r' + 'b' * is_bytes) as file:

        yield file 

    with open(path, 'w' + 'b' * is_bytes) as writer:

        writer.writelines(lines)



@contextmanager
def tempfile(mode='w', ext='.mp4', temp_folder=constants_.STATIC_TEMP_PATH, replace_into=None, open_=True):

    try:
        filename = get_temp_file_in_path(temp_folder, ext)
        
        if open_:

            with open(filename, mode) as handle:

                yield handle

        else:

            yield filename

    finally:

        if not replace_into:

            remove_file(filename) 
        
        else:

            rename_file(filename, replace_into, replace=True)

