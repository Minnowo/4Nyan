import os
import shutil
import stat

from . import NyanData
from . import NyanConstants
from . import NyanGlobals
from . import NyanLogging as logging


def make_sure_directory_exists(path: str):

    os.makedirs(path, exist_ok=True)


def file_is_writeable(path: str):

    return os.access(path, os.W_OK)


def directory_is_writeable(path: str):

    while not os.path.exists(path):

        try:

            path = os.path.dirname(path)

        except:

            return False

    return os.access(path, os.W_OK | os.X_OK)


def delete_path(path):

    if NyanGlobals.file_report_mode:

        logging.info("Deleting {}".format(path))

    if not os.path.exists(path):
        return

    try_to_make_file_writeable(path)

    try:

        if os.path.isdir(path):

            shutil.rmtree(path)

        else:

            os.remove(path)

    except Exception as e:

        # file in use by another process
        if "Error 32" in str(e):

            logging.warning("Trying to delete " + path + " failed because it was in use by another process.")

        else:

            logging.error("Trying to delete " + path + " caused the following error:")
            NyanData.print_exception(e)


def try_to_make_file_writeable(path: str):

    if not os.path.exists(path):

        return

    if file_is_writeable(path):

        return

    try:

        stat_result = os.stat(path)

        current_bits = stat_result.st_mode

        if NyanGlobals.PLATFORM_WINDOWS:

            # this is actually the same value as S_IWUSR, but let's not try to second guess ourselves
            desired_bits = stat.S_IREAD | stat.S_IWRITE

        else:

            # this only does what we want if we own the file, but only owners can non-sudo change permission anyway
            desired_bits = stat.S_IWUSR

        if not (desired_bits & current_bits) == desired_bits:

            os.chmod(path, current_bits | desired_bits)

    except Exception as e:

        logging.error('Wanted to add user write permission to "{}", but had an error: {}'.format(path, str(e)))
