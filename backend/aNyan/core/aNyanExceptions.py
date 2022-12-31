import collections.abc
import os


class bNyan_Exception(Exception):
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


class UnknownException(bNyan_Exception):
    """unknown exception"""


class Unsupported_File_Exception(bNyan_Exception):
    """unsupported file"""


class Zero_Size_File_Exception(Unsupported_File_Exception):
    """file has 0 length"""


class Damaged_Or_Unusual_File_Exception(Unsupported_File_Exception):
    """the file is damaged"""


class FFMPEG_Required_Exception(bNyan_Exception):
    """
    ffmpeg is required to parse the data
    Called when checking file types, it means the file must be downloaded to determine the type
    """


class Shutdown_Exception(bNyan_Exception):
    """shutting down"""


class FFMPEG_Exception(bNyan_Exception):
    """raised when ffmpeg throws an error"""


class FFPROBE_Exception(bNyan_Exception):
    """raised when ffprobe throws an error"""


class Data_Missing(bNyan_Exception):
    """raised when there is no data"""


class Failed_To_Render_With_OpenCV_Exception(bNyan_Exception):
    """raised when openCV cannot render stuff"""


class DB_Access_Exception(bNyan_Exception):
    """database error"""
