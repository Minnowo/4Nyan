import time
import sys
import traceback
import os
import json
import threading
from typing import Union, Callable

try:
    import psutil

    PSUTIL_OK = True

except ImportError:

    PSUTIL_OK = False


from . import aNyanExceptions
from . import aNyanConstants
from . import aNyanPaths
from . import aNyanGlobals
from . import aNyanLogging as logging



def get_create_time():

    if PSUTIL_OK:
        try:

            me = psutil.Process()

            return me.create_time()

        except psutil.Error:

            pass

    return aNyanConstants.START_TIME


def getUptime():

    return time.time() - get_create_time()


def time_now() -> int:

    return int(time.time())


def time_now_float() -> float:

    return time.time()


def time_now_precise() -> float:

    return time.perf_counter()


def time_has_passed(timestamp: Union[float, int]) -> bool:

    if timestamp is None:

        return False

    return time_now() > timestamp


def time_has_passed_float(timestamp: Union[float, int]) -> bool:

    return time_now_float() > timestamp


def time_has_passed_precise(precise_timestamp: Union[float, int]) -> bool:

    return time_now_precise() > precise_timestamp


def time_until(timestamp: Union[float, int]) -> Union[float, int]:

    return timestamp - time_now()


def time_delta_since_time(timestamp):

    time_since = timestamp - time_now()

    result = min(time_since, 0)

    return -result


def Time_Delta_Until_Time(timestamp):

    time_remaining = timestamp - time_now()

    return max(time_remaining, 0)


def time_delta_until_time_float(timestamp):

    time_remaining = timestamp - time_now_float()

    return max(time_remaining, 0.0)


def time_delta_until_time_precise(t):

    time_remaining = t - time_now_precise()

    return max(time_remaining, 0.0)


def print_exception(e, do_wait=True):

    (etype, value, traceback) = sys.exc_info()

    print_exception_tuple(etype, value, traceback, do_wait=do_wait)


def print_exception_tuple(etype, value, trace, do_wait=True):

    if etype is None:

        etype = aNyanExceptions.UnknownException

    if etype == aNyanExceptions.Shutdown_Exception:

        return

    if value is None:

        value = "Unknown error"

    if trace is None:

        trace = "No error trace--here is the stack:" + os.linesep + "".join(traceback.format_stack())

    else:

        trace = "".join(traceback.format_exception(etype, value, trace))

    stack_list = traceback.format_stack()

    stack = "Stack:" + os.linesep + "".join(stack_list)

    message = str(etype.__name__) + ": " + str(value) + os.linesep + trace + os.linesep + stack

    logging.error(f"Exception:{os.linesep}{message}")

    if do_wait:

        time.sleep(1)


def record_running_start(db_path, instance):

    path = os.path.join(db_path, instance + "_running")

    record_string = ""

    if PSUTIL_OK:
        try:

            me = psutil.Process()

            record_string += str(me.pid)
            record_string += os.linesep
            record_string += str(me.create_time())

        except psutil.Error:

            return

    else:

        record_string += str(os.getpid())
        record_string += os.linesep
        record_string += str(aNyanConstants.START_TIME_PRECISE)

    aNyanPaths.make_sure_directory_exists(os.path.dirname(path))

    with open(path, "w", encoding="utf-8") as f:

        f.write(record_string)


def last_shutdown_was_bad(db_path, instance):

    path = os.path.join(db_path, instance + "_running")

    return os.path.exists(path)


def clean_running_file(db_path, instance):

    # just to be careful

    path = os.path.join(db_path, instance + "_running")

    try:
        os.remove(path)

    except:
        pass


def to_human_int(num):

    num = int(num)

    text = "{:,}".format(num)

    return text


def time_delta_to_pretty_time_delta(seconds, show_seconds=True):

    if seconds is None:

        return "per month"

    if seconds == 0:

        return "0 seconds"

    if seconds < 0:

        seconds = abs(seconds)

    if seconds >= 60:

        seconds = int(seconds)

        MINUTE = 60
        HOUR = 60 * MINUTE
        DAY = 24 * HOUR
        MONTH = 30 * DAY
        YEAR = 365 * DAY

        lines = [
            ("year", YEAR),
            ("month", MONTH),
            ("day", DAY),
            ("hour", HOUR),
            ("minute", MINUTE),
        ]

        if show_seconds:

            lines.append(("second", 1))

        result_components = []

        for (time_string, duration) in lines:

            time_quantity = seconds // duration

            seconds %= duration

            # little rounding thing if you get 364th day with 30 day months
            if time_string == "month" and time_quantity > 11:

                time_quantity = 11

            if time_quantity > 0:

                s = to_human_int(time_quantity) + " " + time_string

                if time_quantity > 1:

                    s += "s"

                result_components.append(s)

                if len(result_components) == 2:  # we now have 1 month 2 days

                    break

            else:

                # something like '1 year' -- in which case we do not care about the days and hours
                if len(result_components) > 0:

                    break

        return " ".join(result_components)

    if seconds > 1:

        if int(seconds) == seconds:

            return to_human_int(seconds) + " seconds"

        return "{:.1f} seconds".format(seconds)

    if seconds == 1:

        return "1 second"

    if seconds > 0.1:

        return "{} milliseconds".format(int(seconds * 1000))

    if seconds > 0.01:

        return "{:.1f} milliseconds".format(int(seconds * 1000))

    if seconds > 0.001:

        return "{:.2f} milliseconds".format(int(seconds * 1000))

    return "{} microseconds".format(int(seconds * 1000000))


def get_file_extension(path: str, do_not_include_dot: bool = False):

    index = path.rfind(".")

    if index == -1:
        return ""

    return path[index + do_not_include_dot :]


# TODO: just use a library for this, https://github.com/theskumar/python-dotenv
def get_envvars(env_file=".env", set_environ=False, ignore_not_found_error=False):

    env_vars = {}

    if not os.path.isfile(env_file):

        if not ignore_not_found_error:
            raise FileNotFoundError(f"Could not find env file: {env_file}")

        return env_vars

    with open(env_file) as reader:

        for line in reader:

            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if line[0:7].lower() == "export ":

                line = line[7:]

            try:
                (key, value) = line.split("=", 1)

            except ValueError as e:
                logging.debug(f"ValueErro while parsing .env file: {e}", stack_info=True)
                continue

            # removes quotes from string values
            if value[0] in ("'", '"') and value[-1] in ("'", '"') and value[0] == value[-1] and len(value) > 1:
                value = value[1:-1]

            if set_environ and key:
                os.environ[key] = value

            env_vars[key] = value

    return env_vars


class Call(object):
    def __init__(self, func: Callable, *args, **kwargs):

        self._label = None

        self._func = func
        self._args = args
        self._kwargs = kwargs

    def __call__(self):

        self._func(*self._args, **self._kwargs)

    def __repr__(self):

        label = self._GetLabel()

        return "Call: {}".format(label)

    def _GetLabel(self) -> str:

        if self._label is None:

            # this can actually cause an error with Qt objects that are dead or from the wrong thread, wew!
            label = "{}( {}, {} )".format(self._func, self._args, self._kwargs)

        else:

            label = self._label

        return label

    def GetLabel(self) -> str:

        return self._GetLabel()

    def SetLabel(self, label: str):

        self._label = label


class Job_Database(object):
    def __init__(self, job_type, synchronous, action, *args, **kwargs):

        self._type = job_type
        self._synchronous = synchronous
        self._action = action
        self._args = args
        self._kwargs = kwargs

        self._result_ready = threading.Event()

    def __str__(self):

        return "DB Job: {}".format(self.to_string())

    def _do_delayed_result_relief(self):

        pass

    def get_callable_tuple(self):

        return (self._action, self._args, self._kwargs)

    def get_type(self):

        return self._type

    def is_synchronous(self):

        return self._synchronous

    def put_result(self, result):

        self._result = result

        self._result_ready.set()

    def to_string(self):

        return "{} {}".format(self._type, self._action)

    def get_result(self):

        time.sleep(0.00001)  # this one neat trick can save hassle on superquick jobs as event.wait can be laggy

        while True:

            result_was_ready = self._result_ready.wait(2)

            if result_was_ready:

                break

            if aNyanGlobals.model_shutdown:

                raise aNyanExceptions.Shutdown_Exception("Application quit before db could serve result!")

            self._do_delayed_result_relief()

        if isinstance(self._result, Exception):

            e = self._result

            raise e

        else:

            return self._result
