import os 
import hashlib
from .reg import INVALID_PATH_CHAR, DIGIT

def natural_sort_key(s, _nsre=DIGIT):
    """    Provides a natural sort when used with sort(list, key=natural_sort_key) or sorted(list, key=natural_sort_key) """
    return [int(text) if text.isdigit() else text.lower() for text in _nsre.split(s)]


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


def remove_file(path : str) -> bool:
    """    Deletes the given file.    """
    try:
        os.unlink(path)
    except OSError:
        pass
    return not os.path.exists(path)


def remove_directory(path : str) -> bool:
    """    Deletes the given directory.    """
    try:
        os.rmdir(path)
    except OSError:
        pass
    return not os.path.isdir(path)


def parse_int(value : str, default = None):
    """    Convert 'value' to int    """

    if not value:
        return default
    
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def iter_file(file, chunk_size : int = 262144): # 256kb 
    """    takes a file handle and yields it in blocks    """

    next_block = file.read(chunk_size)
    
    while len( next_block ) > 0:
        
        yield next_block
        
        next_block = file.read(chunk_size)
        
  
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
    