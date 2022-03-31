import os 

from reg import INVALID_PATH_CHAR, DIGIT

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
