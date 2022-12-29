import threading
import weakref
import logging

from . import aNyanData
from . import aNyanExceptions
from . import aNyanGlobals


class Nyan_PubSub(object):
    def __init__(self, controller, valid_callable):

        self._controller = controller
        self._valid_callable = valid_callable

        self._doing_work = False

        self._pubsubs = []

        self._pub_event = threading.Event()

        self._lock = threading.Lock()

        self._topics_to_objects: dict[str, weakref.WeakSet] = {}
        self._topics_to_method_names: dict[str, set] = {}

    def _get_callable_tuples(self, topic: str):

        # this now does the obj as well so we have a strong direct ref to it throughout procesing

        callable_tuples = []

        if topic in self._topics_to_objects:

            try:

                objects = self._topics_to_objects[topic]

                for obj in objects:

                    if obj is None or not self._valid_callable(obj):

                        continue

                    method_names = self._topics_to_method_names[topic]

                    for method_name in method_names:

                        if hasattr(obj, method_name):

                            callable = getattr(obj, method_name)

                            callable_tuples.append((obj, callable))

            except:

                pass

        return callable_tuples

    def doing_work(self):

        return self._doing_work

    def process(self):

        # only do one list of callables at a time
        # we don't want to map a topic to its callables until the previous topic's callables have been fully executed
        # e.g. when we start a message with a pubsub, it'll take a while (in independant thread-time) for Qt to create
        # the dialog and hence map the new callable to the topic. this was leading to messages not being updated
        # because the (short) processing thread finished and entirely pubsubbed before Qt had a chance to boot the
        # message.

        self._doing_work = True

        try:

            callable_tuples = []

            with self._lock:

                if len(self._pubsubs) == 0:

                    return

                pubsubs = self._pubsubs

                self._pubsubs = []

            for (topic, args, kwargs) in pubsubs:

                try:

                    # do all this _outside_ the lock, lol

                    callable_tuples = self._get_callable_tuples(topic)

                    # don't want to report the showtext we just send here!
                    not_a_report = topic != "message"

                    if aNyanGlobals.pubsub_report_mode and not_a_report:

                        logging.info((topic, args, kwargs, callable_tuples))

                    if False and aNyanGlobals.profile_mode and not_a_report:
                        pass
                        # summary = "Profiling pubsub: {}".format(topic)

                        # for (obj, callable) in callable_tuples:

                        #     try:

                        #         aNyanData.profile(
                        #             summary,
                        #             "callable( *args, **kwargs )",
                        #             globals(),
                        #             locals(),
                        #             min_duration_ms=aNyanGlobals.pubsub_profile_min_job_time_ms,
                        #         )

                        #     except aNyanExceptions.Shutdown_Exception:

                        #         return False

                    else:

                        for (obj, callable) in callable_tuples:

                            try:

                                callable(*args, **kwargs)

                            except aNyanExceptions.Shutdown_Exception:

                                return False

                except Exception as e:

                    aNyanData.print_exception(e)

        finally:

            self._doing_work = False

    def pub(self, topic: str, *args, **kwargs):

        with self._lock:

            self._pubsubs.append((topic, args, kwargs))

        self._pub_event.set()

    def pubimmediate(self, topic: str, *args, **kwargs):

        with self._lock:

            callable_tuples = self._get_callable_tuples(topic)

        for (obj, callable) in callable_tuples:

            callable(*args, **kwargs)

    def sub(self, object: object, method_name: str, topic: str):

        with self._lock:

            if topic not in self._topics_to_objects:
                self._topics_to_objects[topic] = weakref.WeakSet()

            if topic not in self._topics_to_method_names:
                self._topics_to_method_names[topic] = set()

            self._topics_to_objects[topic].add(object)
            self._topics_to_method_names[topic].add(method_name)

    def wait_on_pub(self):

        self._pub_event.wait(3)

        self._pub_event.clear()

    def wake(self):

        self._pub_event.set()

    def work_to_do(self):

        with self._lock:

            return len(self._pubsubs) > 0
