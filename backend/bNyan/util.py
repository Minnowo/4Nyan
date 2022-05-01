import os 
import hashlib
import subprocess
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

    except OSError:
        return False 



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
    


def get_temp_file_in_path(path : str):
    """ returns a path in the given folder that does not exist """

    filename = os.path.join(path, os.urandom(32).hex())

    while os.path.isfile(filename):
        filename = os.path.join(path, os.urandom(32).hex())

    return filename




def subprocess_communicate( process: subprocess.Popen, timeout : int = 10) -> tuple:
    """ returns process.communicate with the given timeout """

    while True:
        
        try:
            
            return process.communicate( timeout = timeout )
            
        except subprocess.TimeoutExpired:
            
            pass    

