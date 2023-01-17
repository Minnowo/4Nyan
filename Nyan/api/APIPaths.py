import re
import os

from . import APIExceptions

from ..core import NyanLogging as logging


HAS_VALID_CHARACTERS = re.compile(r"^[a-zA-Z0-9\-\_\.\(\)\[\]\,]+", flags=re.IGNORECASE)

CONTAINS_TRICKY_PATHING = re.compile(r"[\\\/]\.\.[\\\/]")


def die_if_bad_path(path: str):

    if not HAS_VALID_CHARACTERS.match(path):

        raise APIExceptions.API_400_BAD_REQUEST_EXCEPTION


def get_valid_path_or_die(path: tuple[str]):

    die_if_bad_path(path[-1])

    path = os.path.join(*path)

    logging.debug(f"checking path: {path}")

    if not os.path.isfile(path):

        raise APIExceptions.API_400_BAD_REQUEST_EXCEPTION

    return path
