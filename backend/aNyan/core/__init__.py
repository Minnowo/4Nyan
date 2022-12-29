# set the START_TIME constant as soon as possible
# should be set at process start, only used if psutil is not found
from . import aNyanConstants
from . import aNyanThreading
from . import aNyanController
from . import aNyanLogging
from . import aNyanGlobals
from . import aNyanData

import shlex


def useful_thread_callback(controller, nyah):

    print("thread callback invoked", controller, nyah)

    print(aNyanGlobals.debug_value)


def main():
    aNyanGlobals.daemon_report_mode = True
    aNyanLogging.setup_logger("./logs.log")

    try:
        controller = aNyanController.Nyan_Controller("./db")
        controller.record_running_start()
        controller.init_model()

        # thred = aNyanThreading.Daemon_Worker(controller, "test-daemon-thread", useful_thread_callback, period=10)
        thred = aNyanThreading.Threadcall_To_Thread(controller, "threadcall")
        thred.start()

        while True:

            i = input().lower()

            if i == "exit":
                return

            elif i.startswith("job"):

                args = shlex.split(i)

                if len(args) < 3:
                    continue

                thred.put(useful_thread_callback, args[1], args[2])

            elif i.startswith("shutdown"):

                aNyanGlobals.debug_value = True

    except Exception as e:

        aNyanData.print_exception(e)

    finally:

        thred.shutdown()
        controller.shutdown_model()
        controller.shutdown_view()
        controller.clean_running_file()
