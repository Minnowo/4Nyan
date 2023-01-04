import os
import tempfile
import threading
from typing import Union

from . import aNyanData
from . import aNyanPaths
from . import aNyanConstants
from . import aNyanLogging as logging

TEMP_PATH_LOCK = threading.Lock()
IN_USE_TEMP_PATHS = set()


def Get_Temp_Path(suffix: str = "", dir: str = None) -> tuple[int, str]:

    return tempfile.mkstemp(suffix=suffix, prefix=aNyanConstants.BRAND, dir=dir)


def get_current_temp_dir() -> str:

    return tempfile.gettempdir()


def get_temp_dir(dir: str = None) -> Union[str, bytes]:

    return tempfile.mkdtemp(prefix=aNyanConstants.BRAND, dir=dir)


def clean_up_temp_path(os_file_handle, temp_path: str):

    try:

        os.close(os_file_handle)

    except OSError:

        try:

            os.close(os_file_handle)

        except OSError:

            logging.warning("Could not close the temporary file " + temp_path)

            return

    try:

        os.remove(temp_path)

    except OSError:

        with TEMP_PATH_LOCK:

            IN_USE_TEMP_PATHS.add((aNyanData.time_now(), temp_path))


def clean_up_old_temp_paths():

    with TEMP_PATH_LOCK:

        data = list(IN_USE_TEMP_PATHS)

        for row in data:

            (time_failed, temp_path) = row

            if aNyanData.time_has_passed(time_failed + 60):

                try:

                    os.remove(temp_path)

                    IN_USE_TEMP_PATHS.discard(row)

                except OSError:

                    if aNyanData.time_has_passed(time_failed + 600):

                        IN_USE_TEMP_PATHS.discard(row)


def set_env_temp_dir(path: str):

    if os.path.exists(path) and not os.path.isdir(path):

        raise Exception('The given temp directory, "{}", does not seem to be a directory!'.format(path))

    try:

        aNyanPaths.make_sure_directory_exists(path)

    except Exception as e:

        raise Exception("Could not create the temp dir: {}".format(e))

    if not aNyanPaths.directory_is_writeable(path):

        raise Exception('The given temp directory, "{}", does not seem to be writeable-to!'.format(path))

    for tmp_name in ("TMPDIR", "TEMP", "TMP"):

        if tmp_name in os.environ:

            os.environ[tmp_name] = path

    tempfile.tempdir = path
