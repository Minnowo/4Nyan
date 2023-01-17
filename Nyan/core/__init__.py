from . import (
    NyanController,
    NyanDB,
    NyanData,
    NyanExceptions,
    NyanGlobals,
    NyanLogging,
    NyanPaths,
    NyanPubSub,
    NyanTemp,
    NyanThreading,
    NyanConstants,
)

import logging
import threading
import shlex
import sqlite3


def useful_thread_callback(controller, nyah):

    print("thread callback invoked", controller, nyah)

    print(NyanGlobals.debug_value)


def threading_test(controller=None):

    try:

        if controller is None:
            controller = NyanController.Nyan_Controller("./db")
            controller.record_running_start()
            controller.init_model()

        # thred = aNyanThreading.Daemon_Worker(controller, "test-daemon-thread", useful_thread_callback, period=10)
        thred = NyanThreading.Thread_Call_To_Thread(controller, "threadcall")
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

                NyanGlobals.debug_value = True

    except Exception as e:

        NyanData.print_exception(e)

    finally:

        thred.shutdown()
        controller.shutdown_model()
        controller.shutdown_view()
        controller.clean_running_file()


def test_pubsub(controller=None):
    class subscriber:
        def on_notification(self, *args, **kwargs):

            print("Got notification:", *args, "on thread:", threading.current_thread().getName())

    thread = NyanThreading.Thread_Call_To_Thread(None, "pubsub_process_call_to_thread")
    pubsub = NyanPubSub.Nyan_PubSub()

    global is_shutting_down

    is_shutting_down = False

    def pubsub_daemon(pubsub: NyanPubSub.Nyan_PubSub):

        global is_shutting_down

        while not is_shutting_down:

            if pubsub.work_to_do():

                try:
                    pubsub.process()

                except Exception as e:
                    logging.error(e, stack_info=True)

            else:
                pubsub.wait_on_pub()

    # put the pubsub daemon callback into the thread
    # this will overtake run until is_shutting_down is set
    thread.put(pubsub_daemon, pubsub)

    # make some dummy subscribers
    subs = [subscriber() for i in range(3)]

    topic = "TOPIC"

    # sub up
    for sub in subs:
        pubsub.sub(sub, "on_notification", topic)

    # this will send a notification instantely
    pubsub.pubimmediately_here("TOPIC", "here is a notification")

    try:
        thread.start()
        while True:

            i = input().lower()

            if i == "exit":
                return

            if i.startswith("pub "):

                args = shlex.split(i)

                if len(args) < 2:
                    continue

                pubsub.pub(topic, args[1:])

            elif i.startswith("pubi "):

                args = shlex.split(i)

                if len(args) < 2:
                    continue

                pubsub.pubimmediately_here(topic, args[1:])

    except Exception as e:
        logging.error(e)

    finally:

        is_shutting_down = True
        pubsub.wake()  # optional to make it shutdown faster
        thread.shutdown()


def main():
    NyanGlobals.daemon_report_mode = True
    NyanLogging.setup_logger(NyanConstants.BRAND, "./logs.log")

    # controller = aNyanController.Nyan_Controller("./db")
    # controller.record_running_start()
    # controller.init_model()

    test_pubsub()
