import collections.abc
import os


class Nyan_Exception(Exception):
    def __str__(self):

        if isinstance(self.args, collections.abc.Iterable):

            s = []

            for arg in self.args:

                try:
                    s.append(str(arg))

                except:
                    s.append(repr(arg))

        else:
            s = [repr(self.args)]

        return os.linesep.join(s)


class UnknownException(Nyan_Exception):
    """Unknown exception"""


class Unsupported_File_Exception(Nyan_Exception):
    """Unsupported file"""


class Zero_Size_File_Exception(Unsupported_File_Exception):
    """File has 0 length"""


class Damaged_Or_Unusual_File_Exception(Unsupported_File_Exception):
    """The file is damaged"""


class FFMPEG_Required_Exception(Nyan_Exception):
    """
    FFMPEG is required to perform a certain action

    Raised when checking file types, it means the file must be downloaded to determine the type
    """


class Shutdown_Exception(Nyan_Exception):
    """Raised to signal shutting down"""


class FFMPEG_Exception(Nyan_Exception):
    """Raised when ffmpeg throws an error"""


class FFPROBE_Exception(Nyan_Exception):
    """Raised when ffprobe throws an error"""


class Data_Missing(Nyan_Exception):
    """Raised when there is no data"""


class Failed_To_Render_With_OpenCV_Exception(Nyan_Exception):
    """Raised when openCV cannot render stuff"""


class DB_Access_Exception(Nyan_Exception):
    """
    Database access error

    Raised when the database is borken, malformed or cannot be accessed for some reason
    """


class DB_Credentials_Exception(Nyan_Exception):
    """
    Database credential error

    Raised when bad credentials are used to access the database
    """


class Cache_Exception(Nyan_Exception):
    """
    Cache Base Exception
    """

class Cache_Lookup_Exception(Nyan_Exception):
    """
    Cache Lookup Exception

    Raised when a cache lookup has no data
    """

class Cache_Expired_Exception(Nyan_Exception):
    """
    Cache Expired Exception

    Raised when trying to access expired data from a cache
    """
